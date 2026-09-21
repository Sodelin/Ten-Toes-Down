# Ten Toes Down

## The Panorama of Games for Lillian

**240 real games · six comic catalogue volumes · 310 reading pages.** Aiden creates an extravagantly unnecessary game-selection administration, complete with dice, imaginary stamps, a snack amendment and an appeals court. Lillian can ignore all of it and choose directly.

[Open the Panorama](editions/panorama-of-games-for-lillian/) · [Complete PDF](editions/panorama-of-games-for-lillian/Panorama-Complete-Omnibus.pdf) · [EPUB](editions/panorama-of-games-for-lillian/Ten-Toes-Down-Panorama.epub) · [Offline reader bundle](editions/panorama-of-games-for-lillian/Panorama-Reader-Bundle.zip)

Original companion prose by ChatGPT under Nolan's creative direction. Includes 86,073 words of comic scenes, game descriptions and original selection rules; 106,435 words in the full manuscript with headings, metadata and source notes. Game demands and edition-specific catches are stated beside the comedy. The existing novels remain intact.

## Google Docs: books and listening parts

[Choose an edition and book](GOOGLE-DOCS.md) · [Open the Start Here index](https://docs.google.com/document/d/1TfSuhI79CTpGRgRYYLrmTI3HI7PYsQTZ4eVS9cubUw0)

All seven versions are listed separately: 23 complete books and shorter texts, plus 381 numbered listening parts, available as native Google Docs and organized by edition and book.

## Audiobook chapters

[Chapter recordings and progress](audiobook/LISTEN.md) · [Full cast and production workflow](audiobook/production/README.md)

## Audiobook pilot

[Listen to the verbatim funeral pilot](audiobook/pilot/funeral-new-voices.mp3) · [Read along](audiobook/pilot/script.md) · [Audio workflow and downloads](audiobook/README.md)

Distinct voices for six characters, including newly designed Aiden and Tank voices. The source text is unchanged and checked before rendering. Includes free local production scripts and reproducible voice references. This is a scene pilot, not the complete six-book recording.

## The Niggatorial Tellings — complete revised edition

**329,879 words · six books · 130 chapters.** Opens with Aiden's funeral, then moves into the Vegas origin as a flashback. Includes revised and expanded scenes throughout all six books and the complete ending.

- [Read the complete new edition](editions/niggatorial-tellings/)
- [Download EPUB](https://github.com/Sodelin/Ten-Toes-Down/raw/refs/heads/main/editions/niggatorial-tellings/book.epub)
- [Read or download PDF](editions/niggatorial-tellings/book.pdf)
- [Complete editable manuscript](editions/niggatorial-tellings/manuscript.md)
- [Revision and verification record](editions/niggatorial-tellings/editorial-record.md)

The earlier editions and their reading files below remain intact.

## The Viet Telling — complete Bell Street rewrite

**205,636 narrative words · four books · 111 chapters.** Aiden’s neighborhood crime rise, his father’s wedding and war, his living great-grandfather’s river battle, and a second Aiden novel about the Ninth Room, a stolen-prize race and an affair. Every book exceeds 50,000 narrative words.

- [Read the four rewritten novels](editions/the-viet-telling/)
- [Complete Markdown manuscript](editions/the-viet-telling/manuscript.md)
- [Google Docs by book and listening part](https://drive.google.com/drive/folders/1JqOaBDeWej36KHs8A17rhI8lbIb_7O7l)
- [Edition notes](editions/the-viet-telling/afterword.md)

Creative direction: Nolan. New prose: Codex. A separate, noncanonical alternate telling, in English and Markdown. Hòa’s untold history and true strength remain open.

## The Greatest Man Alive

The complete six-book Aiden epic: **318,891 words, 129 chapters, 2,049 PDF pages**. Written by ChatGPT for Nolan, following Nolan's creative direction.

Aiden becomes a valedictorian police captain, takes his Lamborghini to Sky High, conquers a Grand Prix, wins a criminal crown, and comes home for the weddings. Outrageous action, boasts, friendship, romance, and stories told inside other stories carry the six books to a complete ending.

- [Read or download the PDF](editions/the-greatest-man-alive/book.pdf)
- [Download the EPUB](editions/the-greatest-man-alive/book.epub)
- [Read the complete editable manuscript](editions/the-greatest-man-alive/manuscript.md)
- [Read the edition and source record](editions/the-greatest-man-alive/editorial-record.md)

| Book | Read separately | Chapters |
|---|---|---:|
| 1 | [Blood Money and Blue Diamonds](editions/the-greatest-man-alive/books/book-01.md) | 16 |
| 2 | [Sky High, Ten Toes Higher](editions/the-greatest-man-alive/books/book-02.md) | 20 |
| 3 | [The Fastest King Alive](editions/the-greatest-man-alive/books/book-03.md) | 24 |
| 4 | [Every City Wants Him](editions/the-greatest-man-alive/books/book-04.md) | 22 |
| 5 | [The Crown of Midnight](editions/the-greatest-man-alive/books/book-05.md) | 23 |
| 6 | [Ten Toes Down Forever](editions/the-greatest-man-alive/books/book-06.md) | 24 |

Word counts use whitespace splitting and include headings and front matter. The PDF is a 6-by-9-inch reading edition with linked contents and book/chapter bookmarks; the EPUB lets the reader choose type size.

## Earlier editions

Earlier versions remain preserved as separate adaptations:

- [Blood Money and Blue Diamonds — the previous 200-page edition](editions/blood-money-and-blue-diamonds/manuscript.md), [PDF](editions/blood-money-and-blue-diamonds/book.pdf), [record](editions/blood-money-and-blue-diamonds/editorial-record.md).
- [First Night in Vegas experiment](experiments/first-night-in-vegas.md).
- [The Final Final Cut — the earlier 84-page adaptation](editions/the-final-final-cut/manuscript.md), [PDF](editions/the-final-final-cut/book.pdf), [record](docs/EDITORIAL_RECORD.md).
- [Writing checkpoints for this epic](work-in-progress/the-greatest-man-alive/README.md).

## Rebuild the reading editions

Use Python 3 and install the dependencies in requirements.txt. The PDF renderer uses the Liberation Serif and DejaVu font families at the Linux paths listed in the script. The validation script also uses pdftotext from Poppler. Production was checked with ReportLab 4.4.9 and pypdf 6.10.0.

```sh
python -m pip install -r requirements.txt
python scripts/build_omnibus_pdf.py editions/the-greatest-man-alive/manuscript.md editions/the-greatest-man-alive/book.pdf
python scripts/build_epub.py editions/the-greatest-man-alive/manuscript.md editions/the-greatest-man-alive/book.epub
python scripts/audit_omnibus.py editions/the-greatest-man-alive/manuscript.md
python scripts/check_reading_files.py editions/the-greatest-man-alive/manuscript.md editions/the-greatest-man-alive/book.pdf editions/the-greatest-man-alive/book.epub reading-checks.json
```

Font versions, dependency versions, and PDF timestamps can change the binary output of a rebuild. SHA256SUMS records the exact files published; it does not promise byte-identical PDF rebuilds.

## Attribution

Creative direction: Nolan. Adaptation text and production: ChatGPT. The source record identifies the two user-supplied PDFs and the prior manuscript used for this expansion. This alternate-universe fanfiction includes invented crossover and alternate-history episodes.
