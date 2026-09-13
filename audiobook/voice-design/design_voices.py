"""Audition original synthetic character voices using local Qwen VoiceDesign."""
from pathlib import Path
import argparse, hashlib, importlib.metadata, json, os, subprocess, time

os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--roles',nargs='+',default=['AIDEN','TANK'])
    a=p.parse_args()
    import torch, numpy as np, soundfile as sf, imageio_ffmpeg
    from qwen_tts import Qwen3TTSModel
    cast=json.loads((Path(__file__).parent/'directions.json').read_text(encoding='utf-8'))
    if any(role not in cast for role in a.roles): raise ValueError('Unknown role')
    a.out.mkdir(parents=True,exist_ok=True)
    if not torch.cuda.is_available(): raise RuntimeError('This tested configuration requires an NVIDIA CUDA GPU.')
    torch.set_num_threads(4)
    torch.cuda.reset_peak_memory_stats()
    model=Qwen3TTSModel.from_pretrained(str(a.model.resolve()),device_map='cuda:0',dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True)
    versions={name:importlib.metadata.version(name) for name in ['torch','torchaudio','qwen-tts','transformers','accelerate','soundfile']}
    for role in a.roles:
        item=cast[role]
        torch.manual_seed(item['seed'])
        start=time.perf_counter()
        with torch.inference_mode():
            waves,sr=model.generate_voice_design(text=item['text'],language='English',instruct=item['direction'],max_new_tokens=1024)
        sound=np.asarray(waves[0],dtype=np.float32)
        if sound.ndim!=1 or not len(sound) or not np.isfinite(sound).all(): raise ValueError('Invalid generated audio')
        # Preserve a clean reference for later reuse of this synthetic voice.
        raw=a.out/(role.lower()+'-reference.wav')
        sf.write(raw,sound,sr,subtype='FLOAT')
        mp3=a.out/(role.lower()+'-voice.mp3')
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
        result=subprocess.run([ffmpeg,'-hide_banner','-nostdin','-y','-i',str(raw),'-af','loudnorm=I=-18:TP=-2:LRA=11','-ar','24000','-ac','1','-c:a','libmp3lame','-b:a','128k','-metadata','title='+role.title()+' - designed voice audition',str(mp3)],capture_output=True,text=True)
        if result.returncode: raise RuntimeError(result.stderr[-4000:])
        checked=subprocess.run([ffmpeg,'-v','error','-i',str(mp3),'-f','null','-'],capture_output=True,text=True)
        if checked.returncode: raise RuntimeError(checked.stderr)
        report={'role':role,**item,'model':'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign','model_revision':'5ecdb67327fd37bb2e042aab12ff7391903235d3','versions':versions,'attention':'sdpa','dtype':'bfloat16','device':torch.cuda.get_device_name(0),'sample_rate':sr,'duration_seconds':len(sound)/sr,'render_seconds':round(time.perf_counter()-start,2),'peak_allocated_gpu_bytes':torch.cuda.max_memory_allocated(),'reference_sha256':digest(raw),'mp3_sha256':digest(mp3),'mp3_decodes':True,'status':'Generated audition; human performance and spoken-word review pending.'}
        (a.out/(role.lower()+'.manifest.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__': main()
