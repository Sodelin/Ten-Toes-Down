"""Publish verified chapter recordings as GitHub release assets."""
from pathlib import Path
import argparse, copy, hashlib, json, shutil, subprocess, sys, textwrap
from datetime import datetime,timezone
from state import locked_progress
from worker import resolve_config, verify_result

REPO='Sodelin/Ten-Toes-Down'
URL='https://github.com/'+REPO

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def run(args,okay=(0,)):
    r=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode not in okay: raise RuntimeError(r.stderr[-2500:] or r.stdout[-2500:])
    return r

def git(repo,*args,okay=(0,)):
    return run(['git','-c','safe.directory='+repo.as_posix(),'-C',repo,*args],okay)

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def write_index(package,progress):
    lines=['# Listen to The Niggatorial Tellings','',
           'Chapter recordings are being produced in book order, with a consistent cast and verbatim source scripts. This page distinguishes published audio from chapters still in preparation.','',
           '[Three-minute cast pilot](pilot/funeral-new-voices.mp3) · [Production workflow](production/README.md) · [Cast directory](production/cast-inventory.md)','']
    for book in range(1,7):
        jobs=[j for j in progress['chapters'] if j['book']==book]
        done=[j for j in jobs if j.get('publication')]
        lines += [f'## Book {book} — {len(done)}/{len(jobs)} recordings uploaded','', '| Chapter | Recording | Script |','|---|---|---|']
        playlist=['#EXTM3U']
        for job in jobs:
            pub=job.get('publication')
            audio=f"[MP3 · {pub['duration_seconds']/60:.1f} min]({pub['audio_url']})" if pub else job['status'].replace('_',' ')
            script=f"[Read]({job['path']}/script.md)" if (package/job['path']/'script.md').exists() else 'Awaiting speaker pass'
            lines.append(f"| {job['title'].replace('|','/')} | {audio} | {script} |")
            if pub: playlist += [f"#EXTINF:{round(pub['duration_seconds'])},{job['title']}",pub['audio_url']]
        if done:
            playlist_path=package/f'books/book-{book:02}.m3u'
            playlist_path.parent.mkdir(parents=True,exist_ok=True)
            playlist_path.write_text('\n'.join(playlist)+'\n',encoding='utf-8',newline='\n')
            lines += ['',f'[Book {book} playlist](books/book-{book:02}.m3u)','']
        lines += ['']
    lines += ['Source matching and audio integrity are checked automatically. Published does not mean a human has listened to every syllable. The source novels are unchanged.','']
    (package/'LISTEN.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')

def sync_package(package,repo):
    target=repo/'audiobook'
    for path in package.rglob('*'):
        if not path.is_file(): continue
        rel=path.relative_to(package)
        if '__pycache__' in rel.parts or path.suffix in ['.pyc','.part','.lock']: continue
        if rel.parts[0]=='chapters' and path.suffix in ['.mp3','.wav']: continue
        if rel.parts[0]=='pilot' and path.suffix=='.wav': continue
        if path.name=='local-config.json': continue
        destination=target/rel
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,destination)

