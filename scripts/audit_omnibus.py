#!/usr/bin/env python3
"""Check assembly completeness and flag exact long repeated passages for review."""
from pathlib import Path
from collections import defaultdict
import re,json,argparse
p=argparse.ArgumentParser();p.add_argument('manuscript',type=Path);a=p.parse_args()
s=a.manuscript.read_text();assert not [ord(c) for c in s if ord(c)<32 and c not in '\n\t\r'];books=re.findall(r'^# (BOOK [IVX]+:[^\n]+)\n(.*?)(?=^# BOOK |\Z)',s,re.M|re.S)
assert len(books)==6,len(books)
seen=defaultdict(list);report=[]
for bi,(title,body) in enumerate(books,1):
 chapters=re.findall(r'^## (\d+)\. ([^\n]+)\n(.*?)(?=^## |\Z)',body,re.M|re.S)
 assert len(chapters)>=16,(title,len(chapters))
 assert [int(x[0]) for x in chapters]==list(range(1,len(chapters)+1))
 for n,t,text in chapters:
  assert len(text.split())>700,(title,n,'too short')
  for block in re.split(r'\n\s*\n',text):
   norm=' '.join(block.split())
   if len(norm.split())>=70:seen[norm].append((bi,int(n)))
 report.append({'book':bi,'title':title,'chapters':len(chapters),'words':len(body.split())})
dups=[{'locations':loc,'words':len(text.split()),'opening':text[:150]} for text,loc in seen.items() if len(loc)>1]
print(json.dumps({'books':report,'words':len(s.split()),'chapters':sum(x['chapters'] for x in report),'exact_long_duplicates':dups},indent=2))
