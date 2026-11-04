> **2026-11-04 production resumed with memory guards:** The bounded b05-c23 cache recovery succeeded, reusing 37 saved segments. Complete Book V (23 chapters) is published and its local/GitHub SHA-256, size, and chapter metadata are verified; its completion delivery is recorded in work/audio-deliveries.json. One existing serial worker resumed at b06-c01 after memory reserves recovered. There were 106 published chapters and 24 pending Book VI chapters at resume. Always check worker.py --status and live processes before restarting; never duplicate a worker. The worker checks 3072 MiB free RAM and 4096 MiB free Windows commit before each render and writes STOP after the first failed chapter. Preserve any new STOP/user hold and inspect the log before a bounded retry. b06-c02 retains 30/56 cached segments. Recovery evidence is in work/production-logs/memory-recovery-20261104T0212Z. Keep TICKET / am_michael / 0.95 and preserve all published assets and canonical sources.

> **2026-11-03 production resumed:** GitHub identity is verified as Sodelin. Book IV chapters 7 and 8 are fully published from their preserved recordings; remote MP3/manifest/caption hashes and sizes and the GitHub index commit were verified. The existing serial worker resumed at chapter 9. Before any restart, check worker.py --status and live processes; never start a duplicate. The authentication STOP and prior checkpoint are archived in work/production-logs/recovery-20261103T2153Z. The earlier restart and authentication holds are resolved. The rejected desktop-credential-transfer route remains prohibited.

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
