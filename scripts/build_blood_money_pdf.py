#!/usr/bin/env python3
"""Render the Ten Toes Down manuscript as a bookmarked 6x9 reading edition.
Dependencies: reportlab. Usage: python scripts/build_blood_money_pdf.py [manuscript.md] [book.pdf]
"""
from pathlib import Path
import sys,re,html
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,CondPageBreak,HRFlowable
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,Color,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT,TA_CENTER

ROOT=Path(__file__).resolve().parents[1]
INPUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'editions/blood-money-and-blue-diamonds/manuscript.md'
OUTPUT=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'editions/blood-money-and-blue-diamonds/book.pdf'
font_root=Path('/usr/share/fonts/truetype/liberation2')
if not (font_root/'LiberationSerif-Regular.ttf').exists():
 font_root=Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype')
for name,file in [('Book','LiberationSerif-Regular.ttf'),('BookItalic','LiberationSerif-Italic.ttf'),('BookBold','LiberationSerif-Bold.ttf'),('BookBoldItalic','LiberationSerif-BoldItalic.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(font_root/file)))
pdfmetrics.registerFontFamily('Book',normal='Book',bold='BookBold',italic='BookItalic',boldItalic='BookBoldItalic')
for name,file in [('Sans','DejaVuSans.ttf'),('SansBold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=432,648
INK=HexColor('#202634');BLUE=HexColor('#183D91');GOLD=HexColor('#BC8838');PALE=HexColor('#F1EFE8');GREY=HexColor('#6D7380')
styles={
 'body':ParagraphStyle('body',fontName='Book',fontSize=12.5,leading=18.75,textColor=INK,spaceAfter=5.6,allowWidows=0,allowOrphans=0),
 'chapter':ParagraphStyle('chapter',fontName='SansBold',fontSize=21,leading=26,textColor=BLUE,spaceBefore=20,spaceAfter=25,keepWithNext=True),
 'inset':ParagraphStyle('inset',fontName='SansBold',fontSize=9.2,leading=13,textColor=BLUE,spaceBefore=19,spaceAfter=13,backColor=PALE,borderPadding=9,keepWithNext=True),
 'notice':ParagraphStyle('notice',fontName='BookItalic',fontSize=10.6,leading=14.3,textColor=INK,leftIndent=13,rightIndent=13,spaceAfter=5),
 'play':ParagraphStyle('play',fontName='Mono',fontSize=9.1,leading=14,textColor=INK,leftIndent=12,rightIndent=8,spaceAfter=7),
 'small':ParagraphStyle('small',fontName='Sans',fontSize=8.1,leading=12,textColor=GREY,spaceAfter=10),
}

def markup(s):
 s=html.escape(s,quote=False)
 s=re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#183D91"><u>\1</u></link>',s)
 s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
 return s.replace('\n','<br/>')

class BookDoc(BaseDocTemplate):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.chapter='';self._bnum=0
 def beforeDocument(self):self.chapter='';self._bnum=0
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name=='chapter':
   title=f.getPlainText();self.chapter=title;self._bnum+=1;key=f'ch-{self._bnum}'
   self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=0,closed=False)
   if title!='Contents':self.notify('TOCEntry',(0,title,self.page,key))

def page(c,d):
 if d.page==1:
  c.setFillColor(HexColor('#102348'));c.rect(0,0,W,H,stroke=0,fill=1)
  c.setFillColor(BLUE)
  for j in range(10):
   x=35+j*37
   c.rect(x,35,19,118+(j%3)*23,stroke=0,fill=1)
  diamond=c.beginPath();diamond.moveTo(216,125);diamond.lineTo(138,214);diamond.lineTo(171,246);diamond.lineTo(261,246);diamond.lineTo(294,214);diamond.close()
  c.setFillColor(HexColor('#235BBD'));c.drawPath(diamond,stroke=0,fill=1)
  c.setStrokeColor(HexColor('#6DA6F7'));c.setLineWidth(.8);c.line(138,214,294,214);c.line(171,246,195,214);c.line(261,246,237,214);c.line(195,214,216,125);c.line(237,214,216,125)
  c.setFillColor(HexColor('#F3BE5B'));c.rect(35,520,44,5,stroke=0,fill=1)
  c.setFillColor(white);c.setFont('SansBold',54)
  c.drawString(32,453,'TEN TOES');c.drawString(32,391,'DOWN')
  c.setFont('SansBold',18);c.setFillColor(HexColor('#F3BE5B'));c.drawString(36,341,'BLOOD MONEY');c.drawString(36,315,'AND BLUE DIAMONDS')
  c.setFont('BookItalic',13);c.setFillColor(HexColor('#D0DAEE'))
  c.drawString(36,279,'A novel')
  c.setFont('Sans',9);c.drawString(36,78,'WRITTEN BY CHATGPT FOR NOLAN')
  c.setFont('SansBold',9);c.setFillColor(HexColor('#F3BE5B'));c.drawString(36,54,'TEN TOES DOWN. FOREVER.')
  return
 c.setStrokeColor(HexColor('#DDE1E7'));c.setLineWidth(.4);c.line(48,H-35,W-48,H-35)
 c.setFillColor(GREY);c.setFont('Sans',7.1)
 c.drawString(48,H-26,'TEN TOES DOWN')
 c.drawRightString(W-48,H-26,'BLOOD MONEY AND BLUE DIAMONDS')
 c.setFont('Sans',8);c.drawCentredString(W/2,25,str(d.page))

OUTPUT.parent.mkdir(parents=True,exist_ok=True)
doc=BookDoc(str(OUTPUT),pagesize=(W,H),leftMargin=48,rightMargin=48,topMargin=51,bottomMargin=47,title='Ten Toes Down: Blood Money and Blue Diamonds',author='ChatGPT for Nolan',subject='A first-person crime and romance novel',pageCompression=1)
frame=Frame(48,47,W-96,H-98,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
doc.addPageTemplates(PageTemplate(id='book',frames=[frame],onPage=page))
story=[Spacer(1,20),PageBreak(),Paragraph('Contents',styles['chapter'])]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Book',fontSize=10.2,leading=14,leftIndent=0,firstLineIndent=0,rightIndent=14,spaceBefore=2,textColor=INK)]
story.append(toc)
story +=[Spacer(1,19),Paragraph('Written by ChatGPT for Nolan.<br/>September 2026.',styles['small'])]
raw=INPUT.read_text(encoding='utf-8')
raw=raw[raw.index('## 1. '):]
raw=re.sub(r'(?m)^(\*\*\*|---)$', '---', raw)
for block in re.split(r'\n\s*\n',raw.strip()):
 block=block.strip()
 if not block:continue
 if block=='---':
  story.extend([Spacer(1,7),HRFlowable(width=24,thickness=1.1,color=GOLD,hAlign='CENTER',spaceAfter=13)]);continue
 if block.startswith('## '):
  story.append(PageBreak());story.append(Paragraph(markup(block[3:]),styles['chapter']));continue
 if block.startswith('### '):
  story.append(CondPageBreak(95));story.append(Paragraph(markup(block[4:]),styles['inset']));continue
 sty=styles['body']
 if block.startswith(('THE KING:','THE VISITOR:')):sty=styles['play']
 if block.startswith('*') and block.endswith('*') and not block.startswith('**'):sty=styles['notice']
 story.append(Paragraph(markup(block),sty))
doc.multiBuild(story)
print(f'Created {OUTPUT}')
