#!/usr/bin/env python3
"""Build an EPUB 3 reading edition with a nested table of contents."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZIP_STORED
import argparse,html,re,uuid
p=argparse.ArgumentParser();p.add_argument('manuscript',type=Path);p.add_argument('epub',type=Path);a=p.parse_args()
s=a.manuscript.read_text();s=s[s.index('# BOOK I:'):]
uid='urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,s))
E=lambda x:html.escape(x,quote=True)
def inline(x):
 x=E(x);x=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',x);x=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>',x);return x.replace('\n','<br/>')
def page(title,body):
 return '<?xml version="1.0" encoding="utf-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml" lang="en"><head><title>'+E(title)+'</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>'+body+'</body></html>'
files={};groups=[];spine=[]
files['title.xhtml']=page('Ten Toes Down: The Greatest Man Alive','<section class="title"><h1>Ten Toes Down</h1><h2>The Greatest Man Alive</h2><p>The complete six-book epic</p><p>Written by ChatGPT for Nolan</p><p>September 2026</p><p>An alternate-universe work of fiction, including invented crossover and alternate-history episodes.</p></section>')
spine.append(('title','title.xhtml'))
for bi,match in enumerate(re.finditer(r'^# (BOOK [IVX]+: [^\n]+)\n(.*?)(?=^# BOOK |\Z)',s,re.M|re.S),1):
 btitle=match.group(1);body=match.group(2);bfile=f'book-{bi}.xhtml'
 files[bfile]=page(btitle,'<section class="book"><h1>'+E(btitle)+'</h1></section>');spine.append((f'book-{bi}',bfile))
 children=[]
 for ci,ch in enumerate(re.finditer(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)',body,re.M|re.S),1):
  title=ch.group(1);content=ch.group(2);blocks=['<h1>'+E(title)+'</h1>']
  for block in re.split(r'\n\s*\n',content.strip()):
   block=block.strip()
   if not block:continue
   if block in ('***','---'):blocks.append('<hr/>')
   elif block.startswith('### '):blocks.append('<h2>'+inline(block[4:])+'</h2>')
   elif block.startswith('*') and block.endswith('*') and not block.startswith('**'):blocks.append('<p class="letter">'+inline(block)+'</p>')
   else:blocks.append('<p>'+inline(block)+'</p>')
  name=f'book-{bi}-chapter-{ci:02}.xhtml';files[name]=page(title,'\n'.join(blocks));spine.append((f'b{bi}c{ci}',name));children.append((title,name))
 groups.append((btitle,bfile,children))
nav=['<h1>Contents</h1><nav xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc" id="toc"><ol>']
for title,bfile,children in groups:
 nav.append('<li><a href="'+bfile+'">'+E(title)+'</a><ol>')
 nav.extend('<li><a href="'+f+'">'+E(t)+'</a></li>' for t,f in children);nav.append('</ol></li>')
nav.append('</ol></nav>');files['nav.xhtml']=page('Contents','\n'.join(nav))
files['style.css']='body{font-family:serif;line-height:1.45;margin:5%;}h1,h2{font-family:sans-serif;line-height:1.2;}h1{font-size:1.5em;}h2{font-size:1.1em;}p{margin:.7em 0;}p.letter{margin-left:1em;margin-right:1em;}hr{width:10%;margin:1.5em auto;}section.title,section.book{margin-top:20%;}nav ol{padding-left:1.2em;}nav li{margin:.55em 0;}'
manifest=['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>','<item id="css" href="style.css" media-type="text/css"/>']
manifest.extend('<item id="'+i+'" href="'+f+'" media-type="application/xhtml+xml"/>' for i,f in spine)
metadata='<dc:identifier id="uid">'+uid+'</dc:identifier><dc:title>Ten Toes Down: The Greatest Man Alive</dc:title><dc:creator>ChatGPT for Nolan</dc:creator><dc:language>en</dc:language><dc:description>An alternate-universe action and romance epic in six books.</dc:description><meta property="dcterms:modified">2026-09-07T00:00:00Z</meta>'
files['package.opf']='<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'+metadata+'</metadata><manifest>'+''.join(manifest)+'</manifest><spine>'+''.join('<itemref idref="'+i+'"/>' for i,f in spine)+'</spine></package>'
a.epub.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(a.epub,'w') as z:
 z.writestr('mimetype','application/epub+zip',compress_type=ZIP_STORED)
 z.writestr('META-INF/container.xml','<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',compress_type=ZIP_DEFLATED)
 for f,content in files.items():z.writestr('OEBPS/'+f,content,compress_type=ZIP_DEFLATED)
print(a.epub)
