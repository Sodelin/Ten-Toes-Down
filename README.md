# Ten Toes Down

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
