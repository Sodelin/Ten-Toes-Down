# Production complete

Verified 2026-11-04T06:20:19.581603+00:00. All **130 chapters** and all **six complete chaptered M4B book packages** are published at Sodelin/Ten-Toes-Down. No rendering, chapter publication, or book packaging work remains.

The production worker is stopped, no production processes are running, and work/production-logs/STOP records completion. The completed hourly heartbeat ten-toes-down-chapter-recordings was deleted through the Codex automation tool. Do not restart production or recreate the heartbeat automatically.

All 129 chapters after the original Book I Chapter 1 use TICKET, the funeral ticket man: Kokoro am_michael at speed 0.95 for narration and dialogue. The original published Book I Chapter 1 recording is preserved (SHA-256 450044553da3befee461c6e205e0707ab587dbc176c3f23b64ae64b034ff3837).

Canonical source revision: 3f16cb8dc89171439167297d744e623d6b16df25. The six canonical source books remain unchanged against the published repository. Every saved chapter script and source excerpt matches its recorded source-check hash. No paid synthesis services or Amazon/YouTube uploads were used.

## Completed books

| Book | Chapters | Duration | Complete audio |
|---|---:|---:|---|
| 1 | 17 | 5:57:56 | [M4B](https://github.com/Sodelin/Ten-Toes-Down/releases/download/audiobook-book-01/book-01.m4b) |
| 2 | 20 | 5:37:10 | [M4B](https://github.com/Sodelin/Ten-Toes-Down/releases/download/audiobook-book-02/book-02.m4b) |
| 3 | 24 | 5:47:10 | [M4B](https://github.com/Sodelin/Ten-Toes-Down/releases/download/audiobook-book-03/book-03.m4b) |
| 4 | 22 | 5:13:32 | [M4B](https://github.com/Sodelin/Ten-Toes-Down/releases/download/audiobook-book-04/book-04.m4b) |
| 5 | 23 | 6:16:26 | [M4B](https://github.com/Sodelin/Ten-Toes-Down/releases/download/audiobook-book-05/book-05.m4b) |
| 6 | 24 | 5:53:16 | [M4B](https://github.com/Sodelin/Ten-Toes-Down/releases/download/audiobook-book-06/book-06.m4b) |

## Verification and local records

- work/audiobook-completion.json: completion, source preservation, worker stop, and automation deletion receipt.
- work/production-logs/book-06-recovery-20261104T061514Z/completion-audit.json: local versus GitHub SHA-256 and size verification for all 396 chapter audio, manifest, caption, and complete-book assets.
- work/audio-deliveries.json: Chapters 2 and 3, all six book completions, and full completion delivery receipts. Do not repeat those notifications.
- outputs/ten-toes-down-audio/chapters: preserved chapter masters, MP3s, scripts, captions, and manifests.
- outputs/ten-toes-down-audio/books: six complete M4B files, chapter metadata, and playlists.
- LISTEN.md: complete catalog of book and chapter downloads.

Automated source matching, chapter audio integrity, M4B decoding, duration, chapter boundaries, and remote asset hashes passed. Human listening review remains pending.

## Recovery history

Book VI encoding and validation had finished when the system rebooted at 2026-11-04 06:05 UTC, interrupting its upload. The saved book-06.m4b (SHA-256 2db379ebd952db951d5d8bc8b68bce894a9f857e12ba5cb7868fe697446460f6; 272823571 bytes) was verified and published with the explicit --reuse-existing option, without reencoding or replacing it. Backups and the recovery log are in work/production-logs/book-06-recovery-20261104T061514Z.

Earlier authentication and memory recovery checkpoints remain in work/production-logs/recovery-20261103T2153Z and work/production-logs/memory-recovery-20261104T0212Z. Saved segment caches, source files, historical scripts, and published assets are preserved. The rejected desktop-credential-transfer route remains prohibited.
