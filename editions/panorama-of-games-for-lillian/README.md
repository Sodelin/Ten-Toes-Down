# The Ten Toes Down Panorama of Games for Lillian

**240 distinct games · six volumes · 106,435 words · 310 unique reading pages.**

An enormous, original comic game catalogue narrated through Aiden and the Ten Toes Down ensemble. Six departments, optional traits, dice, imaginary Stamp Tokens, a snack amendment and a very short appeals court conspire to answer an ordinary question: what would be fun to play?

The games are real. The ministries are not. Every refusal is free.

## Read or browse

- [Complete omnibus PDF](Panorama-Complete-Omnibus.pdf)
- [Reflowable EPUB](Ten-Toes-Down-Panorama.epub)
- [Offline interactive finder](Start-Here.html) - download and open locally; GitHub displays the source. To use nearby PDF links, extract the full reader bundle into one folder.
- [Complete reader bundle](Panorama-Reader-Bundle.zip)
- [Editable manuscript](Manuscript.md)
- [All 240 games with volume/page references](game-index.csv)

| Volume | Department | PDF | Cases |
|---|---|---|---|
| 1 | The Bureau of Suspiciously Interesting People | [Read](Panorama-Volume-01.pdf) | P001-P040 |
| 2 | The Committee for Taking One's Turn | [Read](Panorama-Volume-02.pdf) | P041-P080 |
| 3 | The Ministry of Looking Around Before Doing Anything | [Read](Panorama-Volume-03.pdf) | P081-P120 |
| 4 | The Department of Things That Fit Into Other Things | [Read](Panorama-Volume-04.pdf) | P121-P160 |
| 5 | The Office of People Who Have Something to Tell You | [Read](Panorama-Volume-05.pdf) | P161-P200 |
| 6 | The Joint Commission for Bringing a Friend | [Read](Panorama-Volume-06.pdf) | P201-P240 |

## What the labels mean

Promising means an editorial starting point with a stated first check. Conditional means a meaningful catch needs checking. Detour means a narrower activity or a more demanding alternative, not a general easy-play recommendation. These are candidates across a range of demands; the catalogue does not claim that all 240 meet every reader’s preferences.

Current distribution: 33 promising, 188 conditional, 19 detours.

The first three offline evidence filters require explicit developer declarations from an exact matching inspected record. Unknown evidence does not pass. Ordinary pace, tracking burden and co-op labels are separate editorial screening fields. Mouse-only does not mean hold-free; camera comfort does not mean no camera movement; turn-based does not mean few menus. The exact edition and the real catch remain visible. No full-game playthrough or personal fit is claimed.

## Source and authorship

Creative direction: Nolan. New prose, selection system and production: ChatGPT. This is a separate companion experiment using the user-directed characters. The existing Ten Toes Down novels remain intact. Voice samples came from the revised comic edition’s Book I funeral opening and Book II academy arrival, plus the editorial record; the six complete novels were not reread line by line.

The text includes original fictional scenes and editorial research notes. Source descriptions are paraphrased; raw store descriptions, ROMs, game files and third-party artwork are not distributed. Source checks are dated 20 September 2026. Availability and features can change.

- [Per-game source notes](Source-Notes.md)
- [Machine-readable corpus](game-corpus.json)
- [Evidence ledger](evidence-ledger.json)
- [Routing rules](routing-rules.json)
- [Importable RIS references](references.ris)
- [CSL JSON references](references.csl.json)
- [Validation report](validation-report.json)
- [Build measurements](build-report.json)

The optional signed dice, traits and point spending were inspired by Fate. The coordinates, snack adjustment, incidents, vetoes and appeals are original comic selection rules. This is not a replacement for a Fate rulebook and does not imply endorsement. Full required attribution is in the books and [credits](credits.md).

## Print and reuse

The PDFs use Letter pages, white backgrounds, embedded reading fonts, live source links and case bookmarks. Print individual volumes to avoid handling the entire omnibus; fit to A4 when needed. Printed references use volume/page, so they remain valid in the concatenated omnibus. EPUB allows readers to enlarge and reflow the text.

The word count is measured once in the combined Markdown manuscript, including headings and source notes. Repeated PDF introductions, the offline app and source caches are not counted as extra prose. Six catalogue volumes are not represented as six 50,000-word novels.

## Rebuild

Source JSON and the builders are under `source/`. Copy or run that directory as a self-contained project; `python work/build_panorama.py`, `python work/build_panorama_finder.py` and `python work/validate_panorama.py` produce outputs under its `outputs/ten-toes-down-panorama/` directory. Python requires reportlab, pypdf, pypdfium2 and Pillow. The font directory defaults to Windows Georgia/Arial; set `PANORAMA_FONT_DIR` to an equivalent licensed font directory on other systems. Source declarations are preserved in sanitized per-game records; raw fetched descriptions are excluded.

Run `node work/test_panorama_finder.cjs` for the routing checks. UI checks and visual inspection scope are recorded separately in the validation files. No script in the source bundle publishes, purchases, installs games or contacts another person.
