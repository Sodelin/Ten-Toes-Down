"""Local, resumable multi-voice TTS. No network is used during rendering."""
from pathlib import Path
import argparse, hashlib, importlib.metadata, json, math, re, subprocess, time
import numpy as np
import onnxruntime as ort
import soundfile as sf
import imageio_ffmpeg
from kokoro_onnx import Kokoro
from verify_verbatim import verify_verbatim

BASE=Path(__file__).resolve().parent

def sha_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def run_ffmpeg(args):
    result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-nostdin',*args],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if result.returncode: raise RuntimeError(result.stderr[-5000:])
    return result.stderr

def load_script(path,cast):
    rows=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(rows,list) or not rows: raise ValueError('Script must be a nonempty JSON array.')
    seen=set()
    for r in rows:
        uid=r.get('id')
        if not isinstance(uid,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',uid) or uid in seen: raise ValueError('Invalid/duplicate segment ID: '+str(uid))
        seen.add(uid)
        if r.get('speaker') not in cast: raise ValueError('Unmapped speaker: '+str(r.get('speaker')))
        if not isinstance(r.get('text'),str) or not r['text'].strip(): raise ValueError('Empty text: '+uid)
        if not isinstance(r.get('pause_ms'),int) or not 0<=r['pause_ms']<=5000: raise ValueError('Invalid pause: '+uid)
        v=cast[r['speaker']]
        if not .5<=v['speed']<=2: raise ValueError('Voice speed out of supported range.')
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--script',type=Path,default=BASE/'pilot'/'script.json')
    p.add_argument('--cast',type=Path,default=BASE/'cast.json')
    p.add_argument('--overrides',type=Path,help='Verified generated voice takes from voice-design/render_scene.py.')
    p.add_argument('--models',type=Path,default=BASE/'models')
    p.add_argument('--cache',type=Path,default=BASE/'cache')
    p.add_argument('--out',type=Path,default=BASE/'pilot'/'funeral-pilot')
    p.add_argument('--threads',type=int,default=4)
    p.add_argument('--title',default=None,help='Audio track title; defaults to the output filename.')
    p.add_argument('--album',default='The Niggatorial Tellings - Listening Edition')
    p.add_argument('--validate-only',action='store_true')
    p.add_argument('--cd',action='store_true',help='Also export 44.1 kHz 16-bit stereo WAV; does not burn a disc.')
    a=p.parse_args()
    cast=json.loads(a.cast.read_text(encoding='utf-8'))
    rows=load_script(a.script,cast)
    verification=verify_verbatim(a.script)
    if a.validate_only:
        print(json.dumps(verification,indent=2))
        return
    overrides={}
    override_rows={}
    if a.overrides:
        overrides=json.loads(a.overrides.read_text(encoding='utf-8'))
        if overrides['source_script_sha256']!=sha_file(a.script): raise ValueError('Voice takes belong to a different script.')
        override_rows=overrides['segments']
        if set(override_rows)-{r['id'] for r in rows}: raise ValueError('Unknown segment IDs in voice takes.')
    t0=time.perf_counter()
    expected=json.loads((BASE/'models.json').read_text(encoding='utf-8'))
    model=a.models/expected['model']['filename']
    voices=a.models/expected['voices']['filename']
    hashes={'model':sha_file(model),'voices':sha_file(voices)}
    for key in hashes:
        if hashes[key]!=expected[key]['sha256']: raise ValueError('Unexpected '+key+' checksum. Use download_models.py.')
    opts=ort.SessionOptions()
    opts.intra_op_num_threads=max(1,a.threads)
    opts.inter_op_num_threads=1
    session=ort.InferenceSession(str(model),sess_options=opts,providers=['CPUExecutionProvider'])
    engine=Kokoro.from_session(session,str(voices))
    for r in rows:
        if cast[r['speaker']]['voice'] not in engine.voices: raise ValueError('Unknown voice preset for '+r['speaker'])
    a.cache.mkdir(parents=True,exist_ok=True)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    sr=24000
    pieces=[np.zeros(int(sr*.15),dtype=np.float32)]
    timeline=[]
    cursor=.15
    warnings=[]
    versions={n:importlib.metadata.version(n) for n in ['kokoro-onnx','onnxruntime','numpy','phonemizer','espeakng-loader','soundfile']}
    for i,r in enumerate(rows):
        voice=cast[r['speaker']]
        text=r.get('tts_text') or r['text']
        settings={'text':text,'voice':voice['voice'],'speed':voice['speed'],'lang':'en-us','hashes':hashes,'versions':versions,'trim':True}
        key=hashlib.sha256(json.dumps(settings,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        cached=a.cache/(key+'.wav')
        start=time.perf_counter()
        hit=cached.exists()
        override=override_rows.get(r['id'])
        if override:
            if override['speaker']!=r['speaker'] or override['text']!=r['text']: raise ValueError('Voice take text/speaker mismatch: '+r['id'])
            take_root=a.overrides.resolve().parent
            cached=(take_root/override['wav']).resolve()
            if not cached.is_relative_to(take_root): raise ValueError('Voice take path leaves its folder.')
            if sha_file(cached)!=override['sha256']: raise ValueError('Voice take checksum mismatch: '+r['id'])
            sound,rate=sf.read(cached,dtype='float32')
            voice={'voice':override['voice'],'speed':override.get('speed',1.0)}
            key=override['sha256']
            hit=True
        elif hit:
            try:
                sound,rate=sf.read(cached,dtype='float32')
                if not len(sound) or not np.isfinite(sound).all(): hit=False
            except (RuntimeError,ValueError):
                hit=False
        if not hit:
            # Kokoro splits phonemes internally. Keep source turns intact and short.
            sound,rate=engine.create(text,voice=voice['voice'],speed=voice['speed'],lang='en-us',trim=True)
            sound=np.asarray(sound,dtype=np.float32).reshape(-1)
            if not np.isfinite(sound).all() or not len(sound): raise ValueError('Invalid samples: '+r['id'])
            temporary=cached.with_suffix('.part.wav')
            sf.write(temporary,sound,rate,subtype='FLOAT')
            temporary.replace(cached)
        if rate!=sr or sound.ndim!=1: raise ValueError('Unexpected sample format: '+r['id'])
        if not len(sound) or not np.isfinite(sound).all(): raise ValueError('Invalid cached samples: '+r['id'])
        duration=len(sound)/sr
        peak=float(np.max(np.abs(sound)))
        rms=float(np.sqrt(np.mean(sound.astype(np.float64)**2)))
        words=len(text.split())
        wpm=words*60/duration
        if duration<.08 or rms<.0001: raise ValueError('Empty/near-silent speech: '+r['id'])
        if peak>=1: warnings.append({'id':r['id'],'issue':'raw peak at or above full scale','peak':peak})
        if words>=5 and not 75<wpm<400: warnings.append({'id':r['id'],'issue':'unusual word-rate estimate','words_per_minute':round(wpm,1)})
        # Very short boundary fades suppress clicks without changing a voice's pitch.
        fade=min(int(sr*.004),len(sound)//2)
        sound=sound.copy()
        if fade:
            sound[:fade]*=np.linspace(0,1,fade)
            sound[-fade:]*=np.linspace(1,0,fade)
        pieces.append(sound)
        pause=r['pause_ms']/1000
        pieces.append(np.zeros(round(sr*pause),dtype=np.float32))
        timeline.append({'id':r['id'],'speaker':r['speaker'],'voice':voice['voice'],'speed':voice['speed'],'text':r['text'],'start_seconds':round(cursor,4),'speech_seconds':round(duration,4),'pause_ms':r['pause_ms'],'cache_key':key,'raw_peak':peak,'rms':rms,'render_seconds':round(time.perf_counter()-start,3),'cached':hit})
        cursor+=duration+pause
        print(f'{i+1:02}/{len(rows)} {r["speaker"]:8} {duration:5.2f}s'+(' cached' if hit else ''),flush=True)
    raw=np.concatenate(pieces)
    raw_path=a.cache/(a.out.name+'.raw.wav')
    sf.write(raw_path,raw,sr,subtype='FLOAT')
    # Two-pass EBU loudness normalization; a spoken-word pilot target, not a distribution certification.
    first=run_ffmpeg(['-i',str(raw_path),'-af','loudnorm=I=-18:TP=-2:LRA=11:print_format=json','-f','null','-'])
    measurement=json.loads(re.findall(r'\{\s*"input_i".*?\}',first,re.S)[-1])
    filt='loudnorm=I=-18:TP=-2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=json'.format(**measurement)
    master=a.out.with_suffix('.wav')
    last=run_ffmpeg(['-y','-i',str(raw_path),'-af',filt,'-ar','24000','-ac','1','-c:a','pcm_s16le',str(master)])
    mp3=a.out.with_suffix('.mp3')
    title=a.title or a.out.name.replace('-',' ')
    run_ffmpeg(['-y','-i',str(master),'-c:a','libmp3lame','-b:a','128k','-id3v2_version','3','-metadata','title='+title,'-metadata','artist=Codex; creative direction by Nolan','-metadata','album='+a.album,str(mp3)])
    if a.cd:
        run_ffmpeg(['-y','-i',str(master),'-ar','44100','-ac','2','-c:a','pcm_s16le',str(a.out.with_suffix('.cd.wav'))])
    # Confirm the export decodes and capture actual samples rather than inferring duration from bytes.
    run_ffmpeg(['-v','error','-i',str(mp3),'-f','null','-'])
    samples,actual_sr=sf.read(master,dtype='float32')
    report={'status':'technical checks complete; human listening review pending','engine':versions,'provider':'CPUExecutionProvider','source_script_sha256':sha_file(a.script),'cast_sha256':sha_file(a.cast),'model_sha256':hashes['model'],'voices_sha256':hashes['voices'],'segments':len(rows),'speakers':sorted({r['speaker'] for r in rows}),'spoken_words':sum(len(r['text'].split()) for r in rows),'duration_seconds':len(samples)/actual_sr,'sample_rate':actual_sr,'master_peak':float(np.max(np.abs(samples))),'samples_at_full_scale':int(np.sum(np.abs(samples)>=.99999)),'mp3_decodes':True,'runtime_seconds':round(time.perf_counter()-t0,2),'loudness_first_pass':measurement,'loudness_second_pass':json.loads(re.findall(r'\{\s*"input_i".*?\}',last,re.S)[-1]),'warnings':warnings,'timeline':timeline}
    report['verbatim_source_check']=verification
    if overrides:
        report['replacement_voice_engine']=overrides['engine']
        report['replacement_segment_ids']=list(override_rows)
    a.out.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='timeline'},indent=2),flush=True)

if __name__=='__main__': main()
