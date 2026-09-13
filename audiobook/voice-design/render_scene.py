"""Render exact script turns with locally designed Qwen character voices.

Only AIDEN and TANK are supported. Models and reference WAVs must already
exist locally. Cache/index.json is written only after every selected turn
has a verified audio file. No model downloading or paid service is used.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent))
from verify_verbatim import verify_verbatim

PARAMETERS = {
    "language": "English",
    "max_new_tokens": 1024,
    "non_streaming_mode": True,
    "do_sample": True,
    "top_k": 50,
    "top_p": 1.0,
    "temperature": 0.9,
    "repetition_penalty": 1.05,
    "subtalker_dosample": True,
    "subtalker_top_k": 50,
    "subtalker_top_p": 1.0,
    "subtalker_temperature": 0.9,
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def contained(root: Path, path: Path) -> Path:
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes cache/model directory: {path}") from exc
    if path == root:
        raise ValueError("Expected a file beneath the directory.")
    return path


def atomic_json(root: Path, path: Path, data: dict) -> None:
    target = contained(root, path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=root, suffix=".part", delete=False
        ) as handle:
            temporary = contained(root, Path(handle.name))
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(contained(root, target))
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            contained(root, temporary).unlink()


def validate_audio(sound, rate, np, label: str) -> dict:
    if rate != 24000 or sound.ndim != 1 or len(sound) == 0:
        raise ValueError(f"Expected nonempty mono 24 kHz speech: {label}")
    if not np.isfinite(sound).all():
        raise ValueError(f"Non-finite speech samples: {label}")
    duration = len(sound) / rate
    rms = float(np.sqrt(np.mean(sound.astype(np.float64) ** 2)))
    if duration < 0.08 or rms < 0.00001:
        raise ValueError(f"Empty or near-silent speech: {label}")
    return {
        "sample_rate": rate,
        "frames": len(sound),
        "duration_seconds": duration,
        "peak": float(np.max(np.abs(sound))),
        "rms": rms,
    }


def read_cached(wav: Path, sidecar: Path, settings: dict, np, sf):
    if not wav.is_file() or not sidecar.is_file():
        return None
    try:
        metadata = read_json(sidecar)
        if metadata.get("settings") != settings:
            return None
        if digest(wav) != metadata.get("sha256"):
            return None
        sound, rate = sf.read(wav, dtype="float32")
        audio = validate_audio(sound, rate, np, wav.name)
        if metadata.get("frames") != audio["frames"] or metadata.get("sample_rate") != rate:
            return None
        return {**metadata, **audio}
    except (OSError, ValueError, RuntimeError, TypeError, AttributeError):
        return None


def write_audio(cache: Path, wav: Path, sound, rate, sf) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=cache, suffix=".part", delete=False) as handle:
            temporary = contained(cache, Path(handle.name))
        sf.write(temporary, sound, rate, format="WAV", subtype="FLOAT")
        temporary.replace(contained(cache, wav))
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            contained(cache, temporary).unlink()


def model_identity(directory: Path) -> dict:
    manifest_path = directory / "download.manifest.json"
    manifest = read_json(manifest_path)
    repo = manifest.get("repo", "")
    revision = manifest.get("revision", "")
    if repo not in {"Qwen/Qwen3-TTS-12Hz-0.6B-Base", "Qwen/Qwen3-TTS-12Hz-1.7B-Base"}:
        raise ValueError("--model must contain a downloaded Qwen3-TTS 12Hz Base snapshot.")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("The model download manifest must pin an exact revision.")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("The model download manifest has no verified file inventory.")
    # Authenticate the local snapshot against its download inventory before
    # using its revision as an audio-cache identity.
    for item in files:
        name = item.get("path", "")
        if not isinstance(name, str) or not name or "\\" in name:
            raise ValueError("Invalid model file path in download manifest.")
        path = contained(directory, directory / name)
        if not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", "")):
            raise ValueError(f"Missing model file SHA-256: {name}")
        if digest(path) != item["sha256"]:
            raise ValueError(f"Model file differs from the verified download: {name}")
    return {
        "model_repo": repo,
        "revision": revision,
        "download_manifest_sha256": digest(manifest_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True, help="Local Qwen Base snapshot directory.")
    parser.add_argument("--cache", type=Path, required=True, help="Directory for reusable WAVs and index.json.")
    parser.add_argument("--script", type=Path, default=BASE.parent / "pilot" / "script.json")
    parser.add_argument("--roles", nargs="+", choices=["AIDEN", "TANK"], default=["AIDEN", "TANK"])
    args = parser.parse_args()
    verification = verify_verbatim(args.script)
    rows = read_json(args.script)
    roles = list(dict.fromkeys(args.roles))
    selected = [row for row in rows if row["speaker"] in roles]
    if any(not any(row["speaker"] == role for row in selected) for role in roles):
        raise ValueError("A requested role has no turns in this script.")
    directions = read_json(BASE / "directions.json")

    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel

    versions = {name: importlib.metadata.version(name) for name in [
        "torch", "torchaudio", "qwen-tts", "transformers", "accelerate", "numpy", "soundfile", "librosa"
    ]}
    identity = model_identity(args.model.resolve())
    engine = {**identity, "versions": versions, "attention": "sdpa", "dtype": "bfloat16"}
    references = {}
    for role in roles:
        item = directions[role]
        reference = BASE / (role.lower() + "-reference.wav")
        manifest = read_json(BASE / (role.lower() + ".manifest.json"))
        reference_sha = digest(reference)
        if manifest.get("role") != role or manifest.get("reference_sha256") != reference_sha:
            raise ValueError(f"Reference WAV differs from its voice-design manifest: {role}")
        if not isinstance(item.get("text"), str) or not item["text"].strip():
            raise ValueError(f"Reference transcript is missing: {role}")
        if manifest.get("text") != item["text"]:
            raise ValueError(f"Reference transcript differs from its voice-design manifest: {role}")
        sound, rate = sf.read(reference, dtype="float32")
        validate_audio(sound, rate, np, role + " reference")
        references[role] = {"audio": (sound, rate), "text": item["text"], "sha256": reference_sha}

    cache = args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    model = None
    prompts = {}
    segments = {}
    for count, row in enumerate(selected, 1):
        role = row["speaker"]
        ref = references[role]
        seed_material = json.dumps([directions[role].get("seed", 20260913), role, row["id"], row["text"]], ensure_ascii=False)
        seed = int.from_bytes(hashlib.sha256(seed_material.encode("utf-8")).digest()[:8], "big") % (2 ** 63 - 1)
        settings = {
            "text": row["text"], "speaker": role, "reference_sha256": ref["sha256"],
            "reference_text": ref["text"], "engine": engine,
            "parameters": PARAMETERS, "seed": seed, "x_vector_only_mode": False,
        }
        key = hashlib.sha256(json.dumps(settings, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        wav = contained(cache, cache / (key + ".wav"))
        sidecar = contained(cache, cache / (key + ".json"))
        metadata = read_cached(wav, sidecar, settings, np, sf)
        hit = metadata is not None
        if not hit:
            if model is None:
                if not torch.cuda.is_available():
                    raise RuntimeError("This rendering configuration requires an NVIDIA CUDA GPU.")
                torch.set_num_threads(4)
                model = Qwen3TTSModel.from_pretrained(
                    str(args.model.resolve()), device_map="cuda:0", dtype=torch.bfloat16,
                    attn_implementation="sdpa", local_files_only=True,
                )
            if role not in prompts:
                prompts[role] = model.create_voice_clone_prompt(
                    ref_audio=ref["audio"], ref_text=ref["text"], x_vector_only_mode=False,
                )
            torch.manual_seed(seed)
            start = time.perf_counter()
            with torch.inference_mode():
                waves, rate = model.generate_voice_clone(
                    text=row["text"], voice_clone_prompt=prompts[role], **PARAMETERS,
                )
            if len(waves) != 1:
                raise ValueError(f"Expected one generated waveform: {row['id']}")
            sound = np.asarray(waves[0], dtype=np.float32)
            audio = validate_audio(sound, rate, np, row["id"])
            # 12Hz codec: a result near the generation ceiling needs explicit
            # inspection before it can silently become a reusable cache entry.
            if audio["duration_seconds"] >= PARAMETERS["max_new_tokens"] / 12 * 0.98:
                raise ValueError(f"Possible generation-limit cutoff in segment {row['id']}; split the source turn for review.")
            write_audio(cache, wav, sound, rate, sf)
            metadata = {
                "settings": settings, "sha256": digest(wav), **audio,
                "render_seconds": round(time.perf_counter() - start, 3),
                "status": "Technical checks passed; spoken-word listening review pending.",
            }
            atomic_json(cache, sidecar, metadata)
        segments[row["id"]] = {
            "speaker": role, "text": row["text"], "wav": wav.name,
            "sha256": metadata["sha256"], "voice": "qwen-designed-" + role.lower(),
            "speed": 1.0,
        }
        print(f"{count:03}/{len(selected)} {row['id']} {role} {metadata['duration_seconds']:.2f}s" + (" cached" if hit else " generated"), flush=True)

    # The source must still be the one verified before a potentially long run.
    if digest(args.script) != verification["script_sha256"]:
        raise ValueError("Script changed during rendering; rerun before assembling this scene.")
    atomic_json(cache, cache / "index.json", {
        "source_script_sha256": verification["script_sha256"],
        "engine": engine, "segments": segments,
    })
    print(f"Complete: {len(segments)} verified turn WAVs; {cache / 'index.json'}", flush=True)


if __name__ == "__main__":
    main()
