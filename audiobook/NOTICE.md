# Audio model and dependency notices

## Story source and performance

This production targets a **word-for-word reading of The Niggatorial Tellings**, pinned at commit `3f16cb8dc89171439167297d744e623d6b16df25` of [Sodelin/Ten-Toes-Down](https://github.com/Sodelin/Ten-Toes-Down/tree/3f16cb8dc89171439167297d744e623d6b16df25/editions/niggatorial-tellings). The original novels remain unchanged. Their existing authorship and source record remain in force.

Speaker assignments, pauses, voice settings, and rendering code are production material. They add no words to the spoken book. Model/software licensing does not relabel the story or characters as open-source software. Source verification and audio listening are separate checks: a correct script does not establish a flawless performance.

## Kokoro and existing local audio

The existing generated audio uses **Kokoro-82M**, whose original model card specifies Apache-2.0 licensing. The **kokoro-onnx** wrapper specifies MIT licensing. The package downloads the ONNX model and presets from the wrapper maintainer's release; model weights are not redistributed inside this audio directory.

- [Kokoro-82M model card](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro-82M voice notes](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)
- [kokoro-onnx project and license](https://github.com/thewh1teagle/kokoro-onnx)
- [ONNX Runtime license](https://github.com/microsoft/onnxruntime/blob/main/LICENSE)
- [SoundFile](https://github.com/bastibe/python-soundfile)
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)
- [FFmpeg license information](https://ffmpeg.org/legal.html)

Voice identifiers describe bundled synthetic presets. No personal voice recording was uploaded, and no named actor's voice was requested or cloned for the Kokoro pilot.

## Qwen voice-design experiment

**Qwen3-TTS-12Hz-1.7B-VoiceDesign** is being evaluated for new synthetic-voice auditions. Its official model card lists **Apache-2.0**. This experiment uses written voice descriptions, not a real person's recording. It generated the delivered Aiden and Tank reference voices locally. Qwen3-TTS-12Hz-0.6B-Base reuses those original synthetic references for the scene. The Base model also lists Apache-2.0: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base. The cast is a production choice for this pilot, not a claim of perfect acting. [Official Qwen VoiceDesign model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign)

## Build records

`models.json` records SHA-256 values measured from downloaded assets. These support repeatable integrity checks; they are not independent publisher signatures. Render manifests record the environment and technical audio checks. A successful technical check is not a listening review.
