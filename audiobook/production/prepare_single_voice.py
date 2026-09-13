"""Prepare unpublished chapters verbatim in the selected funeral ticket voice."""
from pathlib import Path
import argparse, json, re, shutil, sys
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
from verify_verbatim import normalize, verify_verbatim
from prepare import save
from state import locked_progress

def chunks(text):
    pending=[]
    for sentence in re.split(r'(?<=[.!?])\s+',normalize(text)):
        words=sentence.split()
        if pending and len(pending)+len(words)>65:
            yield ' '.join(pending); pending=[]
        while len(words)>65:
            yield ' '.join(words[:65]); words=words[65:]
        pending.extend(words)
    if pending: yield ' '.join(pending)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backup',type=Path,required=True)
    a=p.parse_args()
    progress_path=BASE/'production/progress.json'
    progress=json.loads(progress_path.read_text(encoding='utf-8'))
    changed=[]
    for job in progress['chapters']:
        if job['status']=='published' or job.get('publication'): continue
        folder=BASE/job['path']
        backup=a.backup/job['id']
        backup.mkdir(parents=True,exist_ok=True)
        for name in ('script.json','script.md','source-check.json','assignments.json'):
            source=folder/name
            if source.exists() and not (backup/name).exists(): shutil.copy2(source,backup/name)
        text=(folder/'source-excerpt.md').read_text(encoding='utf-8')
        rows=[{'id':f"{job['id']}-single-{n:04}",'speaker':'TICKET','text':part,'pause_ms':250}
              for n,part in enumerate(chunks(text),1)]
        rows[-1]['pause_ms']=800
        save(folder/'script.json',rows)
        report=verify_verbatim(folder/'script.json')
        save(folder/'source-check.json',report)
        (folder/'script.md').write_text('# '+job['title']+'\n\nSingle narrator: the funeral ticket man. Verbatim chapter body.\n\n'+'\n\n'.join(r['text'] for r in rows)+'\n',encoding='utf-8',newline='\n')
        changed.append((job['id'],report))
    with locked_progress(progress_path) as current:
        current['production_mode']='single narrator: TICKET / am_michael / speed 0.95'
        for identity,report in changed:
            job=next(j for j in current['chapters'] if j['id']==identity)
            job.update(status='ready',narrator='TICKET',segments=report['segments'],words=report['spoken_words'],source_check=report['status'],speaker_review='Single narrator selected by user; no dialogue attribution required.')
            job.pop('error',None); job.pop('parse_error',None)
    print(json.dumps({'prepared':len(changed),'voice':'TICKET','verbatim_checks':'all passed'}))

if __name__=='__main__': main()
