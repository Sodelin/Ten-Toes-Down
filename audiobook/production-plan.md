# Ten Toes Down — word-for-word audio production

The spoken book must reproduce **The Niggatorial Tellings word for word**. Use the source edition pinned at commit `3f16cb8dc89171439167297d744e623d6b16df25`: [Book I and its source revision](https://github.com/Sodelin/Ten-Toes-Down/blob/3f16cb8dc89171439167297d744e623d6b16df25/editions/niggatorial-tellings/books/book-01.md). The original novels remain unchanged.

Keep every original word, including profanity, narration, dialogue, and dialogue attributions. Add no spoken recaps, orientation, explanations, new attributions, or ad-libs. Speaker labels and performance instructions belong in production metadata only. Improve clarity through **distinct voices, pacing, emphasis, and pauses at the existing section breaks**.

## Scope

The six books contain 130 chapters: 17, 20, 24, 22, 23, and 24. At approximately 329,879 words and a planning rate of 150–170 words per minute, the complete reading would run roughly **32–37 hours**, before performance pauses. This is an estimate, not a measured finished runtime.

Make one audio episode per original chapter. If a chapter needs multiple files, divide at an existing scene break; part numbers can appear in filenames and player metadata. The spoken text stays unchanged. A pilot is a precisely identified contiguous source excerpt, not a claim that the whole book has been recorded.

## Cast and delivery

Use one stable voice for Aiden's first-person narration and his dialogue. Give Shawna, Tank, and recurring characters consistent voices across all six books. Preserve existing narration even where a distinct voice makes its speaker attribution seem redundant.

| Role | Performance target |
|---|---|
| Aiden | Conversational confidence, amused disbelief, room for the punchline |
| Shawna | Clear, composed, quick responses |
| Tank | Warm, blunt, completely assured about absurd explanations |
| Ticket man | Dry service-desk delivery |
| Marcellus | Measured, precise, emotionally present |
| Minor roles | Distinct within a scene; reuse a small supporting cast consistently |

Audition the same exact source lines across candidate voices. Choose by listening to actual exchanges, especially slang, timing, and the transition between narration and dialogue. Save the cast, pronunciation settings, and generation parameters. Performance directions must not be read aloud. Keep jokes intact; adjust timing or choose another take instead of rewriting them.

Kokoro supplies the four supporting voices in the pilot. **Qwen3-TTS-12Hz-1.7B-VoiceDesign generated the selected Aiden and Tank voices; Base 0.6B reuses those synthetic references for their scene turns.** Its official model card lists Apache-2.0 licensing. The experiment designs a synthetic voice from a description; it does not clone a real person's recording. The local GPU audition succeeded; reference timings and memory measurements are in voice-design/README.md. Full-book reliability and performance still need review chapter by chapter. [Official Qwen VoiceDesign model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign)

## Repeatable workflow

1. **Pin the source.** Record the revision, book, chapter, and exact excerpt boundaries. Keep the source files unchanged.
2. **Tag speakers without editing text.** Split the source into ordered, contiguous segments. Each contains the original text, a source span, a speaker, and separate performance metadata. Existing dialogue attributions remain narration.
3. **Verify the text.** Reassemble the spoken source segments and compare their words and order with the selected source range. Ignore only documented non-spoken Markdown syntax. Reject any omitted, inserted, substituted, duplicated, or reordered words. The source-verification script is being prepared separately; do not claim this check has passed until its report exists.
4. **Render locally.** Generate a cacheable WAV for each speaker turn or short narration paragraph. Save engine/model revision, voice settings, source ID, and generated duration. Cache on text and all sound-affecting settings so a retake regenerates only the relevant segment.
5. **Assemble in order.** Add pauses at the original paragraph and section boundaries, balance voices, and save a chapter WAV master. Export MP3 listening files and an exact readable transcript from the same segment order.
6. **Listen and repair.** Check the complete pilot against the source. For each later chapter, inspect technical results and listen against its script before marking it finished. Regenerate misread lines; never repair an awkward reading by changing the author's words.

Minimal segment schema:

```json
{"id":"b01-c01-u0001","speaker":"aiden","text":"Nigga, it’s my motherfucking funeral.","source":{"file":"book-01.md","lines":[5,5]},"direction":"disbelieving, conversational","pause_after_ms":350}
```

Source offsets or a source hash should supplement line numbers. Directions and labels are metadata. Any engine pronunciation control must preserve the intended original word; it must not alter the transcript or bypass source comparison.

## QA and retakes

- Require one nonempty audio segment for each script segment, in source order. Flag missing output, clipping, long unintended silence, or a suspicious duration.
- Verify names, profanity, contractions, repeated words, sentence endings, and speaker changes by listening. Text matching proves the script matches the source; it cannot prove the synthesizer actually pronounced every word.
- Keep a defect log with segment ID, problem, and replacement take. Retake pronunciation or delivery errors while leaving the source text fixed.
- Compare voice levels on headphones and an ordinary speaker. Use a clean speech mix first. Report exactly what has been heard and checked; file inspection alone is not a performance review.

## Files and CDs

| Format | Use |
|---|---|
| Numbered MP3 chapters + transcript | First delivery; convenient listening and isolated retakes |
| One chaptered M4B per book | Later audiobook package; verify navigation and resume in the intended player |
| Standard audio CD | Usually 74–80 minutes per disc; the full saga needs at least about 25–28 tightly packed 80-minute discs, often more with natural breaks |
| MP3/data CD | More audio per disc, but requires a player that supports those files |

For a standard audio CD, export 44.1 kHz, 16-bit stereo PCM WAV and burn in Audio CD mode. A smaller MP3 does not extend the standard audio-CD playing-time limit. [Audacity's official CD guide](https://manual.audacityteam.org/man/burning_music_files_to_a_cd.html)

For later M4B packaging, derive chapter timestamps from the assembly manifest and preserve titles in the file metadata. [FFmpeg metadata documentation](https://ffmpeg.org/ffmpeg-formats.html#Metadata-1)

The digital workflow uses free software. Physical discs still require a burner and blank media. Choose the cast from the actual audition audio, then apply the same verified source-to-audio pipeline chapter by chapter.
