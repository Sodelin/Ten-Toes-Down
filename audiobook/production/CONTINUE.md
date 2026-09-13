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
2. Keep AIDEN and TANK references in `voice-design/` fixed. Existing pilot/reference hashes are in the manifests. The first complete chapter has 16 speaking roles. `cast.json` marks their selected Qwen engine and locked references; its Kokoro preset fields are fallback settings. The worker always generates their Qwen overrides. Do not accidentally render them with stock voices.
3. Prepare the earliest `needs_cast` chapters, ideally 2–4 at a time ahead of the worker, using lower-cost agents with modest reasoning (gpt-5.6-sol medium or gpt-5.6-luna medium). Give each agent a bounded chapter group and the source/assignment-template paths. Require every quotation ID/line, consistent named IDs, and notes on ambiguous attribution. Do not repeat entire source text in assignment output.
4. Register missing cast IDs with distinct choices where characters speak together, grounded in the cast inventory and actual chapter. Keep the core cast consistent. The narration is Aiden unless the source clearly changes narrator; flag any actual POV exception for careful handling rather than guessing.
5. Import a reviewed map with `prepare.py --book N --chapter N --assignments <file> --repo <checkout>`. Its mandatory source check must pass before status becomes ready. Preparation and worker status changes use the shared queue lock.
6. The hidden worker processes ready chapters and invokes `publish.py`. The publisher uploads MP3/manifest/SRT release assets, verifies remote hashes, updates LISTEN.md/playlists, commits scripts/status and pushes. It never force-pushes or replaces an existing different asset. Source novels are not edited.

## Recovery and remaining work

- If the worker is absent and work is ready, start it with Windows `Start-Process -WindowStyle Hidden`, separate stdout/stderr log files, and absolute config path. Its lock rejects duplicate workers. Downloaded models and both environments already exist; no paid service or new account is needed.
- A failed rendering job can be reset to ready under `locked_progress` after resolving its concrete error. Cache files make reruns cheap. A failed publication after valid audio exists should be reset to rendered, so it retries upload/commit without changing its manifest or sound. Inspect publication logs and remote assets before retrying.
- **b04-c07's quotation typography is repaired in the parser**, with an exception guarded by its exact source hash. Its 16-line Aiden rap is one dialogue span (quote 42, source line 2656); the refreshed template contains 75 quotes. Source bytes are unchanged. The old progress parse_error clears when its ordinary reviewed assignment map is prepared. Do not repeat this repair or silently narrate the whole chapter as Aiden.
- Chapters b01-c02 through b01-c07 already have reviewed scripts queued behind chapter 1. The cast has 65 registered roles, with evidence in the linked chapter notes. Start the next preparation at b01-c08 after checking actual progress; do not duplicate these completed speaker passes.
- Do not rerun --init-all while the worker is active; it writes the full inventory. Do not edit a ready/rendering/published chapter in place. Use explicit retake versions when needed.
- Automated input matching does not prove every synthesized word was heard correctly. Keep listening-review status honest; repair reported misreads without rewriting source text.
- Once all chapters in a book are published and its progress.books entry is not published, run `work/qwen-runtime/Scripts/python.exe outputs/ten-toes-down-audio/production/package_book.py --config <absolute work/production-config.json> --book N`. It validates sources and masters, streams a chaptered M4B, checks decoding and chapter boundaries, verifies GitHub asset hashes, updates the playlist/index and marks the release complete. The first worker process predates automatic packaging integration, so check this explicitly in continuation; later worker starts call it after each complete book. Book packaging errors never invalidate published chapters. Book and chapter publishers share an OS lock for Git/release mutations. M4B retries are byte deterministic in the tested local runtime. On completion of all six books/packages, stop the worker and pause the heartbeat.
- Keep commentary concise. Notify the user about book completion or a meaningful blocker, not unchanged polling. No Amazon/YouTube posting is authorized yet.

The active local worker, queue, saved chapter assignments and GitHub files are the authoritative progress record. Do not claim all books are done from the existence of their source folders.

An active hourly thread heartbeat already exists: `ten-toes-down-chapter-recordings`, attached to task `01a099fa-f37b-7881-8e58-2629964a1c0a`. Do not create another. Keep its notifications to book completion, meaningful failure or full completion. User explicitly authorized a lower-cost model/medium reasoning for ongoing work.
