#!/usr/bin/env python3
"""Render the six-book omnibus. Usage: python build_omnibus_pdf.py manuscript.md book.pdf"""
from pathlib import Path
import argparse,html,re
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,HRFlowable,CondPageBreak,ActionFlowable
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
parser=argparse.ArgumentParser()
parser.add_argument('manuscript',type=Path);parser.add_argument('pdf',type=Path)
parser.add_argument('--font-size',type=float,default=13.2);parser.add_argument('--leading',type=float,default=20.8)
args=parser.parse_args()
font_root=Path('/usr/share/fonts/truetype/liberation2')
if not (font_root/'LiberationSerif-Regular.ttf').exists():
 font_root=Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype')
for name,file in [('Book','LiberationSerif-Regular.ttf'),('BookItalic','LiberationSerif-Italic.ttf'),('BookBold','LiberationSerif-Bold.ttf'),('BookBoldItalic','LiberationSerif-BoldItalic.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(font_root/file)))
pdfmetrics.registerFontFamily('Book',normal='Book',bold='BookBold',italic='BookItalic',boldItalic='BookBoldItalic')
for name,file in [('Sans','DejaVuSans.ttf'),('SansBold','DejaVuSans-Bold.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=432,648
INK=HexColor('#172234');BLUE=HexColor('#16438c');GOLD=HexColor('#bf913e');GREY=HexColor('#6a7180')
styles={
 'body':ParagraphStyle('body',fontName='Book',fontSize=args.font_size,leading=args.leading,textColor=INK,spaceAfter=5.6,allowWidows=0,allowOrphans=0),
 'chapter':ParagraphStyle('chapter',fontName='SansBold',fontSize=20,leading=25,textColor=BLUE,spaceBefore=12,spaceAfter=24,keepWithNext=True),
 'book':ParagraphStyle('book',fontName='SansBold',fontSize=28,leading=36,textColor=BLUE,spaceBefore=112,spaceAfter=28,keepWithNext=True),
 'inset':ParagraphStyle('inset',fontName='SansBold',fontSize=10,leading=14,textColor=BLUE,spaceBefore=16,spaceAfter=12,keepWithNext=True),
 'notice':ParagraphStyle('notice',fontName='BookItalic',fontSize=args.font_size-.7,leading=args.leading-1.2,textColor=INK,leftIndent=14,rightIndent=12,spaceAfter=5.6),
 'small':ParagraphStyle('small',fontName='Sans',fontSize=8.2,leading=12,textColor=GREY,spaceAfter=10)}
def markup(s):
 s=html.escape(s.replace('\u2011','-'),quote=False)
 s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
 return s.replace('\n','<br/>')
class SetBook(ActionFlowable):
 def __init__(self,title):self.title=title
 def apply(self,doc):doc.book_title=self.title

class BookDoc(BaseDocTemplate):
 def beforeDocument(self):self.book_title='THE GREATEST MAN ALIVE';self.number=0
 def afterFlowable(self,f):
  if not isinstance(f,Paragraph) or f.style.name not in ('chapter','book'):return
  title=f.getPlainText()
  if title=='Contents':return
  self.number+=1;key=f'section-{self.number}';level=0 if f.style.name=='book' else 1
  if level==0:self.book_title=title
  self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=level,closed=level==0)
  self.notify('TOCEntry',(level,title,self.page,key))
def page(c,d):
 if d.page==1:
  c.setFillColor(HexColor('#102348'));c.rect(0,0,W,H,stroke=0,fill=1)
  c.setFillColor(GOLD);c.rect(35,530,60,5,stroke=0,fill=1)
  c.setFillColor(white);c.setFont('SansBold',54);c.drawString(32,464,'TEN TOES');c.drawString(32,402,'DOWN')
  c.setFillColor(HexColor('#f3be5b'));c.setFont('SansBold',24);c.drawString(35,338,'THE GREATEST');c.drawString(35,307,'MAN ALIVE')
  c.setFillColor(HexColor('#d0daee'));c.setFont('BookItalic',15);c.drawString(36,263,'The complete six-book epic')
  c.setStrokeColor(HexColor('#416db4'));c.setLineWidth(2)
  p=c.beginPath();p.moveTo(100,131);p.lineTo(75,215);p.lineTo(150,175);p.lineTo(216,240);p.lineTo(282,175);p.lineTo(357,215);p.lineTo(332,131);p.close()
  c.setFillColor(HexColor('#1c4382'));c.drawPath(p,stroke=1,fill=1)
  c.setFillColor(HexColor('#f3be5b'));c.setFont('SansBold',10);c.drawString(36,86,'TEN TOES DOWN. EVERYWHERE.')
  c.setFillColor(HexColor('#d0daee'));c.setFont('Sans',9);c.drawString(36,59,'WRITTEN BY CHATGPT FOR NOLAN');return
 c.setStrokeColor(HexColor('#dce2ed'));c.setLineWidth(.4);c.line(45,H-35,W-45,H-35)
 c.setFillColor(GREY);c.setFont('Sans',7);c.drawString(45,H-26,'TEN TOES DOWN')
 label=d.book_title.upper()
 while pdfmetrics.stringWidth(label,'Sans',7)>230:label=label[:-2]+'…'
 c.drawRightString(W-45,H-26,label);c.setFont('Sans',8);c.drawCentredString(W/2,25,str(d.page))
args.pdf.parent.mkdir(parents=True,exist_ok=True)
doc=BookDoc(str(args.pdf),pagesize=(W,H),leftMargin=45,rightMargin=45,topMargin=51,bottomMargin=47,title='Ten Toes Down: The Greatest Man Alive',author='ChatGPT for Nolan',subject='A six-book action and romance fanfiction epic',pageCompression=1)
frame=Frame(45,47,W-90,H-98,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
doc.addPageTemplates(PageTemplate(id='book',frames=[frame],onPage=page))
story=[Spacer(1,20),PageBreak(),Paragraph('Contents',styles['chapter'])]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc_book',fontName='SansBold',fontSize=10,leading=14,textColor=BLUE,spaceBefore=12,spaceAfter=4),ParagraphStyle('toc_chapter',fontName='Book',fontSize=10,leading=13.6,leftIndent=12,rightIndent=18,textColor=INK,spaceBefore=1)]
story.append(toc)
story.extend([Spacer(1,20),Paragraph('Written by ChatGPT for Nolan. September 2026.<br/>An alternate-universe work of fiction, including invented crossover and alternate-history episodes.',styles['small'])])
raw=args.manuscript.read_text(encoding='utf-8');raw=raw[raw.index('# BOOK I:'):]
raw=re.sub(r'(?m)^(\*\*\*|---)\n(?!\n)',r'\1\n\n',raw)
for block in re.split(r'\n\s*\n',raw.strip()):
 block=block.strip()
 if not block:continue
 if block in ('---','***'):
  story.extend([Spacer(1,7),HRFlowable(width=25,thickness=1,color=GOLD,hAlign='CENTER',spaceAfter=12)]);continue
 if block.startswith('# BOOK '):
  story.extend([SetBook(block[2:]),PageBreak(),Paragraph(markup(block[2:]),styles['book']),Spacer(1,100)]);continue
 if block.startswith('## '):
  story.extend([PageBreak(),Paragraph(markup(block[3:]),styles['chapter'])]);continue
 if block.startswith('### '):
  story.extend([CondPageBreak(90),Paragraph(markup(block[4:]),styles['inset'])]);continue
 sty=styles['body']
 if block.startswith('*') and block.endswith('*') and not block.startswith('**'):sty=styles['notice']
 story.append(Paragraph(markup(block),sty))
doc.multiBuild(story)
print(args.pdf)
