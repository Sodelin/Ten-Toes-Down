# Visual review — Coalition Edition Volumes 1–3

## Result

All 19 supplied contact sheets were visually inspected through `view_image`: Volume 1 sheets 01–07 (109 initial pages), Volume 2 sheets 01–06 (93 pages), and Volume 3 sheets 01–06 (95 pages). This covers every thumbnail of all 297 pages in that initial render set.

One concrete layout defect was found: the initial Volume 1 page 15 held only the four-line closing paragraph of Article 12 above the chorus, leaving almost the entire page empty. Root corrected the builder. I rendered and visually inspected the revised Volume 1 pages 3, 14 and 15: the paragraph now remains with Article 12 on page 14, the next section begins cleanly on page 15, and the front index has updated page numbers. Revised Volume 1 has 108 pages. That defect is resolved.

No other visible clipping, overlapping text, footer collision, missing-glyph block, stranded heading, blank page, or comparable short orphan spill was found in this scope. The intentional practical-guide / complete-comic-scene two-page treatment remains clear; scene/source pages are not source-only spill pages. The chorus occupies its own shaded footer band and is visibly separate from the body.

## Larger-resolution inspection

Rendered with bundled Python and pypdfium2 at scale 2 (144 dpi); inspected through `view_image`:

- Initial front indexes: Volume 1 page 3, Volume 2 page 3, Volume 3 page 3. Long title wrapping, case IDs, page numbers and the direct sustained-conversation link are legible and aligned.
- Initial Volume 1 page 15: confirmed the orphan defect described above.
- Volume 2 page 28: dense sustained dialogue remains clear of the chorus and footer.
- Volume 2 pages 69–70: the long Dragon Quest XI S edition title, practical labels, complete scene and source note fit cleanly.
- Volume 3 page 29: dense dialogue and short exchanges remain legible with clear margins.
- Volume 3 pages 70–71: The Vanishing of Ethan Carter Redux practical card and complete scene/source card fit, including the long title and URL lines.
- Revised Volume 1 pages 3, 14 and 15: verified corrected navigation and removal of the orphan.

This is 13 full-page visual inspections across the initial and corrected versions, in addition to every contact-sheet thumbnail. QA render images are temporary files under `tmp/pdfs/coalition-review-01-03`.

## Incidental content correction and remaining handoff

The rendered sequence revealed that Volume 2's interlude occurs after P050. P060 still described the veterans discovering their opposite-side signatures as unknown later in the book. Root explicitly authorized a fiction-only JSON repair and notes/hash update. That repair is saved: they now inspect the already revealed copies and dispute compliance. Protected-field comparison still passes, and the scene remains 179 words. No PDF or builder was edited in this lane.

At this report's snapshot, the available Volume 2 PDF did not yet contain the revised P060 paragraph. Root must include the updated JSON in its final build; the revised P060 page needs a final targeted render check after that rebuild. The current visual pass does not claim inspection of a PDF change that has not yet appeared.

The review does not test PDF link activation in a viewer, EPUB/browser rendering, physical printing, game behavior, or source-factual accuracy. Root owns those separate checks and the final publication snapshot. Any later appendix or layout addition requires review of its new/changed pages.

## PDF snapshot at report time

| Volume | Current pages | SHA256 |
|---|---:|---|
| 1 | 108 | `ac99285cdad0dc104d84ad3ecb66ee751eaade14e6712e511af4927fd1af483f` |
| 2 | 93 | `01008398c8746f49fee1d1e0663c0142733f62ac02f7b3771b558face21ebfd7` |
| 3 | 95 | `43e5acba2a732c41eb47c523f85c869685767c17519c5de4063cb91b45c3280d` |


## Addendum — historical field guide and repaired P060

Reviewed final Volume 1 contact sheets 07–09, covering pages 97–133, with special attention to all newly added historical material on pages 106–130 and the source/credits blocks on 131–133. All 22 historical dossiers fit on their intended pages; the history, evidence limits, explicitly labeled fictional commentary, and source/read-scope blocks remain visually distinct. No clipped text, missing-glyph box, source-only spill page or body/footer overlap was found.

One actionable layout defect remains in this 133-page snapshot: the history index uses page 107 for H01–H20 and spills only H21–H22 onto the otherwise nearly empty page 108. The final two rows should fit on the index page or the index should be deliberately balanced across two pages. Root was notified. This is a navigation-layout correction, not a dossier-content defect.

Full-resolution checks at 144 dpi covered Volume 1 pages 107 and 108 (index spill), 121 (Moraga, long title and three source records) and 128 (Kolkata, three source records), plus Volume 2 page 50 (P060). The sources on pages 121 and 128 have clear space above the chorus band. P060 now visibly contains the repaired paragraph: the veterans inspect already-known two-sided copies and dispute whether the promises were kept. The earlier pending P060 rebuild check is resolved; the complete scene, verdict and source block on page 50 fit cleanly.

This adds three contact sheets / 37 thumbnails and five full-resolution visual inspections to the earlier review. Other generated QA images from this check were not separately counted as visually inspected. The field-guide index correction still requires a targeted recheck after root's update.

| Volume | Pages in this addendum snapshot | SHA256 |
|---|---:|---|
| 1 | 133 | `056be009840b46e608044db92a59d783d77d54fa8957413404992da4d2e0a3b9` |
| 2 | 93 | `cec66bc064a9d4a71b9bf0f29982c057d6df02574742e1cdcf78a1afb477678a` |


## Final targeted recheck — history index resolved

The final Volume 1 now has 132 pages. I rendered pages 107–108 again at 144 dpi and inspected both through `view_image`. Page 107 contains all 22 history entries in two columns, with clear title wrapping, aligned row separators and page labels, and ample clearance above the chorus. Page 108 begins H01 as expected; its historical text, question, evidence limit, fictional interlude and source record fit cleanly. The former two-entry index spill page is gone. No clipping, overlap, missing glyphs or footer collision was found in these revised pages.

Final disposition: both concrete visual defects identified in this review are resolved, and the P060 continuity correction has been verified in the rendered Volume 2. No remaining visual blocker was found within the exact scope recorded above. This final check adds two full-resolution page inspections; it is not a new whole-book review or a test of link activation.

Final Volume 1 SHA256: `2c29469798ca80f206b7fdef9f9285cf914416331c864a32caaf054b415c50a7`.
