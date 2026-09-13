"""Verify an audiobook script against its pinned, unchanged source excerpt.

Only whitespace, curly double quotation marks, and standalone *** scene
dividers are ignored. Apostrophes and all other punctuation remain significant.
"""

from pathlib import Path
import argparse
import hashlib
import json
import re
import sys


BASE = Path(__file__).resolve().parent


class VerbatimError(ValueError):
    """The script or its source provenance failed verification."""


def normalize(text):
    text = re.sub(r"(?m)^[ \t]*\*\*\*[ \t]*\r?$", "", text)
    text = text.replace("\u201c", "").replace("\u201d", "")
    return " ".join(text.split())


def first_mismatch(expected, actual):
    limit = min(len(expected), len(actual))
    position = next(
        (index for index in range(limit) if expected[index] != actual[index]),
        limit,
    )
    start = max(0, position - 65)
    stop = position + 90
    expected_char = repr(expected[position]) if position < len(expected) else "<end>"
    actual_char = repr(actual[position]) if position < len(actual) else "<end>"
    return (
        f"First mismatch at normalized character {position + 1}, "
        f"source word {expected[:position].count(' ') + 1}: "
        f"expected {expected_char}, got {actual_char}.\n"
        f"Source: {expected[start:stop]!r}\n"
        f"Script: {actual[start:stop]!r}"
    )


def verify_verbatim(script_path, source_excerpt_path=None, source_metadata_path=None):
    """Return a verification report or raise VerbatimError before synthesis.

    The source-excerpt.md and source.json sidecars default to the script folder.
    Source metadata records the pinned full Git blob hash. This offline check
    verifies the excerpt hash and script text; it does not fetch the Git blob.
    """
    script_path = Path(script_path)
    excerpt_path = (
        Path(source_excerpt_path) if source_excerpt_path is not None
        else script_path.parent / "source-excerpt.md"
    )
    metadata_path = (
        Path(source_metadata_path) if source_metadata_path is not None
        else script_path.parent / "source.json"
    )
    rows = json.loads(script_path.read_text(encoding="utf-8-sig"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    if not isinstance(rows, list) or not rows:
        raise VerbatimError("Script must be a nonempty JSON array.")
    if not isinstance(metadata, dict):
        raise VerbatimError("Source metadata must be a JSON object.")
    if not re.fullmatch(r"[0-9a-f]{40}", metadata.get("commit", "")):
        raise VerbatimError("Source metadata must pin a full 40-character Git commit.")
    if not re.fullmatch(r"[0-9a-f]{64}", metadata.get("source_sha256", "")):
        raise VerbatimError("Source metadata must record the full Git blob SHA-256.")
    excerpt_info = metadata.get("excerpt")
    if not isinstance(excerpt_info, dict):
        raise VerbatimError("Source metadata must describe the excerpt.")
    if not (
        isinstance(excerpt_info.get("start_line"), int)
        and isinstance(excerpt_info.get("end_line"), int)
        and 1 <= excerpt_info["start_line"] <= excerpt_info["end_line"]
    ):
        raise VerbatimError("Source excerpt line bounds must be positive and inclusive.")
    excerpt_bytes = excerpt_path.read_bytes()
    excerpt_hash = hashlib.sha256(excerpt_bytes).hexdigest()
    if excerpt_hash != excerpt_info.get("sha256"):
        raise VerbatimError(
            "Source excerpt SHA-256 differs from its pinned metadata: "
            f"expected {excerpt_info.get('sha256')}, got {excerpt_hash}."
        )

    seen = set()
    spoken = []
    speakers = set()
    for row_index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise VerbatimError(f"Segment {row_index} must be a JSON object.")
        segment_id = row.get("id")
        if not isinstance(segment_id, str) or not segment_id or segment_id in seen:
            raise VerbatimError(f"Invalid or duplicate segment ID: {segment_id!r}.")
        seen.add(segment_id)
        text = row.get("text")
        if not isinstance(text, str) or not text.strip():
            raise VerbatimError(f"Segment {segment_id} has no spoken text.")
        if "tts_text" in row and row["tts_text"] != text:
            raise VerbatimError(
                f"Segment {segment_id}: tts_text changes the spoken text. "
                "Remove the override; verbatim mode requires exactly the text field."
            )
        if not isinstance(row.get("speaker"), str) or not row["speaker"]:
            raise VerbatimError(f"Segment {segment_id} has no speaker.")
        speakers.add(row["speaker"])
        spoken.append(text)

    expected = normalize(excerpt_bytes.decode("utf-8"))
    actual = normalize(" ".join(spoken))
    if expected != actual:
        raise VerbatimError(first_mismatch(expected, actual))
    return {
        "status": "PASS: script matches the source excerpt verbatim",
        "segments": len(rows),
        "spoken_words": len(actual.split()),
        "speakers": sorted(speakers),
        "commit": metadata["commit"],
        "repository_path": metadata.get("repository_path"),
        "source_lines": [excerpt_info["start_line"], excerpt_info["end_line"]],
        "source_sha256": metadata["source_sha256"],
        "excerpt_sha256": excerpt_hash,
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        "normalization": "whitespace, curly double quotation marks, standalone *** only",
        "audio_listening_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", type=Path, default=BASE / "pilot" / "script.json")
    parser.add_argument("--source-excerpt", type=Path)
    parser.add_argument("--source-metadata", type=Path)
    args = parser.parse_args()
    try:
        report = verify_verbatim(args.script, args.source_excerpt, args.source_metadata)
    except (VerbatimError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"VERBATIM CHECK FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