def stamp(seconds):
    millis=round(seconds*1000)
    h,millis=divmod(millis,3600000); m,millis=divmod(millis,60000); s,ms=divmod(millis,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def publish(config,identity):
    package,repo=config['package_root'],config['repo_root']
    progress_path=package/'production/progress.json'
    progress=json.loads(progress_path.read_text(encoding='utf-8'))
    job=next(j for j in progress['chapters'] if j['id']==identity)
    folder=(package/job['path']).resolve()
    if not folder.is_relative_to(package): raise ValueError('Chapter path leaves package')
    verify_result(folder/'script.json',folder/'audio',job['words'])
    report=json.loads((folder/'audio.manifest.json').read_text(encoding='utf-8'))
    if report.get('samples_at_full_scale')!=0: raise ValueError('Clipped master requires a retake')
    if report.get('warnings'): raise ValueError('Audio warnings require review before publication')
    if not report['verbatim_source_check'].get('status','').startswith('PASS'): raise ValueError('Source check did not pass')
    subtitle=[]
    for n,row in enumerate(report['timeline'],1):
        subtitle += [str(n),stamp(row['start_seconds'])+' --> '+stamp(row['start_seconds']+row['speech_seconds']),textwrap.fill(row['text'],width=70),'']
    (folder/'captions.srt').write_text('\n'.join(subtitle),encoding='utf-8',newline='\n')
    staging=config['log_root']/'publish-assets'/identity
    staging.mkdir(parents=True,exist_ok=True)
    asset_name=f"book-{job['book']:02}-chapter-{job['chapter']:02}"
    assets=[]
    for source,suffix in [('audio.mp3','.mp3'),('audio.manifest.json','.manifest.json'),('captions.srt','.srt')]:
        dest=staging/(asset_name+suffix)
        shutil.copy2(folder/source,dest); assets.append(dest)
    tag=job['release_tag']
    existing=run(['gh','release','view',tag,'--repo',REPO,'--json','assets,url'],okay=(0,1))
    if existing.returncode:
        if 'not found' not in (existing.stderr+existing.stdout).lower(): raise RuntimeError(existing.stderr)
        notes=staging/'release-notes.md'
        notes.write_text(f"Book {job['book']} of The Niggatorial Tellings, recorded chapter by chapter with synthetic character voices.\n\nThe book is still in production. Source scripts remain word for word. Recordings pass automated source and audio-integrity checks; human listening review is tracked separately.\n\n[Chapter index]({URL}/blob/main/audiobook/LISTEN.md)\n",encoding='utf-8',newline='\n')
        head=git(repo,'rev-parse','HEAD').stdout.strip()
        run(['gh','release','create',tag,'--repo',REPO,'--target',head,'--title',f"The Niggatorial Tellings — Book {job['book']} audiobook",'--notes-file',notes,'--prerelease','--latest=false'])
    api=['gh','api',f'repos/{REPO}/releases/tags/{tag}']
    release=json.loads(run(api).stdout)
    known={a['name']:a for a in release['assets']}
    for asset in assets:
        old=known.get(asset.name)
        expected='sha256:'+sha(asset)
        if old:
            if old.get('digest')!=expected: raise ValueError('Existing asset differs; explicit versioned retake required: '+asset.name)
        else: run(['gh','release','upload',tag,asset,'--repo',REPO])
    release=json.loads(run(api).stdout)
    known={a['name']:a for a in release['assets']}
    for asset in assets:
        remote=known[asset.name]
        if remote.get('digest')!='sha256:'+sha(asset) or remote['size']!=asset.stat().st_size: raise ValueError('Uploaded asset hash/size mismatch')
    publication={'audio_url':known[asset_name+'.mp3']['browser_download_url'],'release_url':release['html_url'],'audio_sha256':sha(folder/'audio.mp3'),'duration_seconds':report['duration_seconds'],'uploaded_at':datetime.now(timezone.utc).isoformat(),'checks':'verbatim input, audio integrity and remote asset hashes passed','listening_review':'pending'}
    save(folder/'publication.json',publication)
    with locked_progress(progress_path) as progress:
        current=next(j for j in progress['chapters'] if j['id']==identity)
        current['publication']=publication
    # Preserve unrelated remote changes; never force-push or overwrite conflicting work.
    git(repo,'fetch','origin','main')
    git(repo,'merge','--ff-only','origin/main')
    progress=json.loads(progress_path.read_text(encoding='utf-8'))
    snapshot=copy.deepcopy(progress)
    next(j for j in snapshot['chapters'] if j['id']==identity)['status']='published'
    write_index(package,snapshot)
    sync_package(package,repo)
    save(repo/'audiobook/production/progress.json',snapshot)
    git(repo,'add','--','audiobook')
    git(repo,'diff','--cached','--check')
    changes=git(repo,'diff','--cached','--quiet',okay=(0,1))
    if changes.returncode: git(repo,'commit','-m',f"Publish audiobook {identity}: {job['title']}")
    git(repo,'push','origin','main')
    print(json.dumps({'chapter':identity,'publication':publication}))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,required=True); p.add_argument('--chapter',required=True)
    a=p.parse_args(); publish(resolve_config(a.config),a.chapter)

if __name__=='__main__': main()
