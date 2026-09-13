"""Run the bounded, local chapter render and publication queue."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

import psutil
from state import locked_progress

if os.name == "nt":
    import msvcrt


REQUIRED_CONFIG = (
    "package_root",
    "repo_root",
    "qwen_python",
    "kokoro_python",
    "qwen_model",
    "kokoro_models",
    "cache_root",
    "log_root",
)
VALID_STATUSES = {"needs_cast", "ready", "rendering", "rendered", "published", "failed"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, suffix=".part", delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def resolve_config(config_path: Path) -> dict:
    if not config_path.is_absolute():
        raise ValueError("--config must be an absolute path to the uncommitted local config.")
    raw = read_json(config_path)
    missing = [key for key in REQUIRED_CONFIG if not isinstance(raw.get(key), str) or not raw[key]]
    if missing:
        raise ValueError("Missing config paths: " + ", ".join(missing))
    base = config_path.parent
    config = dict(raw)
    for key in REQUIRED_CONFIG:
        path = Path(raw[key])
        config[key] = (path if path.is_absolute() else base / path).resolve()
    if raw.get("publish_script"):
        path = Path(raw["publish_script"])
        config["publish_script"] = (path if path.is_absolute() else base / path).resolve()
    else:
        config["publish_script"] = None
    config["config_path"] = config_path.resolve()
    return config


def validate_progress(value) -> None:
    if not isinstance(value, dict) or not isinstance(value.get("source_commit"), str):
        raise ValueError("progress.json must contain source_commit and chapters.")
    chapters = value.get("chapters")
    if not isinstance(chapters, list):
        raise ValueError("progress.json chapters must be an array.")
    seen = set()
    for chapter in chapters:
        required = ("id", "book", "chapter", "title", "words", "status", "path", "release_tag")
        if not isinstance(chapter, dict) or any(key not in chapter for key in required):
            raise ValueError("Each progress chapter must contain all required fields.")
        if chapter["id"] in seen or chapter["status"] not in VALID_STATUSES:
            raise ValueError("Duplicate chapter ID or invalid status: " + str(chapter.get("id")))
        seen.add(chapter["id"])


def load_progress(progress_path: Path) -> dict:
    value = read_json(progress_path)
    validate_progress(value)
    return value


def update_chapter(progress_path: Path, chapter_id: str, status: str, error: str | None = None) -> dict:
    """Mutate one chapter while retaining concurrent edits to all other chapters."""
    with locked_progress(progress_path) as progress:
        validate_progress(progress)
        for chapter in progress["chapters"]:
            if chapter["id"] == chapter_id:
                chapter["status"] = status
                if error is None:
                    chapter.pop("error", None)
                else:
                    chapter["error"] = error[-2000:]
                chapter["updated_at"] = now()
                return dict(chapter)
        raise ValueError(f"Chapter disappeared from progress.json: {chapter_id}")


def recover_interrupted(progress_path: Path) -> None:
    with locked_progress(progress_path) as progress:
        validate_progress(progress)
        for chapter in progress["chapters"]:
            if chapter["status"] == "rendering":
                chapter["status"] = "ready"
                chapter.pop("error", None)
                chapter["updated_at"] = now()


def write_state(state_path: Path, started: str, current_job: str | None) -> None:
    atomic_json(
        state_path,
        {"pid": os.getpid(), "started": started, "heartbeat": now(), "current_job": current_job},
    )


@contextlib.contextmanager
def single_instance(lock_path: Path):
    if os.name != "nt":
        raise RuntimeError("This production worker requires Windows msvcrt file locking.")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RuntimeError("Another production worker already holds the lock.") from exc
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    finally:
        handle.close()


def run_logged(command: list[str], log_path: Path, label: str) -> None:
    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        log.write(f"\n[{now()}] {label}\n")
        log.flush()
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, text=True)
        if result.returncode:
            raise RuntimeError(f"{label} exited with status {result.returncode}")


def log_tail(log_path: Path, extra: str) -> str:
    try:
        prior = log_path.read_text(encoding="utf-8", errors="replace")[-1800:]
    except OSError:
        prior = ""
    return (prior + "\n" + extra)[-2000:]


def chapter_paths(config: dict, chapter: dict) -> tuple[Path, Path, Path]:
    relative = Path(chapter["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe chapter path: {relative}")
    job = (config["package_root"] / relative).resolve()
    job.relative_to(config["package_root"])
    return job, job / "script.json", job / "audio"


def selected_qwen_roles(script_path: Path) -> list[str]:
    rows = read_json(script_path)
    if not isinstance(rows, list) or not rows:
        raise ValueError("Chapter script must be a nonempty JSON array.")
    speakers = {row.get("speaker") for row in rows if isinstance(row, dict)}
    return [role for role in ("AIDEN", "TANK") if role in speakers]


def verify_result(script_path: Path, out: Path, declared_words: int) -> None:
    rows = read_json(script_path)
    manifest_path = out.with_suffix(".manifest.json")
    wav_path = out.with_suffix(".wav")
    mp3_path = out.with_suffix(".mp3")
    for path in (manifest_path, wav_path, mp3_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Renderer did not create a nonempty result: {path}")
    manifest = read_json(manifest_path)
    expected_words = sum(len(row["text"].split()) for row in rows)
    checks = (
        (manifest.get("source_script_sha256") == sha256(script_path), "source script hash"),
        (manifest.get("segments") == len(rows), "segment count"),
        (manifest.get("spoken_words") == expected_words, "spoken word count"),
        (expected_words == declared_words, "progress word count"),
        (manifest.get("mp3_decodes") is True, "MP3 decode check"),
        (isinstance(manifest.get("verbatim_source_check"), dict), "verbatim source check"),
        (manifest.get("duration_seconds", 0) > 0, "audio duration"),
        (manifest.get("sample_rate") == 24000, "sample rate"),
    )
    failed = [label for okay, label in checks if not okay]
    if failed:
        raise ValueError("Result manifest failed: " + ", ".join(failed))


def render_chapter(config: dict, chapter: dict, log_path: Path) -> None:
    job, script_path, out = chapter_paths(config, chapter)
    if not script_path.is_file():
        raise FileNotFoundError(f"Chapter script is missing: {script_path}")
    package = config["package_root"]
    validation = [
        str(config["kokoro_python"]), str(package / "render.py"), "--script", str(script_path),
        "--cast", str(package / "cast.json"), "--models", str(config["kokoro_models"]),
        "--validate-only",
    ]
    run_logged(validation, log_path, "input verification")

    roles = selected_qwen_roles(script_path)
    overrides = None
    if roles:
        qwen_cache = config["cache_root"] / "qwen" / "shared"
        qwen_cache.mkdir(parents=True, exist_ok=True)
        command = [
            str(config["qwen_python"]), str(package / "voice-design" / "render_scene.py"),
            "--model", str(config["qwen_model"]), "--cache", str(qwen_cache),
            "--script", str(script_path), "--roles", *roles,
        ]
        run_logged(command, log_path, "Qwen role rendering")
        overrides = qwen_cache / "index.json"
        if not overrides.is_file():
            raise ValueError("Qwen renderer did not create its override index.")

    kokoro_cache = config["cache_root"] / "kokoro"
    kokoro_cache.mkdir(parents=True, exist_ok=True)
    job.mkdir(parents=True, exist_ok=True)
    command = [
        str(config["kokoro_python"]), str(package / "render.py"), "--script", str(script_path),
        "--cast", str(package / "cast.json"), "--models", str(config["kokoro_models"]),
        "--cache", str(kokoro_cache), "--out", str(out), "--title", chapter["title"],
    ]
    if overrides is not None:
        command.extend(("--overrides", str(overrides)))
    run_logged(command, log_path, "Kokoro assembly")
    verify_result(script_path, out, chapter["words"])


def publish_chapter(config: dict, chapter: dict, log_path: Path) -> None:
    script = config["publish_script"]
    if script is None:
        raise RuntimeError("No publish_script is configured; chapter remains rendered.")
    command = [
        str(config["qwen_python"]), str(script), "--config", str(config["config_path"]),
        "--chapter", chapter["id"],
    ]
    run_logged(command, log_path, "chapter publication")


def package_completed_book(config: dict, progress_path: Path, book: int) -> None:
    progress = load_progress(progress_path)
    key = f"book-{book:02}"
    chapters = [row for row in progress["chapters"] if row["book"] == book]
    if not chapters or any(row["status"] != "published" for row in chapters):
        return
    if progress.get("books", {}).get(key, {}).get("status") == "published":
        return
    log_path = config["log_root"] / f"{key}-package.log"
    try:
        run_logged([
            str(config["qwen_python"]),
            str(config["package_root"] / "production" / "package_book.py"),
            "--config", str(config["config_path"]), "--book", str(book),
        ], log_path, "complete book packaging")
    except Exception as exc:
        # A packaging failure never changes already published chapter statuses.
        with locked_progress(progress_path) as current:
            current.setdefault("books", {})[key] = {
                "status": "failed", "error": log_tail(log_path, str(exc)),
                "updated_at": now(),
            }


def process_job(config: dict, progress_path: Path, chapter: dict, stop_path: Path) -> None:
    log_path = config["log_root"] / f"{chapter['id']}.log"
    try:
        if chapter["status"] == "ready":
            update_chapter(progress_path, chapter["id"], "rendering")
            render_chapter(config, chapter, log_path)
            chapter = update_chapter(progress_path, chapter["id"], "rendered")
            if stop_path.exists() or config["publish_script"] is None:
                return
        if stop_path.exists():
            return
        publish_chapter(config, chapter, log_path)
        update_chapter(progress_path, chapter["id"], "published")
        package_completed_book(config, progress_path, chapter["book"])
    except Exception as exc:
        error = log_tail(log_path, f"{type(exc).__name__}: {exc}")
        update_chapter(progress_path, chapter["id"], "failed", error)


def process_alive(pid) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
    except (psutil.Error, OSError):
        return False


def print_status(config: dict, progress_path: Path, state_path: Path) -> None:
    progress = load_progress(progress_path)
    counts = {status: 0 for status in sorted(VALID_STATUSES)}
    for chapter in progress["chapters"]:
        counts[chapter["status"]] += 1
    try:
        state = read_json(state_path)
    except (OSError, ValueError, TypeError):
        state = {}
    print(json.dumps({
        "pid": state.get("pid"),
        "running": process_alive(state.get("pid")),
        "started": state.get("started"),
        "heartbeat": state.get("heartbeat"),
        "current_job": state.get("current_job"),
        "queue": counts,
    }, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--once", action="store_true", help="Process at most one render/publication job.")
    parser.add_argument("--status", action="store_true", help="Print worker and queue status without starting.")
    parser.add_argument("--stop-file", default="STOP", help="Stop filename within log_root (default: STOP).")
    args = parser.parse_args()
    config = resolve_config(args.config)
    if Path(args.stop_file).name != args.stop_file:
        raise ValueError("--stop-file must be a filename within log_root.")
    stop_path = config["log_root"] / args.stop_file
    progress_path = config["package_root"] / "production" / "progress.json"
    state_path = config["log_root"] / "worker-state.json"
    if args.status:
        print_status(config, progress_path, state_path)
        return 0

    config["log_root"].mkdir(parents=True, exist_ok=True)
    started = now()
    with single_instance(config["log_root"] / "worker.lock"):
        recover_interrupted(progress_path)
        write_state(state_path, started, None)
        processed = 0
        while not stop_path.exists():
            progress = load_progress(progress_path)
            ready = next((row for row in progress["chapters"] if row["status"] == "ready"), None)
            rendered = None
            if config["publish_script"] is not None:
                rendered = next((row for row in progress["chapters"] if row["status"] == "rendered"), None)
            chapter = rendered or ready
            if chapter is None:
                write_state(state_path, started, None)
                if args.once or not any(row["status"] == "needs_cast" for row in progress["chapters"]):
                    break
                time.sleep(30)
                continue
            write_state(state_path, started, chapter["id"])
            process_job(config, progress_path, chapter, stop_path)
            processed += 1
            write_state(state_path, started, None)
            if args.once:
                break
        write_state(state_path, started, None)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"worker: {exc}", file=sys.stderr)
        raise SystemExit(1)
