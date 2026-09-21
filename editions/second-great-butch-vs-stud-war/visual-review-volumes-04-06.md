# Coalition Edition: visual review of Volumes 4–6

Review completed and frozen: 2026-09-20.

Result: no actionable visual layout defects found within the scope below. No JSON, PDF, builder, or book content was changed during this review.

## Exact scope

All 18 existing contact sheets were opened and visually inspected with `view_image`. Together they represent all 281 pages of the three PDFs:

| Volume | PDF pages | Contact sheets inspected |
| --- | ---: | --- |
| 4 | 95 | `volume-04-sheet-01.jpg` through `volume-04-sheet-06.jpg` |
| 5 | 93 | `volume-05-sheet-01.jpg` through `volume-05-sheet-06.jpg` |
| 6 | 93 | `volume-06-sheet-01.jpg` through `volume-06-sheet-06.jpg` |

The page counts were read from `Panorama-Volume-04.pdf`, `Panorama-Volume-05.pdf`, and `Panorama-Volume-06.pdf` in `../../outputs/ten-toes-down-panorama/` using pypdfium2. Contact-sheet filenames in this report are relative to this QA directory.

Two dense continuation pages were additionally rendered from the PDFs at 2.5× scale (1530 × 1980 pixels) and inspected with `view_image` at original detail:

- Volume 5, printed page 29: [full-size QA image](visual-review-v05-p29.png).
- Volume 6, printed page 29: [full-size QA image](visual-review-v06-p29.png).

Only those two QA images and this report were saved for this review.

## Findings

- No apparent clipping, overlapping text, missing-glyph boxes, blank PDF pages, stranded headings, or source-only spill pages appeared in the contact-sheet survey.
- Covers, front indexes, and routing pages maintain clear visual hierarchy. Longer index titles wrap without visibly colliding with adjacent columns.
- The practical game pages clearly distinguish their labels and retain readable separation between the short pitch, ordinary actions, principal catch, and first-try guidance.
- The repeated two-page game format is consistent: practical guidance precedes the complete comic scene, ruling, and sources. Repeated game identifiers and titles make the continuation relationship clear. White space on shorter pages appears intentional rather than evidence of missing content.
- The longer conversation sequences—Volume 4 pages 48–51, Volume 5 pages 27–30, and Volume 6 pages 27–30—remain within their body areas. The two full-size samples confirm clear gaps between the last body lines and the shaded chorus band, and between the chorus band and the footer.
- The chorus band keeps its heading and five-column, three-row text grid inside its shaded area, with visible padding and no apparent footer collisions. Its attribution is legible in the full-size samples.
- Unused cells on the final contact sheets are empty sheet-grid positions, not blank pages in the PDFs.

## Limits and stopping condition

This was a layout survey of every page at contact-sheet scale, supplemented by two targeted full-size checks. It was not an all-pages full-resolution text proofread, a factual review, a live-link or browser check, a physical print test, or a verification of the literal chorus-word count on every page. Those checks remain separate from this visual finding.

The reviewed PDFs had 95, 93, and 93 pages respectively. Any later reflow or appendix build is outside this frozen report and should be checked separately. No corrections are requested for these three reviewed volumes on the evidence inspected.
