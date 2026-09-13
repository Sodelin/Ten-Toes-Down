# Free multi-voice audiobook research

Checked 13 September 2026 against project repositories, model cards, source code, and Hugging Face documentation. This is implementation research, not a listening-test verdict. Machine reported by root: Windows, RTX 4060 Laptop GPU, 8 GB VRAM, Python 3.12.

## Decision

The user wants **The Niggatorial Tellings spoken strictly word for word**. The source is pinned at commit `3f16cb8dc89171439167297d744e623d6b16df25`. Preserve all original narration, dialogue, attributions, slang, and repetitions. Add no spoken orientation, recap, explanation, or ad-lib. Distinct voices, delivery, and pauses must provide the improvement in clarity.

A **Kokoro ONNX baseline recording exists**, but the user rejected its Aiden and Tank voices. It remains a working technical baseline, not an accepted cast. The current audition experiment is **Qwen3-TTS-12Hz-1.7B-VoiceDesign**, which can design a synthetic voice from a written description. Its official card lists Apache-2.0 licensing. [Official VoiceDesign model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign)

**Current local status, reported by the production agent:** approximately 4.52 GB of VoiceDesign assets have been downloaded and verified; the test environment uses Python 3.12, PyTorch 2.6 with CUDA 12.4, and SDPA attention. Local inference succeeded on the RTX 4060 8 GB: Aiden reference 15.92 seconds of audio in 30.50 seconds, final Tank reference 9.44 seconds in 18.94 seconds, with a maximum observed allocation of about 4.36 GiB. The user asked to stop auditioning and finish; these voices are now selected for the pilot. Performance quality still needs listening judgment. These local setup facts are not claims made by the model card.

If a designed voice works, the scene rendering can use **Qwen3-TTS-12Hz-0.6B-Base** with the generated synthetic sample as a reusable reference. The official project documents a design-then-reference workflow, and the 0.6B Base supports reference-based generation. Whether that smaller model preserves the desired voice well enough is a listening test, not an established result here. No real person's recording is needed. The 0.6B Base does not advertise free-text instruction control. [Official workflow](https://github.com/QwenLM/Qwen3-TTS#voice-design-then-clone), [0.6B Base card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base)

Chatterbox, Piper, F5, and Qwen CustomVoice remain researched alternatives. No service bill is necessary for the local paths; downloads, storage, and render time still apply. Do not promote any candidate to the final cast before hearing its exact source-line auditions.

## What the options actually give us

| Option | License evidence | Compute/download reality | Cast and delivery | Fit here |
|---|---|---|---|---|
| Kokoro ONNX / Kokoro-82M | Wrapper MIT; original weights Apache-2.0. | CPU ONNX runtime; GPU optional. Wrapper describes model as roughly 300 MB or roughly 80 MB quantized, excluding voices/dependencies. | US English has 11 female and 9 male presets; speed and phoneme controls. No official free-text acting instruction API documented. | Existing baseline; Aiden and Tank voices rejected by the user. |
| Piper, maintained OHF fork | Engine GPL-3.0; voice models vary. Never apply repository-level metadata blindly to every voice. | Local ONNX engine. A medium Lessac model is 63.2 MB, plus config and runtime; multiple voices require multiple files. No exact RAM floor verified. | Separate voice models; phoneme overrides, silence and playback controls. | Small CPU fallback; audition quality before using for comedy. |
| Chatterbox Nano / Turbo | Code MIT; Nano and Turbo cards MIT. | Nano 110M; official repo claims 3x real time on 8 CPU cores. Nano repository currently 3 GB; dependencies additional. Turbo 350M. | Native laugh/chuckle/cough tags. One bundled conditioning voice; other cast members need reference clips. | Promising comic acting upgrade; more setup today. |
| Qwen3-TTS CustomVoice | Code and checked 0.6B/1.7B weights Apache-2.0. | 0.6B repository 2.5 GB; 1.7B 4.52 GB, plus runtime. Official examples target CUDA with bfloat16 and optional FlashAttention 2. No authoritative exact minimum VRAM verified. | Nine presets, male/female; English-native presets Ryan and Aiden are both male. All can speak supported languages. Only 1.7B officially advertises instruction control. | Worth an acting audition later; 8 GB GPU compatibility requires actual measurement. |
| Qwen3-TTS 1.7B VoiceDesign | Official weights Apache-2.0. | Current local download approximately 4.52 GB, verified by the production agent; Python 3.12/PyTorch 2.6 CUDA 12.4/SDPA test environment. | Written voice description plus exact source text; no reference recording required. | Generated the selected pilot reference voices locally. |
| Qwen3-TTS 0.6B Base | Official weights Apache-2.0. | Separate model/runtime load; throughput and memory use not measured here. | Reference-based generation; can audition reuse of a designed synthetic voice. No advertised instruction control. | Used to reuse the selected synthetic Aiden/Tank references in the pilot. |
| F5-TTS | Code MIT; official pretrained weights CC-BY-NC-4.0. | V1 Base checkpoint alone 1.35 GB, plus vocoder/runtime. Official GPU installation pathways; no Windows CPU throughput established. | Multi-style and multi-speaker features, reference audio with transcript. | More reference preparation and less permissive model license; no advantage for the first pilot. |

