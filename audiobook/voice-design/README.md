# Aiden and Tank: directed synthetic voices

[Aiden audition](aiden-voice.mp3) · [Tank — deeper take](tank-voice-deeper.mp3)

These voices were generated from performance descriptions with **Qwen3-TTS VoiceDesign**. Aiden's current take is held after the listener singled out Tank for further changes. Tank was revised toward a deeper, fuller bass voice. The user then asked to stop auditioning and finish. These voices are selected for the delivered pilot; future feedback can address specific retakes.

Aiden reads two consecutive narration paragraphs from Book I, chapter 1. Tank reads his exact dialogue from source lines 149 and 153, with the crowd action between them omitted for the isolated audition. The scene recording uses the entire selected excerpt in its original order. No audition wording was invented. `directions.json` records the exact text, source locations, seeds and descriptions; directions are never spoken as book text.

## What ran here

The VoiceDesign model ran successfully on a Windows laptop with an RTX 4060 8 GB GPU, Python 3.12, PyTorch 2.6.0 CUDA 12.4, BF16 and PyTorch SDPA. Aiden's reference is 15.92 seconds and took 30.50 seconds to render. The final Tank reference is 9.44 seconds and took 18.94 seconds. Peak allocated GPU memory for these auditions was approximately 4.36 GiB. These are observed short-sample results, not a minimum specification or a full-book benchmark.

No actor or other real person's recording was used. Both reference WAVs were created by the model. They are included here so later lines can reuse the same generated identities instead of designing a different voice on every turn. A seed alone cannot guarantee identical results across hardware or dependency changes.

The [official VoiceDesign model](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign) occupies approximately 4.52 GB. The [Base 0.6B model](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base) used to carry a designed voice across lines adds approximately 2.52 GB. Runtime packages need additional disk space. Both models run locally; no account, hosted GPU, paid API or subscription is used. Model files are not committed to GitHub.

## Reproduce

From the parent `audiobook` folder, create a separate environment from the CPU Kokoro baseline:

```powershell
py -3.12 -m venv .venv-qwen
.\.venv-qwen\Scripts\python.exe -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
.\.venv-qwen\Scripts\python.exe -m pip install -r voice-design/requirements.txt
.\.venv-qwen\Scripts\python.exe voice-design/download_model.py --out models/qwen-design
.\.venv-qwen\Scripts\python.exe voice-design/design_voices.py --model models/qwen-design
```

The download helper pins the model revision and verifies file sizes and publisher-listed hashes before writing a completion manifest. Rendering uses offline mode. FlashAttention and a SoX executable were not installed for this tested 12 Hz path; the package emits startup notices about them, but the audition generation completed with SDPA.

Regenerating references replaces the current designed identities. To keep the delivered voices, use the included reference WAVs and skip `design_voices.py`.

```powershell
.\.venv-qwen\Scripts\python.exe voice-design/download_model.py --repo Qwen/Qwen3-TTS-12Hz-0.6B-Base --revision 5d83992436eae1d760afd27aff78a71d676296fc --out models/qwen-base
.\.venv-qwen\Scripts\python.exe voice-design/render_scene.py --model models/qwen-base --cache cache/qwen-takes
.\.venv\Scripts\python.exe render.py --overrides cache/qwen-takes/index.json --out pilot/funeral-new-voices --title "The Funeral - verbatim, new Aiden and Tank"
```

The last command uses the separate Kokoro environment from the parent README for the remaining four roles and final assembly. `render_scene.py` checks the source text, model inventory and reference hashes, then caches exact Aiden/Tank turns. The assembler rejects takes belonging to a different script, speaker or text. All spoken source lines stay in order.

This follows Qwen's documented [design-then-reuse workflow](https://github.com/QwenLM/Qwen3-TTS#voice-design-then-clone). Manifests record which model, voice reference, settings and generated files were actually used. Successful source and file checks do not certify every spoken syllable or the performance; listening review remains necessary.
