"""Prepare pinned chapter sources and import reviewed dialogue assignments."""
from pathlib import Path
import argparse, copy, hashlib, json, re, subprocess, sys

BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
from verify_verbatim import normalize, verify_verbatim
from state import locked_progress
COMMIT='3f16cb8dc89171439167297d744e623d6b16df25'
REPOSITORY='https://github.com/Sodelin/Ten-Toes-Down'
QUOTES=re.compile(r'“[^”]*”|"[^"]*"',re.S)
DIALOGUE_SPAN_EXCEPTIONS={
    # b04-c07: one 16-line rap opens each printed verse line with a quote and
    # closes only the final line. The excerpt hash prevents this exception from
    # applying if the pinned source bytes change.
    '6e482f034a67b1fe68e0298afe132e527239ae06614ce384a01aa2d5d95f0a6e': [
        (
            '"Nigga, I came home, the whole road stood up,',
            'She said baby, all that greatness and you still can\'t leave me alone."',
        ),
    ],
}

def sha(data): return hashlib.sha256(data).hexdigest()
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.part')
    temp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    temp.replace(path)

def source_book(repo,book):
    relative=f'editions/niggatorial-tellings/books/book-{book:02}.md'
    raw=subprocess.check_output(['git','-c','safe.directory='+repo.resolve().as_posix(),'-C',str(repo),'show',COMMIT+':'+relative])
    return relative,raw

def extract(repo,book,chapter):
    relative,raw=source_book(repo,book)
    lines=raw.splitlines(keepends=True)
    headings=[i for i,line in enumerate(lines) if line.startswith(b'## ')]
    h=headings[chapter-1]
    start=h+1
    stop=headings[chapter] if chapter<len(headings) else len(lines)
    while start<stop and not lines[start].strip(): start+=1
    while stop>start and not lines[stop-1].strip(): stop-=1
    excerpt=b''.join(lines[start:stop])
    title=lines[h].decode('utf-8').strip()[3:]
    return relative,raw,excerpt,start+1,stop,title,len(headings)

def get_quotes(text,start_line):
    exception_specs=DIALOGUE_SPAN_EXCEPTIONS.get(sha(text.encode('utf-8')),[])
    explicit=[]
    for opening,closing in exception_specs:
        if text.count(opening)!=1 or text.count(closing)!=1:
            raise ValueError('Pinned dialogue-span exception markers are not unique.')
        start=text.index(opening)
        end=text.index(closing,start)+len(closing)
        explicit.append((start,end))
    explicit.sort()
    if any(left[1]>right[0] for left,right in zip(explicit,explicit[1:])):
        raise ValueError('Pinned dialogue-span exceptions overlap.')

    spans=[]
    position=0
    for start,end in explicit:
        section=text[position:start]
        spans.extend((position+m.start(),position+m.end()) for m in QUOTES.finditer(section))
        rest=QUOTES.sub('',section)
        if any(c in rest for c in '“”"'):
            raise ValueError('Unmatched quotation marks need source review.')
        spans.append((start,end))
        position=end
    section=text[position:]
    spans.extend((position+m.start(),position+m.end()) for m in QUOTES.finditer(section))
    rest=QUOTES.sub('',section)
    if any(c in rest for c in '“”"'):
        raise ValueError('Unmatched quotation marks need source review.')

    rows=[]
    for ordinal,(start,end) in enumerate(sorted(spans),1):
        rows.append({'quote':ordinal,'line':start_line+text[:start].count('\n'),'start':start,'end':end,'text':text[start:end]})
    return rows

def initialize(repo):
    progress_path=BASE/'production'/'progress.json'
    old=json.loads(progress_path.read_text(encoding='utf-8')) if progress_path.exists() else {'source_commit':COMMIT,'chapters':[]}
    existing={row['id']:row for row in old['chapters']}
    jobs=[]
    for book in range(1,7):
        relative,raw=source_book(repo,book)
        count=sum(line.startswith(b'## ') for line in raw.splitlines())
        for chapter in range(1,count+1):
            relative,raw,excerpt,start,end,title,_=extract(repo,book,chapter)
            identity=f'b{book:02}-c{chapter:02}'
            rel=Path(f'chapters/book-{book:02}/chapter-{chapter:02}')
            folder=BASE/rel
            folder.mkdir(parents=True,exist_ok=True)
            source_file=folder/'source-excerpt.md'
            if source_file.exists() and source_file.read_bytes()!=excerpt: raise ValueError('Existing chapter source differs: '+identity)
            source_file.write_bytes(excerpt)
            metadata={'title':'Ten Toes Down: The Niggatorial Tellings','book':book,'chapter':chapter,'chapter_title':title,'repository_url':REPOSITORY,'commit':COMMIT,'repository_path':relative,'source_url':f'{REPOSITORY}/blob/{COMMIT}/{relative}','source_sha256':sha(raw),'excerpt':{'file':'source-excerpt.md','start_line':start,'end_line':end,'sha256':sha(excerpt)},'spoken_text_policy':'Verbatim chapter body. Headings are track metadata. Printed quotation delimiters, paired Markdown emphasis and scene separators are formatting.'}
            save(folder/'source.json',metadata)
            parse_error=None
            try: quote_rows=get_quotes(excerpt.decode('utf-8'),start)
            except ValueError as exc:
                quote_rows=[]
                parse_error=str(exc)
            if not (folder/'assignments.json').exists():
                save(folder/'assignment-template.json',{'chapter_id':identity,'source_commit':COMMIT,'quote_count':len(quote_rows),'assignments':[{'quote':q['quote'],'line':q['line'],'speaker':None,'opening':' '.join(q['text'].split()[:8])} for q in quote_rows]})
            job=existing.get(identity,{'id':identity,'book':book,'chapter':chapter,'status':'needs_cast','path':rel.as_posix(),'release_tag':f'audiobook-book-{book:02}'})
            job.update(title=title,words=len(normalize(excerpt.decode('utf-8')).split()),quotes=len(quote_rows))
            if parse_error: job['parse_error']=parse_error
            jobs.append(job)
    old['chapters']=jobs
    old['source_commit']=COMMIT
    save(progress_path,old)
    print(json.dumps({'chapters':len(jobs),'words':sum(j['words'] for j in jobs),'quote_turns':sum(j['quotes'] for j in jobs),'quotation_review':[j['id'] for j in jobs if j.get('parse_error')]}))

