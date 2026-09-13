"""Package one fully published audiobook book and publish its M4B release asset."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import wave

import imageio_ffmpeg

from publish import REPO, URL, git, run, save, sha, sync_package, write_index
from state import locked_progress, publication_lock
from worker import resolve_config, verify_result

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))
from verify_verbatim import verify_verbatim


def ffconcat_quote(path: Path) -> str:
    """Quote an absolute path for ffmpeg's concat demuxer."""
    return "'" + path.resolve().as_posix().replace("'", "'\\''") + "'"


def ffmetadata_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("=", "\\=").replace(";", "\\;").replace("#", "\\#").replace("\n", "\\n")


def run_ffmpeg(arguments: list[str], okay: tuple[int, ...] = (0,)):
    return run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-nostdin", *arguments], okay=okay)


def safe_job(package: Path, relative_value: str) -> Path:
    relative = Path(relative_value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe chapter path: {relative}")
    result = (package / relative).resolve()
    result.relative_to(package)
    return result


def source_inventory(folder: Path, source_commit: str) -> dict[str, str]:
    required = ("source.json", "source-check.json", "source-excerpt.md", "script.json", "audio.manifest.json", "audio.wav")
    paths = {name: folder / name for name in required}
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing chapter input {name}: {path}")
    source = json.loads(paths["source.json"].read_text(encoding="utf-8-sig"))
    verification = verify_verbatim(paths["script.json"])
    if source.get("commit") != source_commit or verification.get("commit") != source_commit:
        raise ValueError(f"Chapter source commit differs from progress.json: {folder.name}")
    if not str(verification.get("status", "")).startswith("PASS"):
        raise ValueError(f"Chapter source verification is not passing: {folder.name}")
    if verification.get("excerpt_sha256") != sha(paths["source-excerpt.md"]):
        raise ValueError(f"Chapter source excerpt changed: {folder.name}")
    if verification.get("script_sha256") != sha(paths["script.json"]):
        raise ValueError(f"Chapter script changed after source verification: {folder.name}")
    return {name: sha(path) for name, path in paths.items()}


def validate_book(progress: dict, package: Path, book_number: int) -> tuple[list[dict], dict[str, dict[str, str]]]:
    chapters = sorted(
        (copy.deepcopy(row) for row in progress.get("chapters", []) if row.get("book") == book_number),
        key=lambda row: row["chapter"],
    )
    if not chapters:
        raise ValueError(f"Book {book_number} is absent from progress.json.")
    expected_numbers = list(range(1, len(chapters) + 1))
    if [row["chapter"] for row in chapters] != expected_numbers:
        raise ValueError("Book chapter numbers must be complete and sequential.")
    release_tag = f"audiobook-book-{book_number:02}"
    inventory = {}
    for chapter in chapters:
        if chapter.get("status") != "published":
            raise ValueError(f"Chapter is not published: {chapter['id']}")
        publication = chapter.get("publication")
        if not isinstance(publication, dict) or not publication.get("audio_url") or not publication.get("audio_sha256"):
            raise ValueError(f"Chapter publication metadata is incomplete: {chapter['id']}")
        if chapter.get("release_tag") != release_tag:
            raise ValueError(f"Chapter release tag differs within the book: {chapter['id']}")
        folder = safe_job(package, chapter["path"])
        verify_result(folder / "script.json", folder / "audio", chapter["words"])
        report = json.loads((folder / "audio.manifest.json").read_text(encoding="utf-8-sig"))
        if report.get("samples_at_full_scale") != 0 or report.get("warnings"):
            raise ValueError(f"Chapter master has unresolved audio-integrity findings: {chapter['id']}")
        if not str(report.get("verbatim_source_check", {}).get("status", "")).startswith("PASS"):
            raise ValueError(f"Chapter renderer source check is not passing: {chapter['id']}")
        if sha(folder / "audio.mp3") != publication["audio_sha256"]:
            raise ValueError(f"Published chapter MP3 differs from publication metadata: {chapter['id']}")
        if abs(float(publication.get("duration_seconds", -1)) - float(report["duration_seconds"])) > 1e-6:
            raise ValueError(f"Chapter duration differs from publication metadata: {chapter['id']}")
        inventory[chapter["id"]] = source_inventory(folder, progress["source_commit"])
    return chapters, inventory


def wav_boundaries(package: Path, chapters: list[dict]) -> tuple[list[dict], int, int]:
    boundaries = []
    cursor = 0
    sample_rate = None
    for chapter in chapters:
        master = safe_job(package, chapter["path"]) / "audio.wav"
        with wave.open(str(master), "rb") as audio:
            if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getcomptype() != "NONE":
                raise ValueError(f"Chapter master is not mono PCM16: {chapter['id']}")
            if sample_rate is None:
                sample_rate = audio.getframerate()
            if audio.getframerate() != sample_rate or sample_rate != 24000:
                raise ValueError(f"Chapter master is not 24 kHz: {chapter['id']}")
            frames = audio.getnframes()
        if frames <= 0:
            raise ValueError(f"Chapter master is empty: {chapter['id']}")
        boundaries.append({
            "id": chapter["id"],
            "chapter": chapter["chapter"],
            "title": chapter["title"],
            "start_frame": cursor,
            "end_frame": cursor + frames,
            "frames": frames,
            "start_seconds": cursor / sample_rate,
            "end_seconds": (cursor + frames) / sample_rate,
        })
        cursor += frames
    return boundaries, sample_rate or 24000, cursor


def write_concat(path: Path, package: Path, chapters: list[dict]) -> None:
    lines = ["ffconcat version 1.0"]
    for chapter in chapters:
        lines.append("file " + ffconcat_quote(safe_job(package, chapter["path"]) / "audio.wav"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_metadata(path: Path, book_number: int, boundaries: list[dict], sample_rate: int) -> None:
    lines = [";FFMETADATA1", f"title={ffmetadata_escape(f'The Niggatorial Tellings — Book {book_number}')}"]
    for item in boundaries:
        lines.extend((
            "[CHAPTER]",
            f"TIMEBASE=1/{sample_rate}",
            f"START={item['start_frame']}",
            f"END={item['end_frame']}",
            f"title={ffmetadata_escape(item['title'])}",
        ))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def metadata_unescape(value: str) -> str:
    output = []
    escaped = False
    for character in value:
        if escaped:
            output.append("\n" if character == "n" else character)
            escaped = False
        elif character == "\\":
            escaped = True
        else:
            output.append(character)
    if escaped:
        output.append("\\")
    return "".join(output)


def parse_chapters(text: str) -> list[dict]:
    chapters = []
    current = None
    for line in text.splitlines():
        if line == "[CHAPTER]":
            if current is not None:
                chapters.append(current)
            current = {}
        elif current is not None and "=" in line:
            key, value = line.split("=", 1)
            current[key] = metadata_unescape(value)
    if current is not None:
        chapters.append(current)
    return chapters


def duration_from_stderr(stderr: str) -> float:
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    if not match:
        raise ValueError("ffmpeg did not report the M4B duration.")
    return int(match[1]) * 3600 + int(match[2]) * 60 + float(match[3])


def verify_m4b(path: Path, boundaries: list[dict], sample_rate: int, total_frames: int) -> tuple[float, list[dict]]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("ffmpeg did not create a nonempty M4B.")
    run_ffmpeg(["-v", "error", "-i", str(path), "-f", "null", "-"])
    metadata = run_ffmpeg(["-i", str(path), "-f", "ffmetadata", "-"])
    reported_duration = duration_from_stderr(metadata.stderr)
    expected_duration = total_frames / sample_rate
    if abs(reported_duration - expected_duration) > 0.25:
        raise ValueError("M4B duration differs from the concatenated chapter masters.")
    actual = parse_chapters(metadata.stdout)
    if len(actual) != len(boundaries):
        raise ValueError("M4B chapter count differs from progress.json.")
    parsed = []
    for expected, item in zip(boundaries, actual):
        try:
            numerator, denominator = item["TIMEBASE"].split("/", 1)
            unit = int(numerator) / int(denominator)
            start_seconds = int(item["START"]) * unit
            end_seconds = int(item["END"]) * unit
        except (KeyError, ValueError, ZeroDivisionError) as exc:
            raise ValueError("M4B contains invalid chapter timing metadata.") from exc
        tolerance = max(unit, 1 / sample_rate) + 1e-9
        if item.get("title") != expected["title"]:
            raise ValueError(f"M4B chapter title differs: {expected['id']}")
        if abs(start_seconds - expected["start_seconds"]) > tolerance or abs(end_seconds - expected["end_seconds"]) > tolerance:
            raise ValueError(f"M4B chapter boundary differs: {expected['id']}")
        parsed.append({
            **expected,
            "m4b_timebase": item["TIMEBASE"],
            "m4b_start": int(item["START"]),
            "m4b_end": int(item["END"]),
        })
    return expected_duration, parsed


def upload_asset(repo: Path, tag: str, asset: Path) -> tuple[str, str]:
    release_result = run(["gh", "release", "view", tag, "--repo", REPO, "--json", "url"], okay=(0, 1))
    if release_result.returncode:
        raise ValueError(f"Required GitHub release tag does not exist: {tag}")
    endpoint = f"repos/{REPO}/releases/tags/{tag}"
    release = json.loads(run(["gh", "api", endpoint]).stdout)
    known = {item["name"]: item for item in release.get("assets", [])}
    expected_digest = "sha256:" + sha(asset)
    existing = known.get(asset.name)
    if existing:
        if existing.get("digest") != expected_digest or existing.get("size") != asset.stat().st_size:
            raise ValueError("Existing M4B differs; an explicit versioned retake is required.")
    else:
        run(["gh", "release", "upload", tag, asset, "--repo", REPO])
    release = json.loads(run(["gh", "api", endpoint]).stdout)
    remote = next((item for item in release.get("assets", []) if item.get("name") == asset.name), None)
    if remote is None or remote.get("digest") != expected_digest or remote.get("size") != asset.stat().st_size:
        raise ValueError("Uploaded M4B hash/size verification failed.")
    return remote["browser_download_url"], release["html_url"]


def package_book(config: dict, book_number: int) -> None:
    package = config["package_root"]
    repo = config["repo_root"]
    progress_path = package / "production" / "progress.json"
    with locked_progress(progress_path) as progress:
        initial_progress = copy.deepcopy(progress)
    chapters, inventory_before = validate_book(initial_progress, package, book_number)
    source_commit = initial_progress["source_commit"]

    boundaries, sample_rate, total_frames = wav_boundaries(package, chapters)
    books = package / "books"
    books.mkdir(parents=True, exist_ok=True)
    output = books / f"book-{book_number:02}.m4b"
    temporary_output = output.with_suffix(".part.m4b")
    temporary_output.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"book-{book_number:02}-", dir=config["log_root"]) as temporary_name:
        temporary = Path(temporary_name)
        concat_path = temporary / "chapters.ffconcat"
        metadata_path = temporary / "chapters.ffmetadata"
        write_concat(concat_path, package, chapters)
        write_metadata(metadata_path, book_number, boundaries, sample_rate)
        run_ffmpeg([
            "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-f", "ffmetadata", "-i", str(metadata_path), "-map", "0:a:0",
            "-map_metadata", "1", "-map_chapters", "1", "-c:a", "aac",
            "-b:a", "96k", "-ac", "1", "-ar", "24000", "-movflags", "+faststart",
            "-f", "ipod", str(temporary_output),
        ])
    duration, verified_boundaries = verify_m4b(temporary_output, boundaries, sample_rate, total_frames)
    temporary_output.replace(output)

    inventory_after = {chapter["id"]: source_inventory(safe_job(package, chapter["path"]), source_commit) for chapter in chapters}
    if inventory_after != inventory_before:
        raise ValueError("A chapter source or master changed while the book was being packaged.")

    tag = f"audiobook-book-{book_number:02}"
    audio_url, release_url = upload_asset(repo, tag, output)
    staging = config["log_root"] / "publish-assets" / f"book-{book_number:02}"
    staging.mkdir(parents=True, exist_ok=True)
    notes = staging / "release-notes.md"
    notes.write_text(
        f"Complete Book {book_number} audiobook containing all {len(chapters)} chapters.\n\n"
        "Source matching, audio decoding, chapter boundaries, duration, and remote asset hashes passed automated checks. "
        "Human listening review remains pending.\n\n"
        f"[Chapter index]({URL}/blob/main/audiobook/LISTEN.md)\n",
        encoding="utf-8", newline="\n",
    )
    run([
        "gh", "release", "edit", tag, "--repo", REPO,
        "--title", f"The Niggatorial Tellings — Book {book_number} — Complete audiobook",
        "--notes-file", notes, "--prerelease=false", "--latest=false",
    ])

    book_key = f"book-{book_number:02}"
    book_publication = {
        "status": "published",
        "audio_url": audio_url,
        "release_url": release_url,
        "sha256": sha(output),
        "size": output.stat().st_size,
        "duration_seconds": duration,
        "sample_rate": sample_rate,
        "chapters": len(chapters),
    }
    chapter_document = {
        "book": book_number,
        "source_commit": source_commit,
        **book_publication,
        "chapter_boundaries": verified_boundaries,
        "checks": "source inputs unchanged; M4B decode, duration, chapter metadata, and remote SHA-256/size passed",
        "listening_review": "pending",
    }
    chapter_json = books / f"book-{book_number:02}.chapters.json"
    local_pending_document = {**chapter_document, "status": "upload_verified_pending_git"}
    save(chapter_json, local_pending_document)

    git(repo, "fetch", "origin", "main")
    git(repo, "merge", "--ff-only", "origin/main")
    with locked_progress(progress_path) as current:
        snapshot = copy.deepcopy(current)
    current_chapters, current_inventory = validate_book(snapshot, package, book_number)
    if [row["id"] for row in current_chapters] != [row["id"] for row in chapters] or current_inventory != inventory_before:
        raise ValueError("Book inputs changed before the Git publication step.")
    snapshot.setdefault("books", {})[book_key] = book_publication
    write_index(package, snapshot)
    sync_package(package, repo)
    save(repo / "audiobook" / "production" / "progress.json", snapshot)
    save(repo / "audiobook" / "books" / chapter_json.name, chapter_document)
    git(repo, "add", "--", "audiobook")
    git(repo, "diff", "--cached", "--check")
    changes = git(repo, "diff", "--cached", "--quiet", okay=(0, 1))
    if changes.returncode:
        git(repo, "commit", "-m", f"Publish complete audiobook Book {book_number}")
    git(repo, "push", "origin", "main")

    with locked_progress(progress_path) as current:
        live_rows = sorted(
            (row for row in current.get("chapters", []) if row.get("book") == book_number),
            key=lambda row: row["chapter"],
        )
        if live_rows != current_chapters:
            raise ValueError("Progress changed during the Git publication step; book status was not marked published.")
        current.setdefault("books", {})[book_key] = book_publication
    save(chapter_json, chapter_document)
    print(json.dumps({"book": book_number, "publication": book_publication}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--book", type=int, required=True)
    args = parser.parse_args()
    if args.book <= 0:
        raise ValueError("--book must be a positive integer.")
    config = resolve_config(args.config)
    config["log_root"].mkdir(parents=True, exist_ok=True)
    with publication_lock(config["log_root"]):
        package_book(config, args.book)


if __name__ == "__main__":
    main()
