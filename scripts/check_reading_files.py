#!/usr/bin/env python3
"""Verify PDF navigation/text endpoints and EPUB structure against the manuscript."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZIP_STORED
from xml.etree import ElementTree as ET
from pypdf import PdfReader
import argparse,json,re,subprocess,unicodedata
p=argparse.ArgumentParser();p.add_argument('manuscript',type=Path);p.add_argument('pdf',type=Path);p.add_argument('epub',type=Path);p.add_argument('report',type=Path);a=p.parse_args()
s=a.manuscript.read_text();chapters=re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |^# BOOK |\Z)',s,re.M|re.S)
books=re.findall(r'^# (BOOK [IVX]+:[^\n]+)',s,re.M)
r=PdfReader(a.pdf)
def outline_items(seq):
 for x in seq:
  if isinstance(x,list):yield from outline_items(x)
  else:yield x
outline=list(outline_items(r.outline))
assert len(outline)==len(books)+len(chapters),(len(outline),len(books),len(chapters))
expected=[]
for line in s.splitlines():
 if line.startswith('# BOOK '):expected.append(line[2:])
 elif line.startswith('## '):expected.append(line[3:])
assert [x.title for x in outline]==expected,'PDF bookmark sequence differs'
for x in outline:assert 0<=r.get_destination_page_number(x)<len(r.pages)
textfile=a.report.with_suffix('.txt');textfile.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['pdftotext',str(a.pdf),str(textfile)],check=True)
def norm(x):return ' '.join(unicodedata.normalize('NFKC',x).replace('\u2011','-').split())
pdftext=norm(textfile.read_text())
missing=[]
for title,body in chapters:
 blocks=[x.strip() for x in re.split(r'\n\s*\n',body.strip()) if x.strip() not in ('***','---')]
 for label,block in [('opening',blocks[0]),('ending',blocks[-1])]:
  clean=norm(re.sub(r'[*#]','',block))
  needle=clean[:90] if label=='opening' else clean[-90:]
  if needle not in pdftext:missing.append((title,label,needle))
assert not missing,missing
pages=textfile.read_text().split('\f');empties=[i+1 for i,x in enumerate(pages[:len(r.pages)]) if not x.strip()]
assert not empties,empties
with ZipFile(a.epub) as z:
 names=set(z.namelist());assert z.infolist()[0].filename=='mimetype' and z.infolist()[0].compress_type==ZIP_STORED
 assert z.read('mimetype')==b'application/epub+zip'
 roots={n:ET.fromstring(z.read(n)) for n in names if n.endswith(('.xhtml','.xml','.opf'))}
 opf=roots['OEBPS/package.opf'];ns={'p':'http://www.idpf.org/2007/opf'}
 ids={i.attrib['id']:i.attrib['href'] for i in opf.findall('p:manifest/p:item',ns)}
 for name in ids.values():assert 'OEBPS/'+name in names,name
 spine=opf.findall('p:spine/p:itemref',ns)
 for item in spine:assert item.attrib['idref'] in ids
 for file,root in roots.items():
  for e in root.iter():
   href=e.get('href')
   if href and file.endswith('.xhtml'):assert str(PurePosixPath(file).parent/href.split('#')[0]) in names,(file,href)
 epub_chapters=[n for n in names if re.search(r'book-\d+-chapter-\d+\.xhtml$',n)]
 assert len(epub_chapters)==len(chapters)
report={'words_including_front_matter_and_headings':len(s.split()),'books':len(books),'chapters':len(chapters),'pdf_pages':len(r.pages),'pdf_bookmarks':len(outline),'all_chapter_openings_and_endings_found':True,'empty_pdf_pages':empties,'epub_chapters':len(epub_chapters),'epub_xml_documents':len(roots),'epub_spine_items':len(spine),'epub_xml_and_local_links_valid':True}
a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
