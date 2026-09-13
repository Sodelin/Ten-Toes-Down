> **Current production:** From Book I chapter 2 onward, all narration and dialogue use the funeral ticket man’s voice (Kokoro `am_michael`, speed 0.95), selected by the author. The previously published Chapter 1 and pilot retain their original cast. Historical multi-voice development notes below describe that earlier approach.

# Chapter production

[Listen and track all six books](../LISTEN.md) · [Recurring cast](cast-inventory.md) · [Queue data](progress.json)

The project contains 130 chapter jobs. Source bodies are frozen at commit `3f16cb8dc89171439167297d744e623d6b16df25`. All narration and dialogue are retained; typography and scene dividers are represented through speech and pauses. Chapter headings appear in player metadata.

Each chapter moves through **needs cast → ready → rendering → rendered → published**. Failed jobs retain their logs and cached takes. A chapter becomes ready only after its complete quotation map has been reviewed and its script matches the pinned source. The selected Aiden and deeper Tank voices remain fixed; the chapter cast records other recurring and incidental roles.

Small agents handle the speaker assignments. Free local Qwen and Kokoro models perform synthesis. The worker sleeps without making model/API requests while no reviewed chapter is ready. An hourly Codex continuation prepares the next chapters and resolves failures. The computer must be awake for local work to run; interrupted jobs resume from cached takes.

## Output per chapter

- MP3 recording, exact script, source record and cast assignments.
- Render manifest with source checks, voice identities, timings and audio-integrity results.
- Segment-timed SRT captions. These are coarse segment timings, not word-level forced alignment.
- A GitHub release download and a place in the book playlist.

Recordings are GitHub **release assets**, grouped by book. Source scripts, manifests and the listening index remain in Git. This follows GitHub's recommended binary-distribution mechanism and keeps the repository from accumulating hours of MP3s in its history. [GitHub large-file documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)

An in-progress book release is marked prerelease. Published means the recording exists and passed the declared automated checks. It does not mean a human reviewed every syllable, nor that Amazon or YouTube publication has occurred.

## Local worker

The runtime configuration stays outside the published package because it contains machine-specific paths. It points to the two isolated Python environments, downloaded models, caches, logs, output package and Git checkout. No access token is stored in that file; publication uses the already authenticated GitHub CLI.

```powershell
python production/worker.py --config C:/path/to/local-config.json --status
python production/worker.py --config C:/path/to/local-config.json
```

Use the Qwen environment's Python for these commands. Only one worker may hold its lock. A `STOP` file in the configured log directory requests a stop after the current render, before another chapter or publication begins. The worker runs with a hidden window. Logs and the process state identify what is currently running.

Never use `os.kill(pid, 0)` as a Windows status probe. The worker uses `psutil` for read-only process checks.

## Add a reviewed chapter

`prepare.py --init-all` creates the source inventory before production begins. Do not rerun inventory initialization while a worker is editing the queue.

Read a chapter's `source-excerpt.md` and fill its `assignment-template.json`, using every quotation ID exactly once. Source line numbers must match. Named characters keep their registered IDs. Anonymous speakers receive chapter-specific IDs unless the source establishes continuity. Add missing voices to the cast before marking the chapter ready.

```powershell
python production/prepare.py --repo C:/path/to/Ten-Toes-Down --book 1 --chapter 2 --assignments C:/path/to/reviewed-assignments.json --reviewer "speaker attribution review"
```

The preparer rejects incomplete assignments, unknown voices and changed text. Chapter I.1 reuses the verified pilot prefix and its cached takes. Do not overwrite a queued or published chapter: later retakes need an explicit version and retained prior recording.

After all chapters in a book are available, build and verify its final playlist and chaptered M4B package, then remove that release's in-progress designation. After all six books and their packages are uploaded, stop the worker and pause the continuation.

```powershell
python production/package_book.py --config C:/path/to/local-config.json --book 1
```

The packager requires every chapter to be published and its local WAV master to pass verification. It exports AAC at 96 kbps in an M4B with chapter navigation, checks the decoded file and chapter boundaries, uploads the asset and marks the book release complete. A shared publication lock serializes chapter and book uploads and Git updates. Different existing release assets are never overwritten.
