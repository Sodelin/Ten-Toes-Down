"""Download a pinned, free Hugging Face model with verified atomic writes.

Standard library only. No account, token, paid endpoint, or inference service.
Run explicitly to download; importing this module does not access the network.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time
import urllib.parse
import urllib.request


DEFAULT_REPO = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
DEFAULT_REVISION = "5ecdb67327fd37bb2e042aab12ff7391903235d3"
EXTENSIONS = {".json", ".txt", ".safetensors"}
CHUNK = 1024 * 1024
PRINT_LOCK = threading.Lock()


def progress(message: str) -> None:
    with PRINT_LOCK:
        print(message, flush=True)


def within(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes output directory: {path}") from exc
    if resolved == root:
        raise ValueError("Expected a file beneath the output directory.")
    return resolved


def destination(root: Path, name: str) -> Path:
    # Strict component syntax rejects traversal, Windows drive/UNC paths,
    # alternate data streams, and platform-specific path separators.
    parts = name.split("/")
    if any(
        part in {"", ".", ".."}
        or re.fullmatch(r"[A-Za-z0-9_.-]+", part) is None
        for part in parts
    ):
        raise ValueError(f"Unsafe repository filename: {name!r}")
    return within(root, root.joinpath(*parts))


def request(url: str):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "Ten-Toes-Down-Audio/1.0"}),
        timeout=60,
    )


def inspect_file(path: Path, item: dict) -> dict:
    size = path.stat().st_size
    expected_size = item.get("size")
    if expected_size is not None and size != expected_size:
        raise ValueError(f"Size mismatch for {item['name']}: {size} != {expected_size}")
    sha256 = hashlib.sha256()
    git_sha1 = None
    if item["algorithm"] == "git-blob-sha1":
        git_sha1 = hashlib.sha1(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as handle:
        while block := handle.read(CHUNK):
            sha256.update(block)
            if git_sha1 is not None:
                git_sha1.update(block)
    actual = sha256.hexdigest() if git_sha1 is None else git_sha1.hexdigest()
    if actual != item["expected"]:
        raise ValueError(f"{item['algorithm']} mismatch for {item['name']}")
    return {"bytes": size, "sha256": sha256.hexdigest()}


def get_items(repo: str, revision: str, root: Path) -> tuple[str, list[dict]]:
    api_url = f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true"
    with request(api_url) as response:
        payload = response.read(16 * 1024 * 1024 + 1)
    if len(payload) > 16 * 1024 * 1024:
        raise ValueError("Unexpectedly large repository metadata response.")
    metadata = json.loads(payload)
    if metadata.get("sha") != revision:
        raise ValueError(f"Repository revision differs from requested pin: {metadata.get('sha')}")
    items = []
    seen = set()
    for sibling in metadata.get("siblings", []):
        name = sibling.get("rfilename")
        if not isinstance(name, str) or Path(name).suffix not in EXTENSIONS:
            continue
        dest = destination(root, name)
        # Casefold also prevents Windows case-insensitive output collisions.
        identity = str(dest).casefold()
        if identity in seen or name.casefold() == "download.manifest.json":
            raise ValueError(f"Colliding repository filename: {name}")
        seen.add(identity)
        lfs = sibling.get("lfs")
        if isinstance(lfs, dict):
            algorithm, expected = "sha256", lfs.get("sha256")
            size = lfs.get("size", sibling.get("size"))
            valid = isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected)
        else:
            algorithm, expected = "git-blob-sha1", sibling.get("blobId")
            size = sibling.get("size")
            valid = isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{40}", expected)
        if not valid:
            raise ValueError(f"No verifiable upstream hash for {name}")
        if size is not None and (not isinstance(size, int) or size < 0):
            raise ValueError(f"Invalid upstream size for {name}")
        encoded_name = urllib.parse.quote(name, safe="/")
        items.append({
            "name": name,
            "url": f"https://huggingface.co/{repo}/resolve/{revision}/{encoded_name}?download=true",
            "algorithm": algorithm,
            "expected": expected,
            "size": size,
        })
    if not items or not any(item["name"].endswith(".safetensors") for item in items):
        raise ValueError("The pinned repository contains no selected model weights.")
    return api_url, sorted(items, key=lambda item: item["name"])


def download_one(root: Path, item: dict, stopped: threading.Event) -> dict:
    if stopped.is_set():
        raise RuntimeError("Download cancelled after another file failed.")
    dest = destination(root, item["name"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest = within(root, dest)
    if dest.is_file():
        try:
            details = inspect_file(dest, item)
        except ValueError:
            progress(f"Replacing unverified file: {item['name']}")
        else:
            progress(f"Verified existing: {item['name']}")
            return {"path": item["name"], "url": item["url"], **details,
                    "verification": {"algorithm": item["algorithm"], "expected": item["expected"]},
                    "reused": True}
    progress(f"Downloading: {item['name']}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=dest.parent, prefix=dest.name + ".", suffix=".part", delete=False
        ) as output:
            temporary = within(root, Path(output.name))
            received = 0
            last_report = time.monotonic()
            with request(item["url"]) as response:
                while block := response.read(CHUNK):
                    if stopped.is_set():
                        raise RuntimeError("Download cancelled after another file failed.")
                    output.write(block)
                    received += len(block)
                    if item["size"] is not None and received > item["size"]:
                        raise ValueError(f"Download exceeds expected size: {item['name']}")
                    if time.monotonic() - last_report >= 10:
                        total = f" / {item['size'] / 1048576:.1f}" if item["size"] is not None else ""
                        progress(f"{item['name']}: {received / 1048576:.1f}{total} MiB")
                        last_report = time.monotonic()
            output.flush()
            os.fsync(output.fileno())
        details = inspect_file(temporary, item)
        # Recheck after network/file work before replacing an existing target.
        dest = destination(root, item["name"])
        temporary.replace(dest)
        temporary = None
        progress(f"Verified download: {item['name']} ({details['bytes'] / 1048576:.1f} MiB)")
        return {"path": item["name"], "url": item["url"], **details,
                "verification": {"algorithm": item["algorithm"], "expected": item["expected"]},
                "reused": False}
    except Exception:
        stopped.set()
        raise
    finally:
        if temporary is not None and temporary.exists():
            within(root, temporary).unlink()


def save_manifest(root: Path, manifest: dict) -> None:
    target = within(root, root / "download.manifest.json")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=root,
            prefix="download.manifest.", suffix=".part", delete=False,
        ) as handle:
            temporary = within(root, Path(handle.name))
            json.dump(manifest, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(within(root, target))
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            within(root, temporary).unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="Directory for the pinned model snapshot.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--revision", default=DEFAULT_REVISION, help="Exact 40-character repository commit.")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("--repo must be a Hugging Face owner/repository name.")
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        parser.error("--revision must be an exact lowercase 40-character commit SHA.")
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=True)
    api_url, items = get_items(args.repo, args.revision, root)
    progress(f"Pinned {args.repo}@{args.revision}; {len(items)} selected files; two download workers.")
    stopped = threading.Event()
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(download_one, root, item, stopped) for item in items]
        try:
            for future in as_completed(futures):
                results.append(future.result())
        except BaseException:
            stopped.set()
            for future in futures:
                future.cancel()
            raise
    save_manifest(root, {
        "repo": args.repo,
        "revision": args.revision,
        "metadata_url": api_url,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_extensions": sorted(EXTENSIONS),
        "files": sorted(results, key=lambda result: result["path"]),
    })
    progress(f"Complete: {len(results)} verified files. Manifest: {root / 'download.manifest.json'}")


if __name__ == "__main__":
    main()
