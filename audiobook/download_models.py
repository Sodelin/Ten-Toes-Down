"""Download the two free, pinned release assets. No account or paid API."""
from pathlib import Path
import argparse, hashlib, json, urllib.request

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--directory',type=Path,default=Path(__file__).parent/'models')
    a=p.parse_args()
    manifest=json.loads((Path(__file__).parent/'models.json').read_text(encoding='utf-8'))
    a.directory.mkdir(parents=True,exist_ok=True)
    for key in ['model','voices']:
        item=manifest[key]
        dest=a.directory/item['filename']
        if dest.exists() and digest(dest)==item['sha256']:
            print('Verified existing',dest.name,flush=True)
            continue
        partial=dest.with_suffix(dest.suffix+'.part')
        print('Downloading',item['filename'],flush=True)
        request=urllib.request.Request(item['url'],headers={'User-Agent':'Ten-Toes-Down-Audio/1.0'})
        with urllib.request.urlopen(request,timeout=120) as src, partial.open('wb') as out:
            while data:=src.read(1024*1024): out.write(data)
        if digest(partial)!=item['sha256']:
            raise RuntimeError('Model checksum mismatch; partial file retained for inspection: '+str(partial))
        partial.replace(dest)
        print('Verified',dest.name,flush=True)

if __name__=='__main__': main()
