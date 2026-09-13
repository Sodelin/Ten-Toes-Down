# Ten Toes Down audio

Free local audiobook production for **The Niggatorial Tellings**.

## Listen

- [Finished pilot — new Aiden and Tank, verbatim source text](pilot/funeral-new-voices.mp3): **3:25**, six character voices.
- [Funeral excerpt — corrected verbatim text, provisional Kokoro cast](pilot/funeral-pilot.mp3): 3:23, six voices, 560 words.
- [Read along](pilot/script.md) · [Unchanged source excerpt](pilot/source-excerpt.md)
- [Aiden and Tank voice development](voice-design/README.md)

The selected pilot uses Qwen-designed voices for Aiden and Tank, with Kokoro presets for the ticket man, guest, Shawna and Mercedes. Tank uses the deeper, fuller take requested in feedback. The user asked to stop auditioning and finish; these are the production choices for this pilot. The older CPU baseline remains available for comparison.

**The script follows the book word for word.** All four added explanations have been removed. This continuous excerpt starts with the first line of Book I, chapter 1 and ends with “She turned me toward the door.” It is not the whole chapter or all six books. Aiden narrates and speaks in the same voice. Original slang, profanity, narration and dialogue attributions remain intact.

Source: [Book I, pinned revision](https://github.com/Sodelin/Ten-Toes-Down/blob/3f16cb8dc89171439167297d744e623d6b16df25/editions/niggatorial-tellings/books/book-01.md#L5-L141). Silas is present in this edition and now enters at the source's original point.

## Reproduce the CPU baseline

Use 64-bit Python 3.12 and run these commands from this folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe download_models.py
.\.venv\Scripts\python.exe render.py --title "The Funeral - verbatim draft"
```

Setup downloads packages and approximately 354 MB of model assets. After setup, synthesis runs locally on four CPU threads with no network. No API key, subscription, hosted Space or paid endpoint is needed. The GPU voice-design experiment has separate installation instructions and a larger download.

## Source fidelity and retakes

`render.py` now requires `source-excerpt.md` and `source.json` beside every chapter script. It verifies the excerpt hash and checks the entire script against it before synthesis. Only whitespace, curly double quotation marks and standalone `***` dividers are ignored. Changed words, punctuation and `tts_text` overrides fail the check.

```powershell
.\.venv\Scripts\python.exe render.py --validate-only
.\.venv\Scripts\python.exe verify_verbatim.py
```

This verifies the **input text**. The generated speech still needs listening review for mispronunciations, missing words, repeated words and delivery. Technical checks confirm finite nonempty segments, successful MP3 decoding and no full-scale clipped master samples; they do not certify the acting.

Change a voice preset or speed in `cast.json`, or a pause in `pilot/script.json`, then rerun. Cached unchanged speech is reused. Kokoro does not interpret written `direction` notes as acting instructions. Keep the source wording unchanged during retakes and keep the readable transcript synchronized.

For another chapter, prepare its speaker-tagged script and source sidecars first:

```powershell
.\.venv\Scripts\python.exe render.py --script chapters/b01-c02/script.json --out chapters/b01-c02/audio --title "Book I, Chapter 2"
```

The renderer does not automatically assign speakers from raw novel prose. Models, environments, caches and WAV masters are excluded from GitHub. The local delivery includes WAV masters.

## Files

| File | Purpose |
|---|---|
| `pilot/script.json` | Exact spoken text, speaker IDs and pauses |
| `pilot/source.json` and `source-excerpt.md` | Pinned source and hash-checked excerpt |
| `pilot/funeral-pilot.manifest.json` | Cast, timing, hashes and technical/source checks |
| `cast.json` | Provisional Kokoro presets and speeds |
| `render.py` | Cached synthesis, assembly, leveling and export |
| `verify_verbatim.py` | Mandatory source-fidelity check |
| `voice-design/` | Aiden and Tank performance experiment |
| `production-plan.md` | Chapter-by-chapter recording workflow |
| `research.md` and `NOTICE.md` | Primary sources, capabilities and attribution |

## Full audiobook and CDs

The source has 130 chapters and approximately 329,879 words. At an assumed 150–170 spoken words per minute, the full reading would take roughly **32–37 hours**, before pauses. It has not been produced. Settle the cast with short scenes, then produce and review chapter MP3s. Chaptered M4B files can follow.

A normal audio CD holds about 74–80 minutes. The saga would need at least **25–28 fully packed 80-minute discs**, likely more with chapter breaks. MP3/data discs need a compatible player. [Audacity's CD guide](https://manual.audacityteam.org/man/burning_music_files_to_a_cd.html)

```powershell
.\.venv\Scripts\python.exe render.py --cd
```

This additionally exports a 44.1 kHz, 16-bit stereo `.cd.wav`; it does not burn a disc.

Creative direction: Nolan. Source prose: ChatGPT's existing adaptation. Speaker assignment and audio production: Codex. The source novels remain unchanged; this excerpt adds no prose. See [notices](NOTICE.md), [research](research.md) and [production plan](production-plan.md).