def prepare(repo,book,chapter,assignments,reviewer):
    identity=f'b{book:02}-c{chapter:02}'
    with locked_progress(BASE/'production'/'progress.json') as progress:
        status=next(j for j in progress['chapters'] if j['id']==identity)['status']
        if status not in ['needs_cast','failed']:
            raise ValueError('Chapter is already queued or published; do not replace its files in place.')
    folder=BASE/f'chapters/book-{book:02}/chapter-{chapter:02}'
    meta=json.loads((folder/'source.json').read_text(encoding='utf-8'))
    text=(folder/'source-excerpt.md').read_text(encoding='utf-8')
    quotes=get_quotes(text,meta['excerpt']['start_line'])
    given=json.loads(assignments.read_text(encoding='utf-8-sig'))
    mapping={row['quote']:row for row in given['assignments']}
    if len(mapping)!=len(given['assignments']) or set(mapping)!=set(range(1,len(quotes)+1)):
        raise ValueError('Each quotation requires exactly one reviewed assignment.')
    cast=json.loads((BASE/'cast.json').read_text(encoding='utf-8'))
    for q in quotes:
        a=mapping[q['quote']]
        if a.get('line')!=q['line']: raise ValueError('Assignment source line mismatch: '+str(q['quote']))
        if a.get('speaker') not in cast: raise ValueError('Uncast speaker: '+str(a.get('speaker')))
    rows=[]
    cutoff=0
    if book==1 and chapter==1:
        prefix=json.loads((BASE/'pilot'/'source.json').read_text(encoding='utf-8'))['excerpt']
        prefix_lines=prefix['end_line']-meta['excerpt']['start_line']+1
        cutoff=len(''.join(text.splitlines(keepends=True)[:prefix_lines]))
        pilot=json.loads((BASE/'pilot'/'script.json').read_text(encoding='utf-8'))
        if normalize(text[:cutoff])!=normalize(' '.join(r['text'] for r in pilot)): raise ValueError('Pilot prefix mismatch')
        rows=copy.deepcopy(pilot)

    def emit(speaker,raw,line):
        # Narration paragraph splits and short chunks keep speech below model limits.
        for paragraph in re.split(r'\n\s*\n',raw):
            if paragraph.strip()=='***':
                if rows: rows[-1]['pause_ms']=650
                continue
            clean=normalize(paragraph)
            if not clean: continue
            words=clean.split()
            for offset in range(0,len(words),65):
                value=' '.join(words[offset:offset+65])
                number=len(rows)+1
                uid=f'{number:03}' if book==1 and chapter==1 else f'{identity}-u{number:04}'
                rows.append({'id':uid,'speaker':speaker,'text':value,'pause_ms':180 if speaker=='AIDEN' else 200,'source_line':line})
    position=cutoff
    for q in quotes:
        if q['end']<=cutoff: continue
        if q['start']<cutoff: raise ValueError('Pilot boundary intersects quotation')
        emit('AIDEN',text[position:q['start']],meta['excerpt']['start_line']+text[:position].count('\n'))
        emit(mapping[q['quote']]['speaker'],q['text'],q['line'])
        position=q['end']
    emit('AIDEN',text[position:],meta['excerpt']['start_line']+text[:position].count('\n'))
    rows[-1]['pause_ms']=800
    save(folder/'script.json',rows)
    report=verify_verbatim(folder/'script.json')
    save(folder/'source-check.json',report)
    save(folder/'assignments.json',{'source_commit':COMMIT,'reviewer':reviewer,'quote_count':len(quotes),'assignments':list(mapping.values())})
    transcript='# '+meta['chapter_title']+'\n\nVerbatim chapter script. Speaker labels and source locations are production metadata, not spoken additions.\n\n'
    transcript+='\n\n'.join('**'+r['id']+' · '+r['speaker']+'**\n\n'+r['text'] for r in rows)+'\n'
    (folder/'script.md').write_text(transcript,encoding='utf-8',newline='\n')
    progress_path=BASE/'production'/'progress.json'
    with locked_progress(progress_path) as progress:
        job=next(j for j in progress['chapters'] if j['id']==identity)
        if job['status'] in ['rendering','published']: raise ValueError('Do not replace an active or published chapter in place.')
        job.update(status='ready',speaker_review=reviewer,segments=len(rows),quotes=len(quotes),words=report['spoken_words'],source_check=report['status'])
        job.pop('parse_error',None)
    print(json.dumps({'chapter':identity,'segments':len(rows),'voices':len(report['speakers']),'words':report['spoken_words'],'status':'ready'}))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--init-all',action='store_true')
    p.add_argument('--book',type=int)
    p.add_argument('--chapter',type=int)
    p.add_argument('--assignments',type=Path)
    p.add_argument('--reviewer',default='agent-reviewed')
    a=p.parse_args()
    if a.init_all: initialize(a.repo)
    else:
        if not all([a.book,a.chapter,a.assignments]): p.error('Provide --book, --chapter and --assignments')
        prepare(a.repo,a.book,a.chapter,a.assignments,a.reviewer)

if __name__=='__main__': main()
