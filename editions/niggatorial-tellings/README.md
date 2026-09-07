# Ten Toes Down: The Niggatorial Tellings

**Complete revised edition: 329,879 words, six books, 130 chapters.**

The story now opens at Aiden's own funeral, after the homecoming. A question from the sound technician starts the earlier Vegas story. The original first sixteen chapters follow as Book I chapters 2–17, and the entire six-book journey continues to its ending.

> “Nigga, it’s my motherfucking funeral.”
>
> The man taking tickets didn’t look up.
>
> “Forty dollars.”

- [Download the complete EPUB](https://github.com/Sodelin/Ten-Toes-Down/raw/refs/heads/main/editions/niggatorial-tellings/book.epub)
- [Read or download the complete PDF](book.pdf) — 2,125 pages, linked contents and bookmarks.
- [Complete Markdown manuscript](manuscript.md) · [plain-text download](https://github.com/Sodelin/Ten-Toes-Down/raw/refs/heads/main/editions/niggatorial-tellings/manuscript.md)
- [What changed and what was checked](editorial-record.md) · [Exact text changes](changes.patch)

| Book | Read separately | Chapters | Words with headings |
|---|---|---:|---:|
| 1 | [Blood Money and Blue Diamonds](books/book-01.md) | 17 | 59,111 |
| 2 | [Sky High, Ten Toes Higher](books/book-02.md) | 20 | 52,452 |
| 3 | [The Fastest King Alive](books/book-03.md) | 24 | 54,747 |
| 4 | [Every City Wants Him](books/book-04.md) | 22 | 49,371 |
| 5 | [The Crown of Midnight](books/book-05.md) | 23 | 59,339 |
| 6 | [Ten Toes Down Forever](books/book-06.md) | 24 | 54,835 |

Revised and expanded conversations appear in 59 distributed scenes across all six books, in addition to the new funeral opening. Frequent reclaimed language is carried through the exchanges and Aiden's narration. The edition retains the full plot, fixes identified continuity slips, and preserves the complete ending. It is a complete reading edition with targeted revisions, not a claim that every sentence was rewritten.

[The Greatest Man Alive and its original reading files remain intact.](../the-greatest-man-alive/)

Creative direction: Nolan. Adaptation and revision prose: ChatGPT. September 2026.

## Rebuild this edition

Run from the repository root after installing requirements.txt:

```bash
python editions/niggatorial-tellings/assemble.py
python editions/niggatorial-tellings/build_epub.py editions/niggatorial-tellings/manuscript.md editions/niggatorial-tellings/book.epub
python editions/niggatorial-tellings/build_pdf.py editions/niggatorial-tellings/manuscript.md editions/niggatorial-tellings/book.pdf
python scripts/audit_omnibus.py editions/niggatorial-tellings/manuscript.md
python scripts/check_reading_files.py editions/niggatorial-tellings/manuscript.md editions/niggatorial-tellings/book.pdf editions/niggatorial-tellings/book.epub editions/niggatorial-tellings/reading-checks.json
python editions/niggatorial-tellings/check_complete_epub.py
```

The original builders retain their original edition defaults. These edition-specific builders carry the new title. Published file hashes appear in SHA256SUMS; environment-dependent timestamps can change binary hashes on rebuild.