Primary sources for Kokoro: [wrapper README](https://github.com/thewh1teagle/kokoro-onnx), [original model card](https://huggingface.co/hexgrad/Kokoro-82M), [voice inventory and limitations](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).

Primary sources for Piper: [maintained engine](https://github.com/OHF-Voice/piper1-gpl), [voice licensing instructions](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md), [Lessac files](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium). Example licensing complexity: [Ryan medium card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ryan/medium/MODEL_CARD) identifies CC BY-NC-SA 4.0 training data and Lessac finetuning; [Lessac card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/lessac/medium/MODEL_CARD) links its own dataset license. We have not cleared a specific Piper cast for publication.

Primary sources for Chatterbox: [code and installation](https://github.com/resemble-ai/chatterbox), [Nano card](https://huggingface.co/ResembleAI/chatterbox-nano), [Nano files](https://huggingface.co/ResembleAI/chatterbox-nano/tree/main), [Turbo card](https://huggingface.co/ResembleAI/chatterbox-turbo).

Primary sources for Qwen: [official instructions and voice list](https://github.com/QwenLM/Qwen3-TTS), [0.6B CustomVoice files/license](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice/tree/main), [1.7B CustomVoice files/license](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice/tree/main), [1.7B VoiceDesign card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign), [0.6B Base card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base).

Primary sources for F5: [official setup and multi-speaker workflow](https://github.com/SWivid/F5-TTS), [weight license](https://huggingface.co/SWivid/F5-TTS), [V1 Base checkpoint](https://huggingface.co/SWivid/F5-TTS/tree/main/F5TTS_v1_Base).

## Kokoro implementation notes

The current main-branch wrapper declares version 0.6.1 and Python >=3.10,<3.14, with `onnxruntime`, `espeakng-loader`, `phonemizer`, and NumPy >=2 dependencies. The small example uses `Kokoro(model_file, voices_file).create(text, voice=..., speed=1.0, lang='en-us')`; it returns samples and sample rate for `soundfile.write`. This is the ONNX wrapper, distinct from the PyTorch `kokoro` package whose Windows instructions include installing espeak-ng. [Dependency file](https://raw.githubusercontent.com/thewh1teagle/kokoro-onnx/main/pyproject.toml), [official minimal example](https://raw.githubusercontent.com/thewh1teagle/kokoro-onnx/main/examples/save.py), [original PyTorch package](https://github.com/hexgrad/kokoro).

Verified official full-size files:

- [kokoro-v1.0.onnx](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx)
- [voices-v1.0.bin](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin)

Starter audition set: female `af_heart` and `af_bella`; male `am_fenrir`, `am_michael`, and `am_puck`. These are audition candidates, not a claim that the voices sound like a specific racial group or dialect. The author rates their training/target quality relatively higher than several alternatives. The voice notes warn that very short utterances below 10–20 tokens can underperform, while passages above roughly 400 tokens can rush; roughly 100–200 tokens is their preferred range. Preserve speaker turns, but group adjacent same-speaker lines where sensible. [Voice notes](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).

Neither these docs nor the other inspected sources benchmark this story's invented vocabulary or slang. Preserve the exact source words and punctuation in the script. Make a pronunciation test list for Aiden, Shawna, Ten Toes, invented words, and slang; pronunciation controls must still produce the original word. Listen for omitted or repeated words, substitutions, unwanted emphasis, and robotic one-word reactions. Repair performance with another take or voice setting, not a rewritten line. These are production recommendations, not source claims.

## Chatterbox source-code reality

The current Nano/Turbo source loads a bundled `conds.pt` when available, so an external reference is not required for its default voice despite the README example describing reference input. A different cast voice needs a reference; the code asserts that it exceed five seconds and uses up to ten seconds for the decoder reference. `generate` explicitly ignores CFG and exaggeration controls for Nano/Turbo; those controls belong to original Chatterbox. Nano/Turbo can instead use their supported vocalization tags. [Inspected implementation](https://raw.githubusercontent.com/resemble-ai/chatterbox/master/src/chatterbox/tts_turbo.py).

Default Nano download matching includes every safetensors file in its roughly 3 GB repository, including both approximately 1.06 GB decoder versions, though this code loads the meanflow decoder. Its current dependencies pin PyTorch 2.6, torchaudio 2.6, and NumPy <2 for Python 3.12; this conflicts with the current Kokoro ONNX NumPy requirement, hence a separate environment. Its installation docs say tested on Debian 11/Python 3.11. A Windows RTX 4060 8 GB trial is plausible but not proven by these docs. [Files](https://huggingface.co/ResembleAI/chatterbox-nano/tree/main), [dependencies](https://raw.githubusercontent.com/resemble-ai/chatterbox/master/pyproject.toml).

## Where Hugging Face helps for free

Downloading these open models from Hugging Face is useful. Existing ZeroGPU demos are free to try but quota-limited: the live documentation currently lists 2 GPU minutes/day without signing in and 5/day for a free account. That is GPU compute time, not audio duration. Queue priority also differs. This is an audition option, not a dependable unattended pipeline for hundreds of thousands of words. [Current ZeroGPU rules](https://huggingface.co/docs/hub/spaces-zerogpu).

Do not advise a new ordinary free Gradio/Docker Space based on old tutorials: current overview says creating compute Spaces requires a paid plan, with a limited free ZeroGPU exception for eligible personal accounts. Nothing about hosting is needed for this audiobook. [Current Spaces overview](https://huggingface.co/docs/hub/spaces-overview).

## Scale and workflow

Using the production agent's supplied 329,879-word source count: at an assumed 150–170 spoken words per minute, the word-for-word edition is approximately 32–37 hours before performance pauses. This is arithmetic, not a measured runtime.

1. Preserve the original books and pin the source revision. Tag a contiguous excerpt with speakers in separate metadata while retaining every original word and attribution.
2. Reassemble the text and compare it with that source range. Permit only documented handling of non-spoken Markdown syntax; reject missing, extra, substituted, duplicated, or reordered words.
3. Render exact source-line auditions, then a short contiguous scene. Use one consistent voice for Aiden's narration and dialogue and distinct voices for the other speakers.
4. Listen against the source, adjust pacing and pronunciation, and select voices from the audible results. Do not add narration, recaps, or vocal ad-libs to fix clarity.
5. Render chapter by chapter with a manifest of source span, speaker, exact text, voice, speed, and filename. Cache segments so a retake does not rerender the book.
6. Assemble tracks in source order, add pauses at existing section breaks, balance volume, and export MP3 plus optional chaptered M4B. Keep WAV masters for later retakes.

Storage arithmetic: 24 kHz mono 16-bit PCM is 172.8 MB/hour, so 32–37 hours is about 5.5–6.4 GB before intermediates. A 96 kbps MP3 is 43.2 MB/hour, or roughly 1.4–1.6 GB. These are estimates from audio format sizes, not software minimum disk specifications.

What the pilot must demonstrate: the cast can be told apart; the slang is intelligible; pauses and delivery make the source easier to follow; every original word is spoken in order; the file plays correctly. Script comparison and listening are separate checks. Neither a matching transcript nor a playable file alone proves a faithful, enjoyable performance.
