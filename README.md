# Ten Toes Down

## The Final Final Cut

*A deeply unnecessary motion picture in ten chapters.*

A new comic adaptation written by ChatGPT for Nolan, following Nolan's creative direction. This is a separate version of the supplied material. The generated prose is not attributed to Nolan.

- [Read the manuscript](editions/the-final-final-cut/manuscript.md)
- [Download the reading edition (PDF)](editions/the-final-final-cut/book.pdf)
- [Read the editorial and source record](docs/EDITORIAL_RECORD.md)

The brief: make a funnier, profane **parody of a parody** whose nested stories change what happens. The characters' desires, affection, and loyalty carry the conflict; the machinery of studios and institutions supplies obstacles and comic targets.

There are five narrative levels, with four nested enclosures inside the outer frame: the filming frame, Aiden's account of the adventure, his earlier cassette confession, Grant's prison story, and Candle's embedded play. The levels interact at the climax.

## Source material and influences

Nolan supplied two PDFs: `ChatGpt Fanfic (1).pdf`, the original conversational fanfic, and `Ten_Toes_Down_Aiden_and_the_Story_That_Wrote_Him.pdf`, titled *Ten Toes Down: Aiden and the Story That Wrote Him*. They were used as creative source material and are not uploaded in this edition commit. The editorial record explains what this adaptation carries forward and changes.

Structural influences named in the brief are Mary Shelley's [*Frankenstein*](https://www.gutenberg.org/cache/epub/84/pg84-images.html), Robert W. Chambers's [*The King in Yellow*](https://www.gutenberg.org/cache/epub/8492/pg8492-images.html), and Alexandre Dumas's [*The Count of Monte Cristo*](https://www.gutenberg.org/cache/epub/1184/pg1184-images.html). The embedded prison tale and play in this adaptation are newly written fiction.

## Rebuild the PDF

Use Python 3 with ReportLab. The renderer also expects Liberation Serif and DejaVu fonts at the standard Linux paths used in `scripts/build_pdf.py`. On Debian or Ubuntu, install `fonts-liberation2` and `fonts-dejavu-core` if those fonts are absent.

Run these commands from the repository root. Explicit paths select the published edition rather than the renderer's original workspace defaults:

```sh
python -m pip install -r requirements.txt
python scripts/build_pdf.py editions/the-final-final-cut/manuscript.md editions/the-final-final-cut/book.pdf
```

The renderer creates a 6-by-9-inch reading edition with a generated contents page and PDF bookmarks. Font versions, dependency versions, and PDF timestamps can change the binary output of a rebuild. `SHA256SUMS` records the exact files published in this edition; it does not assert byte-identical PDF rebuilds.

## Attribution

Creative direction: Nolan. Adaptation text and production: ChatGPT. The supplied source artifacts have separate provenance; this repository makes no claim that Nolan authored all source or generated text.
