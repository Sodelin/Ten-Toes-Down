"""Build the six-volume Panorama, EPUB and offline selector from reviewed JSON.

Requires reportlab, pypdf and Pillow. Fonts default to Windows Georgia/Arial;
set PANORAMA_FONT_DIR when rebuilding on another machine with equivalent files.
Raw store text and private project context never enter the publication bundle.
"""
from pathlib import Path
import json, re, html, os, zipfile, hashlib, argparse, collections
from xml.etree import ElementTree as ET
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import NameObject, DictionaryObject, ArrayObject, NumberObject, RectangleObject

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATA=HERE/'panorama'
OUT=ROOT/'outputs'/'ten-toes-down-panorama'
TITLE='The Ten Toes Down Panorama of Games for Lillian'
DATE='2026-09-20'
AUTHOR='ChatGPT, under Nolan’s creative direction'
BURGUNDY=colors.HexColor('#782a3b')
INK=colors.HexColor('#252526')
GRAY=colors.HexColor('#565656')
CREAM=colors.HexColor('#f4f0e8')
EMBLEMS=['Envelope','Key','Plant','Map','Teacup','Spare chair','Gold stamp','Clock']
MOODS=['Quietly curious','Ready for conversation','Willing to inspect a thing','Here for the atmosphere','Open to a wildcard']
ATTR_KEYS=['pleasure','burden','first','ruling']
LABELS={'pleasure':'The actual attraction','burden':'The catch worth knowing','first':'An opening invitation','ruling':'Aiden’s entirely unnecessary ruling'}
STYLES={}
def words(s): return len(re.findall(r"\b[\w’'-]+\b",s))
def plain(s): return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ')
def esc(s): return html.escape(plain(s),quote=True)
def para(s,sty='body'):return Paragraph(esc(s),STYLES[sty])
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def setup_fonts():
    fd=Path(os.environ.get('PANORAMA_FONT_DIR','C:/Windows/Fonts'))
    for name,file in [('Body','georgia.ttf'),('BodyBold','georgiab.ttf'),('BodyItalic','georgiai.ttf'),('Sans','arial.ttf'),('SansBold','arialbd.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fd/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    for name,font,size,lead,space in [('body','Body',11.2,14.6,5),('small','Sans',8.9,11.5,5),('label','SansBold',9.5,12,3),('h1','BodyBold',25,29,15),('h2','BodyBold',17,21,11),('h3','BodyBold',13.5,17,7),('kicker','SansBold',9,12,8),('cover','BodyBold',35,39,19),('sub','BodyItalic',14,19,12),('index','Sans',10,13,4)]:
        STYLES[name]=ParagraphStyle(name,fontName=font,fontSize=size,leading=lead,spaceAfter=space,textColor=INK,allowWidows=0,allowOrphans=0)
    for key in ['kicker','label']:STYLES[key].textColor=BURGUNDY
    for key in ['h1','h2','h3','label','kicker']:STYLES[key].keepWithNext=True
    STYLES['narrative']=ParagraphStyle('narrative',parent=STYLES['body'],spaceAfter=3)
    STYLES['case']=ParagraphStyle('case',parent=STYLES['body'],leading=14.1,spaceAfter=3)
    STYLES['index'].spaceAfter=0
    STYLES['index'].fontSize=9.5
    STYLES['index'].leading=11.7

def metadata_line(g):
    return f"{g['id']}  /  {g['fit_tier'].upper()}  /  {g['input']} input  /  pace: {g['pace'].replace('_',' ')}  /  native co-op: {g['native_coop']}"

class BookDoc(SimpleDocTemplate):
    def __init__(self,*a,volume=1,**kw):
        super().__init__(*a,**kw);self.volume=volume;self.locations={}
    def afterFlowable(self,f):
        key=getattr(f,'case_id',None)
        if key:
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(getattr(f,'outline_title',key),key,level=0,closed=False);self.locations[key]=self.page
    def afterPage(self):
        pass

def furniture(c,doc):
    w,h=doc.pagesize;c.saveState()
    if doc.page==1:
        c.setStrokeColor(BURGUNDY);c.setLineWidth(1.5);c.rect(60,111,492,64)
        c.setFont('SansBold',13);c.setFillColor(BURGUNDY);c.drawCentredString(306,149,'240 CASES  /  SIX DEPARTMENTS')
        c.setFont('Sans',10);c.drawCentredString(306,129,'ZERO OBLIGATION TO OBEY THE DEPARTMENTS')
    if doc.page>1:
        c.setStrokeColor(BURGUNDY);c.setLineWidth(.5);c.line(50,h-38,w-50,h-38)
        c.setFont('SansBold',8);c.setFillColor(BURGUNDY);c.drawString(50,h-29,'TEN TOES DOWN  /  PANORAMA OF GAMES')
        c.setFont('Sans',8);c.setFillColor(GRAY);c.drawRightString(w-50,h-29,f'VOLUME {doc.volume}')
    c.setFont('Sans',8);c.setFillColor(GRAY);c.drawString(50,27,'THE GAMES ARE REAL. THE MINISTRIES ARE NOT.')
    c.drawRightString(w-50,27,f'{doc.volume} / {doc.page}')
    c.restoreState()

def section(story,title,paragraphs,break_before=False):
    if break_before:story.append(PageBreak())
    story.append(para(title,'h2'))
    tail=0;tail_words=0
    if break_before and len(paragraphs)>2:
        for p in reversed(paragraphs):
            tail+=1;tail_words+=len(p.split())
            if tail_words>=140:break
    if tail and tail<len(paragraphs):
        story.extend(para(p,'narrative')for p in paragraphs[:-tail])
        story.append(KeepTogether([para(p,'narrative')for p in paragraphs[-tail:]]))
    else:story.extend(para(p,'narrative')for p in paragraphs)

def source_paras(g):
    out=[para(g['source_note'],'small')]
    for i,url in enumerate(g['source_urls'],1):
        # Line-breakable printed URL plus an actual PDF hyperlink.
        visible=esc(url).replace('/','/<wbr/>').replace('_','_<wbr/>').replace('?','?<wbr/>')
        out.append(Paragraph(f'<link href="{esc(url)}" color="#782a3b">Source {i}: {visible}</link>',STYLES['small']))
    return out

def route_grid(n):
    rows=[[para('Mood / emblem','small')]+[para(f'{i+1}. {v}','small')for i,v in enumerate(EMBLEMS)]]
    for row,mood in enumerate(MOODS):
        rows.append([para(f'{row+1}. {mood}','small')]+[para(f'P{40*(n-1)+8*row+c+1:03d}','small')for c in range(8)])
    t=Table(rows,colWidths=[100]+[49]*8,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),CREAM),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d4ccbf')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    return t

def make_story(v,front,known_pages):
    n=v['number'];st=[]
    st.extend([Spacer(1,40),para('TEN TOES DOWN PRESENTS','kicker'),para('The Panorama\nof Games for Lillian'.replace('\n',' '),'cover'),para(f'VOLUME {n} OF SIX','kicker'),para(v['title'],'h1'),para(v['subtitle'],'sub'),Spacer(1,25),para('Forty real games. One wildly unnecessary department.','body'),para('A comic companion, written by ChatGPT under Nolan’s creative direction.','small'),para('Reader edition 1.0 - 20 September 2026','small'),PageBreak()])
    section(st,'Before the stamp hits the page',[
        'This is an original comic game catalogue inspired by the Aiden ensemble in Ten Toes Down. The source novels remain separate. Game descriptions and catches are research-based editorial notes; Aiden’s ministry and rulings are fiction.',
        'The catalogue ranges across possible fits and clearly marked detours. “Waits” describes the usual decision loop, not a certification that every scene is untimed. Promising, conditional and detour are editorial labels, not measurements of anyone’s ability. Read the catch on the exact edition.',
        'Choose any game directly. Skip any game for any reason. The elaborate route is an optional joke; declining never costs a token. No purchase, download, account or medical information is needed to use this book.',
        'Print on Letter paper at actual size, or fit to A4. Page references use volume / page, which remain valid in the omnibus. For larger type, use the reflowable EPUB. Links and a full alphabetical index sit beside the printed case numbers.'
    ])
    st.append(para('The six departments','h3'))
    for no,label in enumerate(['Suspiciously Interesting People - mysteries and adventures','Taking One’s Turn - strategy and role-playing','Looking Around Before Doing Anything - exploration','Things That Fit Into Other Things - puzzles and construction','People Who Have Something to Tell You - character stories','Bringing a Friend - co-op and shared play'],1):st.append(para(f'{no}. {label}','index'))
    if n==1:
        for title,ps in front['preface']:section(st,title,ps,True)
        st.append(PageBreak());st.append(para('The Rules Department Has Acquired a Rules Department','h1'))
        for title,ps in front['rules']:section(st,title,ps)
        section(st,'Twelve optional declarations of personality',[f'{i+1}. {s[0]}. {s[1]}'for i,s in enumerate(front['aspects'])],True)
        section(st,'The incident desk',[f'{i+1}. {s[0]}. {s[1]}'for i,s in enumerate(front['incidents'])],True)
    st.append(PageBreak());st.append(para('A route that knows when to shut up','h1'))
    section(st,'The shortest working procedure',[
        'First name up to three real preferences or vetoes: required speed, camera movement, holds, menus, reading, clue tracking or native co-op. Keep them beside you. The route cannot overrule them.',
        f'You are in Department {n}. Pick one mood row and one emblem column below; neither claims to describe a game feature. That gives a starting case. You can go there now.',
        'For ceremonial excess only, roll four ordinary six-sided dice: 1-2 means minus one; 3-4 means zero; 5-6 means plus one. Add the four results. Add zero, one or two for any already-available wanted drink and wanted snack. Eating is never required.',
        'Begin a browsing session with three imaginary Stamp Tokens. At most once per selection, spend one to add two OR reroll all four dice. You may take an optional funny trait from Book I as your excuse. Never pay a token to refuse a game.',
        'Move that many cases along this department’s forty-case shelf, wrapping around at either end. Read the real catch. If you want one appeal, visit the adjacent case or the same local position in another department; then choose freely or stop. No appeal loops.',
        'The printed full rules, worked example and incident desk are in Volume I. The offline index performs the arithmetic and provides conservative evidence filters. The direct alphabetical index at the back always works without dice.'
    ])
    st.append(route_grid(n));st.append(Spacer(1,10));st.append(para('Local position = 8 × (row - 1) + emblem. Wrap modified position to 1-40. Global case = 40 × (department - 1) + local position.','small'))
    for sec in v['opening']:section(st,sec['title'],sec['paragraphs'],True)
    inter=list(v['interludes'])
    for i,g in enumerate(v['games']):
        st.append(PageBreak());st.append(para(metadata_line(g),'kicker'))
        h=para(g['title'],'h1');h.case_id=g['id'];h.outline_title=f"{g['id']} - {g['title']}";st.append(h)
        st.append(para(g['case_title'],'sub'))
        st.append(para('Edition considered: '+g.get('edition_target','See the evidence note for the edition.'),'small'))
        st.extend(para(p,'case')for p in g['scene'])
        for k in ATTR_KEYS:
            st.append(para(LABELS[k],'label'));st.append(para(g[k],'case'))
        st.append(Spacer(1,4));st.append(para('Evidence desk / checked 20 September 2026','label'));st.extend(source_paras(g))
        if (i+1)%10==0 and inter:
            sec=inter.pop(0);section(st,sec['title'],sec['paragraphs'],True)
    for sec in inter+v['ending']:section(st,sec['title'],sec['paragraphs'],True)
    st.append(PageBreak());st.append(para('An index with no authority over you','h1'))
    st.append(para('The case number works in every format. The last column is this volume’s printed page. Click a title in the PDF to jump to it.','body'))
    cells=[]
    for g in sorted(v['games'],key=lambda x:x['title'].casefold()):
        cells.append([para(g['id'],'index'),Paragraph(f'<link href="#{g["id"]}" color="#782a3b">{esc(g["title"])}</link>',STYLES['index']),para(str(known_pages.get(g['id'],'...')),'index')])
    half=(len(cells)+1)//2
    rows=[cells[i]+(cells[i+half]if i+half<len(cells)else ['','',''])for i in range(half)]
    t=Table(rows,colWidths=[39,176,25]*2,hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#ddd6ce')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]));st.append(t)
    section(st,'Credits, source limits and the paperwork we actually mean',front['attribution'],True)
    st.append(para('Each case names its inspected sources and the limits of those sources. Store descriptions and developer feature declarations are not a playthrough of every route. The companion evidence ledger records editorial tags separately from source declarations. Availability and features may change after the check date.','body'))
    return st

def write_book(v,front):
    path=OUT/f'Panorama-Volume-{v["number"]:02d}.pdf';loc={}
    for attempt in range(2):
        doc=BookDoc(str(path),volume=v['number'],pagesize=(612,792),rightMargin=60,leftMargin=60,topMargin=56,bottomMargin=49,title=f'{TITLE} - Volume {v["number"]}',author=AUTHOR,pageCompression=1)
        doc.build(make_story(v,front,loc),onFirstPage=furniture,onLaterPages=furniture)
        if attempt and loc!=doc.locations:raise AssertionError('Index pagination did not converge')
        loc=doc.locations
    return path,loc,len(PdfReader(path).pages)

def all_sections(volumes,front):
    # This common linear reading sequence drives Markdown and EPUB.
    for i,(title,ps)in enumerate(front['preface']):yield f'welcome-{i}',title,[(None,p)for p in ps]
    yield 'rules','The Rules Department Has Acquired a Rules Department',[(t,p)for t,ps in front['rules']for p in ps]
    yield 'aspects','Twelve optional declarations of personality',[(None,f'{i+1}. {s[0]}. {s[1]}')for i,s in enumerate(front['aspects'])]
    yield 'incidents','The incident desk',[(None,f'{i+1}. {s[0]}. {s[1]}')for i,s in enumerate(front['incidents'])]
    for v in volumes:
        n=v['number'];yield f'v{n}',f'Volume {n}: {v["title"]}',[(None,v['subtitle'])]
        for i,s in enumerate(v['opening']):yield f'v{n}-open{i}',s['title'],[(None,p)for p in s['paragraphs']]
        inter=list(v['interludes'])
        for i,g in enumerate(v['games']):
            ps=[(None,g['case_title']),(None,metadata_line(g)),('Edition considered',g.get('edition_target','See the evidence note for the edition.'))]+[(None,p)for p in g['scene']]+[(LABELS[k],g[k])for k in ATTR_KEYS]+[('Evidence desk',g['source_note'])]+[('Source',u)for u in g['source_urls']]
            yield g['id'],f'{g["id"]} - {g["title"]}',ps
            if (i+1)%10==0 and inter:
                s=inter.pop(0);yield f'v{n}-inter{i}',s['title'],[(None,p)for p in s['paragraphs']]
        for i,s in enumerate(inter+v['ending']):yield f'v{n}-end{i}',s['title'],[(None,p)for p in s['paragraphs']]
    yield 'credits','Credits and source limits',[(None,p)for p in front['attribution']]

def write_text_and_epub(volumes,front):
    secs=list(all_sections(volumes,front));md=[f'# {TITLE}',f'\n{AUTHOR}\n\nReader edition 1.0 / {DATE}\n']
    for sid,title,ps in secs:
        md.append(f'\n## {title}\n')
        previous=None
        for label,p in ps:
            if label and label!=previous:md.append(f'### {label}\n')
            md.append(p+'\n');previous=label
    manuscript='\n'.join(md);(OUT/'Manuscript.md').write_text(manuscript,encoding='utf8')
    epub=OUT/'Ten-Toes-Down-Panorama.epub';manifest=[];spine=[];nav=[]
    css='body{font-family:serif;line-height:1.5;margin:5%;}h1,h2{line-height:1.2;}h2{font-size:1.15em;margin-top:1.5em;}p{margin:0 0 .75em;}a{overflow-wrap:anywhere;} .label{font-weight:bold;} .meta{font-family:sans-serif;font-size:.85em;}'
    with zipfile.ZipFile(epub,'w')as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml','<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr('OEBPS/style.css',css)
        for sid,title,ps in secs:
            body=f'<h1>{html.escape(title)}</h1>';previous=None
            for label,p in ps:
                if label and label!=previous:body+=f'<h2>{html.escape(label)}</h2>'
                previous=label
                body+=f'<p><a href="{html.escape(p,quote=True)}">{html.escape(p)}</a></p>'if label=='Source'else f'<p>{html.escape(p)}</p>'
            x=f'<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" lang="en"><head><title>{html.escape(title)}</title><link href="style.css" rel="stylesheet" type="text/css"/></head><body>{body}</body></html>'
            ET.fromstring(x);z.writestr(f'OEBPS/{sid}.xhtml',x)
            manifest.append(f'<item id="{sid}" href="{sid}.xhtml" media-type="application/xhtml+xml"/>');spine.append(f'<itemref idref="{sid}"/>');nav.append(f'<li><a href="{sid}.xhtml">{html.escape(title)}</a></li>')
        navx='<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1><ol>'+''.join(nav)+'</ol></nav></body></html>'
        z.writestr('OEBPS/nav.xhtml',navx)
        opf=f'<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:ttd:panorama:20260920:1</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title><dc:creator>{html.escape(AUTHOR)}</dc:creator><dc:language>en</dc:language><meta property="dcterms:modified">2026-09-20T00:00:00Z</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="style.css" media-type="text/css"/>'+''.join(manifest)+'</manifest><spine>'+''.join(spine)+'</spine></package>'
        z.writestr('OEBPS/content.opf',opf)
    # A paragraph-by-paragraph check ensures every authored chapter reached EPUB.
    with zipfile.ZipFile(epub)as z:
        for sid,title,ps in secs:
            rt=ET.fromstring(z.read(f'OEBPS/{sid}.xhtml'))
            actual=[''.join(p.itertext())for p in rt.findall('.//{http://www.w3.org/1999/xhtml}p')]
            assert actual==[p for _,p in ps],sid
    return words(manuscript),len(secs)

def load_data(partial=False):
    front=json.loads((DATA/'frontmatter.json').read_text(encoding='utf8'))
    vols=[json.loads(p.read_text(encoding='utf8'))for p in sorted(DATA.glob('volume-??.json'))]
    games=[g for v in vols for g in v['games']]
    inventory=json.loads((HERE/'panorama-candidate-draft.json').read_text(encoding='utf-8-sig'))
    editions={g['id']:g.get('edition','See source note.')for v in inventory['volumes']for g in v['games']}
    for g in games:g['edition_target']=editions[g['id']]
    if not partial:
        assert len(vols)==6 and [v['number']for v in vols]==list(range(1,7))
        assert all(len(v['games'])==40 for v in vols),[(v['number'],len(v['games']))for v in vols]
        assert {g['id']for g in games}=={f'P{i:03d}'for i in range(1,241)}
    assert len({g['id']for g in games})==len(games)
    for g in games:
        for k in ['id','title','case_title','scene',*ATTR_KEYS,'input','pace','memory','tone','native_coop','fit_tier','source_urls','source_note']:assert g.get(k),f'{g.get("id")} missing {k}'
        assert g['fit_tier']in ['promising','conditional','detour']
        assert g['pace']in ['waits','real_time','mixed','unknown']
        assert all(u.startswith('https://')or u.startswith('http://')for u in g['source_urls'])
    return front,vols,games

def make_evidence(games):
    evidence=[]
    for g in games:
        p=DATA/'primary-cache'/f'{g["id"]}.json';raw=json.loads(p.read_text(encoding='utf8'))if p.exists()else{}
        def source_identity(u):
            m=re.search(r'store\.steampowered\.com/app/(\d+)',u)
            return 'steam:'+m.group(1)if m else u.rstrip('/').split('?')[0]
        same_source=any(source_identity(u)==source_identity(raw.get('source_url',''))for u in g['source_urls'])
        # Edition exceptions are fail-closed. Never import a remake's declarations.
        eligible=raw.get('status')=='matched' and same_source and g['id']not in ['P201'] and raw.get('type')=='game'
        decs=raw.get('categories',[])if eligible else []
        record={'id':g['id'],'title':g['title'],'source_urls':g['source_urls'],'source_note':g['source_note'],'checked':DATE,'developer_declarations':decs,'declarations_status':'exact source match; developer declaration, not hands-on test'if eligible else'not imported; unknown or different edition/source','editorial_tags':{k:g[k]for k in ['input','pace','memory','native_coop','fit_tier','tone']},'hands_on_test':False}
        evidence.append(record)
    return evidence

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);setup_fonts();front,vols,games=load_data(args.preview)
    books=[];locations={};counts={}
    for v in vols:
        if args.preview and not v['games']:continue
        if args.preview:v=dict(v,games=v['games'][:2])
        path,loc,count=write_book(v,front);books.append(path);locations.update({k:{'volume':v['number'],'page':p}for k,p in loc.items()});counts[path.name]=count;print(path.name,count,flush=True)
    if args.preview:return
    combined=PdfWriter();offset=0
    for no,b in enumerate(books,1):
        r=PdfReader(b);page_ids={p.indirect_reference.idnum:i for i,p in enumerate(r.pages)}
        for p in r.pages:
            original_annotations=p.pop(NameObject('/Annots'),None)
            combined.add_page(p)
            if original_annotations is not None:p[NameObject('/Annots')]=original_annotations
        parent=combined.add_outline_item(f'Volume {no}',offset)
        for gid,where in locations.items():
            if where['volume']==no:combined.add_outline_item(gid+' - '+next(g['title']for g in games if g['id']==gid),offset+where['page']-1,parent=parent)
        for i,p in enumerate(r.pages):
            for ref in p.get('/Annots',[]):
                a=ref.get_object();rect=tuple(float(x)for x in a['/Rect'])
                if a.get('/A',{}).get('/URI'):
                    combined.add_annotation(offset+i,Link(rect=rect,url=str(a['/A']['/URI'])))
                elif a.get('/Dest'):
                    target=a['/Dest'][0];target_index=page_ids[target.idnum]
                    link=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Link'),NameObject('/Rect'):RectangleObject(rect),NameObject('/Border'):ArrayObject([NumberObject(0),NumberObject(0),NumberObject(0)]),NameObject('/Dest'):ArrayObject([combined.pages[offset+target_index].indirect_reference,NameObject('/Fit')])})
                    dest_page=combined.pages[offset+i]
                    if '/Annots'not in dest_page:dest_page[NameObject('/Annots')]=ArrayObject()
                    dest_page['/Annots'].append(combined._add_object(link))
                else:raise AssertionError('Unsupported annotation during omnibus merge')
        offset+=len(r.pages)
    combined.add_metadata({'/Title':TITLE,'/Author':AUTHOR});combined.write(OUT/'Panorama-Complete-Omnibus.pdf');counts['Panorama-Complete-Omnibus.pdf']=sum(counts.values())
    wc,chapters=write_text_and_epub(vols,front)
    evidence=make_evidence(games)
    corpus={'title':TITLE,'edition':'1.0','checked':DATE,'scope':'240 editorial candidates, including conditional and detour entries; no full-game accessibility certification','privacy':'No personal or clinical history included','games':games}
    dump(OUT/'game-corpus.json',corpus);dump(OUT/'evidence-ledger.json',evidence);dump(OUT/'page-index.json',locations)
    dump(OUT/'routing-rules.json',{'departments':[{'number':v['number'],'title':v['title']}for v in vols],'moods':MOODS,'emblems':EMBLEMS,'aspects':front['aspects'],'incidents':front['incidents'],'rules':front['rules'],'stamp_tokens':3,'max_modification_actions_per_selection':1,'max_appeals_per_selection':1,'veto_is_free':True})
    summary={'title':TITLE,'games':len(games),'volumes':6,'unique_manuscript_word_count':wc,'word_count_method':'Regex word tokens in single combined Markdown; excludes duplicate PDF introductions, offline app and raw source cache','epub_chapters':chapters,'pdf_pages':counts,'tier_counts':dict(collections.Counter(g['fit_tier']for g in games)),'primary_declaration_records':sum(bool(e['developer_declarations'])for e in evidence),'all_games_have_source_notes':True,'full_playthroughs':0}
    prose=[p for g in games for p in g['scene']]+[g[k]for g in games for k in ATTR_KEYS]+[p for v in vols for s in v['opening']+v['interludes']+v['ending']for p in s['paragraphs']]+[p for _,ps in front['preface']+front['rules']for p in ps]+[p for entry in front['aspects']+front['incidents']for p in entry]
    summary['original_comic_and_catalog_prose_word_count']=sum(words(s)for s in prose)
    dump(OUT/'build-report.json',summary)
    import csv
    with(OUT/'game-index.csv').open('w',newline='',encoding='utf-8-sig')as f:
        fields=['id','title','volume','page','input','pace','memory','native_coop','fit_tier','source_urls'];w=csv.DictWriter(f,fields);w.writeheader()
        for g in games:w.writerow({**{k:g[k]for k in fields if k in g},**locations[g['id']],'source_urls':' | '.join(g['source_urls'])})
    (OUT/'Source-Notes.md').write_text('# Source notes\n\nChecked '+DATE+'. Research notes are editorial screening, not full playthroughs. Raw store descriptions are excluded from the publication.\n\n'+'\n\n'.join(f'## {g["id"]}: {g["title"]}\n\n{g["source_note"]}\n\n'+'\n'.join('- '+u for u in g['source_urls'])for g in games),encoding='utf8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
