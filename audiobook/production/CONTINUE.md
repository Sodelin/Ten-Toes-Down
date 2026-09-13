# Continuation checkpoint

Authorized objective: finish and upload all 130 chapters of all six books, verbatim, with a fleshed-out consistent cast. User requested token efficiency and approved choosing a cheaper model/effort. No further audition loop or repeated permission questions. Amazon/YouTube are future user plans; do not publish there.

Workspace: `C:/Users/nolan/Documents/Codex/2026-09-13/yo-yo-yo-my-nigga-nigga`.
Package: `outputs/ten-toes-down-audio`.
Git checkout: `work/audio-repository`, remote `https://github.com/Sodelin/Ten-Toes-Down`.
Local config (not committed): `work/production-config.json`.
Python: `work/qwen-runtime/Scripts/python.exe` (Qwen, queue, GitHub publisher); `work/audio-runtime/Scripts/python.exe` (Kokoro/assembly).
Source: story commit `3f16cb8dc89171439167297d744e623d6b16df25`; do not use newer story edits automatically.

## First actions

1. Read `progress.json` and the last worker log/state in `work/production-logs`. Run `worker.py --config <absolute work/production-config.json> --status`; it safely probes via psutil. If it is running, do not launch another worker or mutate the Git checkout during its publication. A long GPU generation can leave the worker-state timestamp unchanged; inspect chapter log activity before declaring a stall.
2. Keep AIDEN and TANK references in `voice-design/` fixed. Existing pilot/reference hashes are in the manifests. The first complete chapter has 16 speaking roles. `cast.json` holds engine presets; Aiden/Tank entries are stock fallback settings, but the worker always generates their Qwen overrides. Do not accidentally render them with stock voices.
3. Prepare the earliest `needs_cast` chapters, ideally 2–4 at a time ahead of the worker, using lower-cost agents with modest reasoning (gpt-5.6-sol medium or gpt-5.6-luna medium). Give each agent a bounded chapter group and the source/assignment-template paths. Require every quotation ID/line, consistent named IDs, and notes on ambiguous attribution. Do not repeat entire source text in assignment output.
4. Register missing cast IDs with distinct choices where characters speak together, grounded in the cast inventory and actual chapter. Keep the core cast consistent. The narration is Aiden unless the source clearly changes narrator; flag any actual POV exception for careful handling rather than guessing.
5. Import a reviewed map with `prepare.py --book N --chapter N --assignments <file> --repo <checkout>`. Its mandatory source check must pass before status becomes ready. Preparation and worker status changes use the shared queue lock.
6. The hidden worker processes ready chapters and invokes `publish.py`. The publisher uploads MP3/manifest/SRT release assets, verifies remote hashes, updates LISTEN.md/playlists, commits scripts/status and pushes. It never force-pushes or replaces an existing different asset. Source novels are not edited.

## Recovery and remaining work

- If the worker is absent and work is ready, start it with Windows `Start-Process -WindowStyle Hidden`, separate stdout/stderr log files, and absolute config path. Its lock rejects duplicate workers. Downloaded models and both environments already exist; no paid service or new account is needed.
- A failed rendering job can be reset to ready under `locked_progress` after resolving its concrete error. Cache files make reruns cheap. A failed publication after valid audio exists should be reset to rendered, so it retries upload/commit without changing its manifest or sound. Inspect publication logs and remote assets before retrying.
- One source chapter, **b04-c07**, has unmatched quotation typography in the simple parser. Its original source is preserved and it is marked needs_cast with parse_error. Resolve its dialogue spans without changing source words; add explicit span handling before preparing that chapter. Do not silently narrate the whole chapter as Aiden.
- Existing completed helper files may be waiting in work/: b01-c02-assignments.json, b01-c03-assignments.json, b01-c04-assignments.json, b01-next-cast.md. Check them before duplicating agent work.
- Do not rerun --init-all while the worker is active; it writes the full inventory. Do not edit a ready/rendering/published chapter in place. Use explicit retake versions when needed.
- Automated input matching does not prove every synthesized word was heard correctly. Keep listening-review status honest; repair reported misreads without rewriting source text.
- Once a book has all chapter MP3s, produce and verify its chaptered M4B and playlist; upload the M4B to that book release and mark the release complete. This packaging step remains to be implemented. On completion of all books, stop the worker and pause the heartbeat.
- Keep commentary concise. Notify the user about book completion or a meaningful blocker, not unchanged polling. No Amazon/YouTube posting is authorized yet.

The active local worker, queue, saved chapter assignments and GitHub files are the authoritative progress record. Do not claim all books are done from the existence of their source folders.
