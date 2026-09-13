# Current production checkpoint

The user changed direction: use ONE narrator for every remaining chapter, specifically the funeral ticket man, the second voice in the pilot. This is TICKET, Kokoro am_michael at speed 0.95. Do not return to Aiden/Tank synthesis or multi-character casting. Keep every book word for word.

All 129 unpublished chapter scripts have been converted and passed mandatory source verification. Book I chapter 1 remains available as the previously published multi-voice edition; do not overwrite its release assets. The immediate requested deliveries are Chapters 2 and 3 in the ticket voice. The earlier multi-voice script maps are backed up in work/multivoice-script-backup. Canonical novels and chapter source excerpts are unchanged.

Workspace: C:/Users/nolan/Documents/Codex/2026-09-13/yo-yo-yo-my-nigga-nigga.
Config: work/production-config.json (absolute path required by worker).
Python: work/qwen-runtime/Scripts/python.exe for the worker/publisher; worker uses work/audio-runtime/Scripts/python.exe for CPU Kokoro synthesis.
Worker: outputs/ten-toes-down-audio/production/worker.py.
Progress: outputs/ten-toes-down-audio/production/progress.json.
Logs: work/production-logs, including chapter logs and worker-state.json.
Git checkout: work/audio-repository; remote Sodelin/Ten-Toes-Down.

First run worker.py --config <absolute config> --status. Do not start a duplicate worker. The new single-voice worker performs rendering, chapter publication and completed-book M4B packaging automatically. No further speaker-attribution passes or agents are needed. All unpublished chapters are ready in book order.

If a job fails, inspect its log. Fix the concrete error and reset it under state.locked_progress: ready for a rendering retry, rendered for a publication retry after valid audio exists. Preserve caches. Never replace a different existing GitHub release asset; use explicit versioned retakes. Book/chapter publishing shares a publication lock. Local master WAVs and MP3s remain in outputs, release downloads hold the published audio, and Git stores scripts/manifests/index.

The existing hourly heartbeat ten-toes-down-chapter-recordings is attached to this task. Do not duplicate it. Deliver Chapters 2 and 3 here with local audio players and GitHub links when published, recording that notification locally. Otherwise notify only for book completion, an actionable failure, or all work complete. No paid services or Amazon/YouTube uploads. Pause the heartbeat and stop the worker after all requested chapters/book packages finish. Automated input matching is not human listening certification.

Delivery receipts are stored locally in work/audio-deliveries.json. Read that file before posting completed Chapters 2 and 3, and update it after delivering them.
