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
TITLE='Ten Toes Down: The Second Great Butch vs. Stud War - The Panorama of Games for Lillian'
DATE='2026-09-20'
AUTHOR='ChatGPT, under Nolan’s creative direction'
BURGUNDY=colors.HexColor('#61275f')
INK=colors.HexColor('#252526')
GRAY=colors.HexColor('#565656')
CREAM=colors.HexColor('#f4f0e8')
EMBLEMS=['Envelope','Key','Plant','Map','Teacup','Spare chair','Gold stamp','Clock']
MOODS=['Quietly curious','Ready for conversation','Willing to inspect a thing','Here for the atmosphere','Open to a wildcard']
ATTR_KEYS=['pleasure','burden','first','ruling']
CHORUS_LABEL='AIDEN AND TANK / THE COALITION CHORUS'
CHORUS=[
    ['Niggas, games up.','Niggas, pens out.','Niggas, chairs in.','Niggas, snacks here.','Niggas, receipts ready.'],
    ['Niggas, lights on.','Niggas, mic check.','Niggas, take turns.','Niggas, dance later.','Niggas, read first.'],
    ['Niggas, pick freely.','Niggas, no rush.','Niggas, sign here.','Niggas, stay petty.',"Niggas, we're good."]
]
CHORUS_LINES=['  /  '.join(row)for row in CHORUS]
DISCUSSION_LOCATIONS={}
DISCUSSION_TOPICS={1:'Names, race and who gets treated as the default',2:'Money, labor and respectability',3:'Public space and being read by strangers',4:'Drag, identity and the audience',5:'Desire, femmes and the work of care',6:'Coalition, resources and accountability'}

def deep_discussion(v):
    i,sec=max(enumerate(v['interludes']),key=lambda x:sum(words(p)for p in x[1]['paragraphs']))
    return i,sec

HISTORY_TITLE='The Department of Lesbian Lore Has Seized the Microphone'
HISTORY_INTRO=[
    'Aiden requested the entire history of lesbians, preferably in a font that made him look responsible. The archive declined the second condition. What follows is a substantial, selective field guide through several histories of desire, community, conflict and organizing. Its dates orient the reader; they do not rank cultures by how far they have progressed.',
    'There is no single family tree that begins in Greece, passes through white Europe and ends by admitting everybody else. Nor can one white-butch/Black-stud rivalry explain the racial boundaries of lesbian life. Read the locally named people, organizations and records here as distinct histories that sometimes meet, rather than stages of one universal development.',
    'Every dossier separates the historical account, a question for interpretation, the limits of the evidence, and a completely fictional summit scene. A source record may be a manifesto, an organizational self-history, an interview, an abstract or a curator’s description. Those are different forms of evidence. An archive finding aid does not mean its whole collection was read.',
    'Pleasure belongs in the history alongside organizing and exclusion. Sexual roles, gender presentation, erotic preference and identity can connect without being interchangeable. This guide discusses desire and sexual politics without converting anyone’s body or boundaries into a spectacle. Aiden supplies enough spectacle already. The fictional 1967 Blue Comet war remains entirely outside the factual timeline.'
]

def load_history():
    entries=[]
    for name in ['history-root.json','history-black.json','history-world.json']:
        entries.extend(json.loads((DATA/name).read_text(encoding='utf8')))
    entries.sort(key=lambda h:(h['sort_year'],h['title']))
    for i,h in enumerate(entries,1):h['source_id']=h['id'];h['id']=f'H{i:02d}'
    return entries

def history_sections():
    yield 'history-intro',HISTORY_TITLE,[(None,p)for p in HISTORY_INTRO]
    for h in load_history():
        ps=[('Place and period',h['period'])]+[(None,p)for p in h['paragraphs']]+[('The question underneath',h['question']),('Evidence limit',h['caveat'])]
        ps += [('Aiden has entered the archive / fiction'if i==0 else None,p)for i,p in enumerate(h['fiction'])]
        for c in h['source_records']:ps.extend([('Read scope',c['title']+'. '+c['read_scope']),('Source',c['url'])])
        yield h['id'],h['title'],ps

def write_history_notes(history_index):
    md=['# '+HISTORY_TITLE,'']
    for sid,title,ps in history_sections():
        md.extend(['## '+title,'']);prev=None
        for label,para_text in ps:
            if label and label!=prev:md.extend(['### '+label,''])
            md.extend([para_text,'']);prev=label
    (OUT/'Lesbian-History-Field-Guide.md').write_text('\n'.join(md),encoding='utf8')
    dump(OUT/'history-corpus.json',{'title':HISTORY_TITLE,'scope':HISTORY_INTRO,'entries':load_history(),'full_global_history_claimed':False})
    dump(OUT/'history-index.json',history_index)
    refs={c['url']:c for h in load_history()for c in h['source_records']}
    dump(OUT/'history-source-ledger.json',{'checked':DATE,'sources':list(refs.values()),'quotations_reproduced':False})
    ris=[];csl=[]
    for i,(url,c)in enumerate(refs.items(),1):
        rid=f'HREF{i:02d}';ris.extend(['TY  - ELEC','ID  - '+rid,'TI  - '+c['title'],'UR  - '+url,'N1  - '+c['read_scope'],'ER  - ',''])
        csl.append({'id':rid,'type':'webpage','title':c['title'],'URL':url,'note':c['read_scope']})
    (OUT/'history-references.ris').write_text('\n'.join(ris),encoding='utf8');dump(OUT/'history-references.csl.json',csl)

def cultural_sources():
    return json.loads((DATA/'cultural-sources.json').read_text(encoding='utf8'))

CONTEXT_INTRO='These are cultural reading notes, not a taxonomy of people. The dialogues are original fiction: each character has a partial perspective and no character speaks for an entire community. The fictional 1967 feud is not actual LGBTQ history. The notes below distinguish what was inspected from what was not.'

def write_cultural_notes():
    sources=cultural_sources();dump(OUT/'cultural-source-ledger.json',{'checked':DATE,'scope':CONTEXT_INTRO,'sources':sources})
    lines=['# Cultural reading notes','',CONTEXT_INTRO,'']
    ris=[];csl=[]
    for c in sources:
        lines.extend([f"## {c['id']}. {c['title']}",'',c['note'],'',f"**Read scope:** {c['scope']}",'',f"[Source]({c['url']})",''])
        ris.extend(['TY  - '+('JOUR'if c['id']=='C1'else'ELEC'),'ID  - '+c['id'],'TI  - '+c['title'],'AU  - '+c['author'],'UR  - '+c['url'],'N1  - '+c['scope']])
        if c.get('year'):ris.append('PY  - '+str(c['year']))
        if c.get('doi'):ris.append('DO  - '+c['doi'])
        ris.extend(['ER  - ',''])
        item={'id':c['id'],'type':'article-journal'if c['id']=='C1'else'webpage','title':c['title'],'author':[{'literal':c['author']}],'URL':c['url'],'note':c['scope']}
        if c.get('year'):item['issued']={'date-parts':[[c['year']]]}
        if c.get('doi'):item['DOI']=c['doi']
        csl.append(item)
    (OUT/'Cultural-Reading-Notes.md').write_text('\n'.join(lines),encoding='utf8')
    (OUT/'cultural-references.ris').write_text('\n'.join(ris),encoding='utf8');dump(OUT/'cultural-references.csl.json',csl)


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
    for name,font,size,lead,space in [('body','Body',11.2,14.6,5),('small','Sans',8.9,11.5,5),('label','SansBold',9.5,12,3),('h1','BodyBold',25,29,15),('h2','BodyBold',17,21,11),('h3','BodyBold',13.5,17,7),('kicker','SansBold',9,12,8),('cover','BodyBold',30,34,15),('sub','BodyItalic',14,19,12),('index','Sans',10,13,4)]:
        STYLES[name]=ParagraphStyle(name,fontName=font,fontSize=size,leading=lead,spaceAfter=space,textColor=INK,allowWidows=0,allowOrphans=0)
    for key in ['kicker','label']:STYLES[key].textColor=BURGUNDY
    for key in ['h1','h2','h3','label','kicker']:STYLES[key].keepWithNext=True
    STYLES['narrative']=ParagraphStyle('narrative',parent=STYLES['body'],spaceAfter=3)
    STYLES['rules']=ParagraphStyle('rules',parent=STYLES['narrative'],fontSize=10.8,leading=13.2)
    STYLES['case']=ParagraphStyle('case',parent=STYLES['body'],leading=14.1,spaceAfter=3)
    STYLES['case_title']=ParagraphStyle('case_title',parent=STYLES['h1'],fontSize=22,leading=25,spaceAfter=9)
    STYLES['scene']=ParagraphStyle('scene',parent=STYLES['body'],fontSize=10.7,leading=13.0,spaceAfter=3)
    STYLES['quick']=ParagraphStyle('quick',parent=STYLES['body'],fontName='BodyBold',fontSize=11.2,leading=14.4,spaceAfter=7)
    STYLES['fact']=ParagraphStyle('fact',parent=STYLES['body'],fontSize=10.8,leading=13.5,spaceAfter=5)
    STYLES['credits']=ParagraphStyle('credits',parent=STYLES['small'],fontSize=9.8,leading=12.5,spaceAfter=7)
    STYLES['index'].spaceAfter=0
    STYLES['index'].fontSize=9.5
    STYLES['index'].leading=11.7

def metadata_line(g):
    return f"{g['id']}  /  "+{'promising':'A PLACE TO START','conditional':'READ THE CATCH FIRST','detour':'A MORE DEMANDING DETOUR'}[g['fit_tier']]

def fact_line(label,text):
    return Paragraph(f'<b>{esc(label)}</b> {esc(text)}',STYLES['fact'])

def control_line(g):
    inputs={'pointer':'Mouse / pointer','buttons':'Buttons','directional':'Direction + buttons','touch':'Touch','keyboard':'Keyboard','mixed':'Mixed controls','dual_stick':'Movement + camera','camera':'Movement + camera','text':'Dialogue / text choices'}
    paces={'waits':'Usually waits for choices','real_time':'Action continues while you think','mixed':'Some real-time demands','unknown':'Timing needs checking'}
    coops={'yes':'Native co-op in this edition','no':'Single-player; a friend can share the decisions','unknown':'Co-op details need checking'}
    return inputs.get(g['input'],g['input'].replace('_',' '))+' | '+paces[g['pace']]+' | '+coops.get(g['native_coop'],g['native_coop'])

class BookDoc(SimpleDocTemplate):
    def __init__(self,*a,volume=1,**kw):
        super().__init__(*a,**kw);self.volume=volume;self.locations={};self.case_ends={};self.discussion_locations={}
    def afterFlowable(self,f):
        key=getattr(f,'case_id',None)
        if key:
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(getattr(f,'outline_title',key),key,level=0,closed=False);self.locations[key]=self.page
        discussion=getattr(f,'discussion_id',None)
        if discussion:
            self.canv.bookmarkPage(discussion);self.canv.addOutlineEntry(getattr(f,'outline_title',discussion),discussion,level=0,closed=False);self.discussion_locations[discussion]=self.page
        end=getattr(f,'case_end_id',None)
        if end:self.case_ends[end]=self.page
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
    c.setFillColor(CREAM);c.rect(50,35,w-100,64,stroke=0,fill=1)
    c.setFillColor(BURGUNDY);c.setFont('SansBold',8)
    c.drawString(58,85,CHORUS_LABEL)
    c.setFont('Sans',8.5)
    for row,phrases in enumerate(CHORUS):
        for col,phrase in enumerate(phrases):
            assert pdfmetrics.stringWidth(phrase,'Sans',8.5)<97
            c.drawString(58+col*99,71-row*12,phrase)
    c.setFont('Sans',8);c.setFillColor(GRAY);c.drawString(50,19,'THE GAMES ARE REAL. THE SUMMIT IS FICTION.')
    c.drawRightString(w-50,19,f'{doc.volume} / {doc.page}')
    c.restoreState()

def section(story,title,paragraphs,break_before=False,bookmark=None,style='narrative'):
    if break_before:story.append(PageBreak())
    heading=para(title,'h2')
    if bookmark:heading.discussion_id=bookmark;heading.outline_title='Conversation: '+title
    story.append(heading)
    tail=0;tail_words=0
    if break_before and len(paragraphs)>2:
        for p in reversed(paragraphs):
            tail+=1;tail_words+=len(p.split())
            if tail_words>=140:break
    if tail and tail<len(paragraphs):
        story.extend(para(p,style)for p in paragraphs[:-tail])
        story.append(KeepTogether([para(p,style)for p in paragraphs[-tail:]]))
    else:story.extend(para(p,style)for p in paragraphs)

def source_paras(g):
    out=[para(g['source_note'],'small')]
    for i,url in enumerate(g['source_urls'],1):
        # Line-breakable printed URL plus an actual PDF hyperlink.
        visible=esc(url).replace('/','/<wbr/>').replace('_','_<wbr/>').replace('?','?<wbr/>')
        out.append(Paragraph(f'<link href="{esc(url)}" color="#61275f">Source {i}: {visible}</link>',STYLES['small']))
    return out

def route_grid(n):
    rows=[[para('Mood / emblem','small')]+[para(f'{i+1}. {v}','small')for i,v in enumerate(EMBLEMS)]]
    for row,mood in enumerate(MOODS):
        rows.append([para(f'{row+1}. {mood}','small')]+[para(f'P{40*(n-1)+8*row+c+1:03d}','small')for c in range(8)])
    t=Table(rows,colWidths=[100]+[49]*8,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),CREAM),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d4ccbf')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    return t

def make_story(v,front,known_pages,split_games=(),known_discussions=None):
    n=v['number'];st=[];deep_i,deep=deep_discussion(v);discussion_id=f'D{n:02d}';known_discussions=known_discussions or {}
    st.extend([Spacer(1,25),para('TEN TOES DOWN PRESENTS / THE COALITION EDITION','kicker'),para('The Second Great Butch vs. Stud War','cover'),para('The Panorama of Games for Lillian','sub'),para(f'VOLUME {n} OF SIX','kicker'),para(v['title'],'h1'),para(v['subtitle'],'sub'),Spacer(1,14),para('Forty real games. One coalition. Aiden has already overspent.','body'),para('Fictional wars, adult coalition comedy, reclaimed in-group language and innuendo.','small'),para('New ChatGPT prose under Nolan’s creative direction. The 1967 war is invented history.','small'),para('Coalition Edition 3.0 - 20 September 2026','small'),PageBreak()])
    section(st,'How to find a game in this book',[
        'Each game starts with a short pitch, what you actually do, the controls and pace, the main catch, and a first action to try. These practical sections use plain language. The longer Aiden scene comes after them.',
        'For a fast comparison, read the pitch and main catch on two or three pages. Use the alphabetical index to jump to a title. Choose the full story only when you want the comedy; it is never a prerequisite for understanding the game.',
        'This is an original comic game catalogue inspired by the Aiden ensemble in Ten Toes Down. The source novels remain separate. Game descriptions and catches are research-based editorial notes; the coalition summit and Aiden’s rulings are fiction.',
        'The catalogue ranges across possible fits and clearly marked detours. “Waits” describes the usual decision loop, not a certification that every scene is untimed. The labels mean: A place to start = a promising candidate; Read the catch first = a meaningful obstacle needs checking; A more demanding detour = a narrower or harder option. They describe the game, not the reader. Check the exact edition.',
        'Choose any game directly. Skip any game for any reason. The elaborate route is an optional joke; declining never costs a token. No purchase, download, account or medical information is needed to use this book.',
        'Print on Letter paper at actual size, or fit to A4. Page references use volume / page, which remain valid in the omnibus. For larger type, use the reflowable EPUB. Links and a full alphabetical index sit beside the printed case numbers.'
    ])
    st.append(para('The six departments','h3'))
    for no,label in enumerate(['Suspiciously Interesting People - mysteries and adventures','Taking One’s Turn - strategy and role-playing','Looking Around Before Doing Anything - exploration','Things That Fit Into Other Things - puzzles and construction','People Who Have Something to Tell You - character stories','Bringing a Friend - co-op and shared play'],1):st.append(para(f'{no}. {label}','index'))
    st.append(PageBreak());st.append(para('Choose a game by its name','h1'))
    st.append(para('This is the quick route. Click any title, or turn to its page. Read the short pitch and main catch first; Aiden’s scene follows the practical guide. The case number works across every format.','body'))
    st.append(Paragraph(f'<b>The long conversation:</b> <link href="#{discussion_id}" color="#61275f">{esc(deep["title"])}</link> - page {known_discussions.get(discussion_id,"...")}. {esc(DISCUSSION_TOPICS[n])}.',STYLES['small']))
    if n==1:st.append(Paragraph(f'<b>The historical field guide:</b> <link href="#HISTORY" color="#61275f">Lesbian lives, desire and politics across several histories</link> - page {known_discussions.get("HISTORY","...")}.',STYLES['small']))
    cells=[]
    for g in sorted(v['games'],key=lambda x:x['title'].casefold()):
        cells.append([para(g['id'],'index'),Paragraph(f'<link href="#{g["id"]}" color="#61275f">{esc(g["title"])}</link>',STYLES['index']),para(str(known_pages.get(g['id'],'...')),'index')])
    half=(len(cells)+1)//2
    rows=[cells[i]+(cells[i+half]if i+half<len(cells)else ['','',''])for i in range(half)]
    t=Table(rows,colWidths=[39,176,25]*2,hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#ddd6ce')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]));st.append(t)
    if n==1:
        for title,ps in front['preface']:section(st,title,ps,True)
        st.append(PageBreak());st.append(para('The Coalition Has Created a Committee to Abolish Committees','h1'))
        for title,ps in front['rules']:section(st,title,ps,style='rules')
        section(st,'Twelve optional declarations of personality',[f'{i+1}. {s[0]}. {s[1]}'for i,s in enumerate(front['aspects'])],True)
        section(st,'The incident desk',[f'{i+1}. {s[0]}. {s[1]}'for i,s in enumerate(front['incidents'])],True)
    st.append(PageBreak());st.append(para('A route that knows when to shut up','h1'))
    section(st,'The shortest working procedure',[
        'First name up to three real preferences or vetoes: required speed, camera movement, holds, menus, reading, clue tracking or native co-op. Keep them beside you. The route cannot overrule them.',
        f'You are in Department {n}. Pick one mood row and one emblem column below; neither claims to describe a game feature. That gives a starting case. You can go there now.',
        'For ceremonial excess only, roll four ordinary six-sided dice: 1-2 means minus one; 3-4 means zero; 5-6 means plus one. Add the four results. Add zero, one or two for any already-available wanted drink and wanted snack. Eating is never required.',
        'Begin a browsing session with three imaginary Stamp Tokens. At most once per selection, spend one to add two OR reroll all four dice. You may take an optional funny trait from Book I as your excuse. Never pay a token to refuse a game.',
        'Move that many cases along this department’s forty-case shelf, wrapping around at either end. Read the real catch. If you want one appeal, visit the adjacent case or the same local position in another department; then choose freely or stop. No appeal loops.',
        'The printed full rules, worked example and incident desk are in Volume I. The offline index performs the arithmetic and provides conservative evidence filters. The direct alphabetical index near the front always works without dice.'
    ])
    st.append(route_grid(n));st.append(Spacer(1,10));st.append(para('Local position = 8 × (row - 1) + emblem. Wrap modified position to 1-40. Global case = 40 × (department - 1) + local position.','small'))
    for sec in v['opening']:section(st,sec['title'],sec['paragraphs'],True)
    inter=list(v['interludes'])
    for i,g in enumerate(v['games']):
        st.append(PageBreak());st.append(para(metadata_line(g),'kicker'))
        h=para(g['title'],'case_title');h.case_id=g['id'];h.outline_title=f"{g['id']} - {g['title']}";st.append(h)
        st.append(para('Edition considered: '+g.get('edition_target','See the evidence note for the edition.'),'small'))
        st.append(para(g.get('quick_pitch',g['pleasure']),'quick'))
        st.append(fact_line('What you do.',g.get('what_you_do',g['first'])))
        st.append(para(control_line(g),'small'))
        st.append(fact_line('Main catch.',g.get('watch_for',g['burden'])))
        st.append(fact_line('Why it might click.',g['pleasure']))
        st.append(fact_line('The full catch.',g['burden']))
        st.append(fact_line('Try this first.',g['first']))
        if g['id'] in split_games:
            st.append(Spacer(1,10));st.append(para('Aiden’s complete scene and the source notes follow on the next page.','small'))
            st.append(PageBreak());st.append(para(g['id']+' / THE COMIC SCENE AND SOURCES','kicker'))
            st.append(para(g['title'],'case_title'))
        st.append(Spacer(1,6));st.append(para('AIDEN AT THE SUMMIT / '+g['case_title'],'kicker'))
        st.extend(para(p,'scene')for p in g['scene'])
        st.append(fact_line('Aiden’s verdict.',g['ruling']))
        st.append(Spacer(1,4));st.append(para('Evidence desk / checked 20 September 2026','label'))
        source_items=source_paras(g);source_items[-1].case_end_id=g['id'];st.extend(source_items)
        if (i+1)%10==0 and inter:
            sec=inter.pop(0);section(st,sec['title'],sec['paragraphs'],True,discussion_id if sec is deep else None)
    for sec in inter+v['ending']:section(st,sec['title'],sec['paragraphs'],True)
    if n==1:
        section(st,HISTORY_TITLE,HISTORY_INTRO,True,bookmark='HISTORY')
        st.append(PageBreak());st.append(para('Choose a historical dossier','h2'))
        history_cells=[]
        for h in load_history():
            history_cells.append(Paragraph(f'<link href="#{h["id"]}" color="#61275f"><b>{h["id"]}. {esc(h["title"])}</b></link><br/><font size="8.5">Page {known_discussions.get(h["id"],"...")}</font>',STYLES['index']))
        half=(len(history_cells)+1)//2
        history_rows=[[history_cells[i],history_cells[i+half] if i+half<len(history_cells) else '']for i in range(half)]
        history_table=Table(history_rows,colWidths=[246,246],hAlign='LEFT')
        history_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#ddd6ce')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
        st.append(history_table)
        for h in load_history():
            section(st,h['id']+'. '+h['title'],[h['period']]+h['paragraphs'],True,bookmark=h['id'])
            st.append(fact_line('The question underneath.',h['question']))
            st.append(para('Evidence limit: '+h['caveat'],'small'))
            st.append(para('AIDEN HAS ENTERED THE ARCHIVE / FICTION','kicker'))
            st.extend(para(p,'scene')for p in h['fiction'])
            for c in h['source_records']:
                st.append(para(c['title']+'. Read scope: '+c['read_scope'],'small'))
                visible=esc(c['url']).replace('/','/<wbr/>').replace('_','_<wbr/>')
                st.append(Paragraph(f'<link href="{esc(c["url"])}" color="#61275f">{visible}</link>',STYLES['small']))
        st.append(PageBreak());st.append(para('Cultural reading notes','h1'));st.append(para(CONTEXT_INTRO,'body'))
        for c in cultural_sources():
            st.append(para(c['id']+'. '+c['title'],'h3'));st.append(para(c['note'],'body'));st.append(para('Read scope: '+c['scope'],'small'))
            visible=esc(c['url']).replace('/','/<wbr/>').replace('_','_<wbr/>')
            st.append(Paragraph(f'<link href="{esc(c["url"])}" color="#61275f">{visible}</link>',STYLES['small']))
    st.append(PageBreak());st.append(para('Credits, source limits and the paperwork we actually mean','h2'))
    st.extend(para(p,'credits')for p in front['attribution'])
    st.append(para('Each case names its inspected sources and the limits of those sources. Store descriptions and developer feature declarations are not a playthrough of every route. The companion evidence ledger records editorial tags separately from source declarations. Availability and features may change after the check date.','credits'))
    return st

def write_book(v,front):
    path=OUT/f'Panorama-Volume-{v["number"]:02d}.pdf';loc={};discussion_loc={};split_games=set()
    for attempt in range(3):
        doc=BookDoc(str(path),volume=v['number'],pagesize=(612,792),rightMargin=60,leftMargin=60,topMargin=56,bottomMargin=117,title=f'{TITLE} - Volume {v["number"]}',author=AUTHOR,pageCompression=1)
        doc.build(make_story(v,front,loc,split_games,discussion_loc),onFirstPage=furniture,onLaterPages=furniture)
        if attempt==0:split_games={gid for gid,start in doc.locations.items()if doc.case_ends[gid]>start}
        if attempt==2 and (loc!=doc.locations or discussion_loc!=doc.discussion_locations):raise AssertionError('Index pagination did not converge')
        loc=doc.locations;discussion_loc=doc.discussion_locations
    DISCUSSION_LOCATIONS[v['number']]=discussion_loc
    return path,loc,len(PdfReader(path).pages)

def base_sections(volumes,front):
    # This common linear reading sequence drives Markdown and EPUB.
    yield 'start-here','Read this when you want to choose a game',[(None,'The Coalition Edition is an adult comic edition with reclaimed in-group language, strong profanity, cocaine references and sexual innuendo. The practical game information stays in plain language.'),(None,'On each card: read the short pitch, what you do, controls and pace, main catch, and first try. Aiden’s scene follows the useful information. Use the table of contents to jump directly to a game.'),(None,'Volume 1: mysteries and adventures. Volume 2: strategy and role-playing. Volume 3: exploration. Volume 4: puzzles and building. Volume 5: character stories. Volume 6: co-op and shared play.'),(None,'A place to start is a promising candidate, read the catch first flags a meaningful obstacle, and a detour is a narrower or more demanding option. These are editorial labels, not guarantees. Choose by interest and the stated catch.')]
    for i,(title,ps)in enumerate(front['preface']):yield f'welcome-{i}',title,[(None,p)for p in ps]
    yield 'rules','The Coalition Has Created a Committee to Abolish Committees',[(t,p)for t,ps in front['rules']for p in ps]
    yield 'aspects','Twelve optional declarations of personality',[(None,f'{i+1}. {s[0]}. {s[1]}')for i,s in enumerate(front['aspects'])]
    yield 'incidents','The incident desk',[(None,f'{i+1}. {s[0]}. {s[1]}')for i,s in enumerate(front['incidents'])]
    for v in volumes:
        n=v['number'];yield f'v{n}',f'Volume {n}: {v["title"]}',[(None,v['subtitle'])]
        for i,s in enumerate(v['opening']):yield f'v{n}-open{i}',s['title'],[(None,p)for p in s['paragraphs']]
        inter=list(v['interludes'])
        for i,g in enumerate(v['games']):
            ps=[('In one sentence',g.get('quick_pitch',g['pleasure'])),('What you do',g.get('what_you_do',g['first'])),('How you play',control_line(g)),('Main catch',g.get('watch_for',g['burden'])),('Edition considered',g.get('edition_target','See the evidence note for the edition.')),('Editorial starting point',metadata_line(g)),('Why it might click',g['pleasure']),('The full catch',g['burden']),('Try this first',g['first']),('Aiden at the summit',g['case_title'])]+[(None,p)for p in g['scene']]+[('Aiden’s verdict',g['ruling']),('Evidence desk',g['source_note'])]+[('Source',u)for u in g['source_urls']]
            yield g['id'],f'{g["id"]} - {g["title"]}',ps
            if (i+1)%10==0 and inter:
                s=inter.pop(0);yield f'v{n}-inter{i}',s['title'],[(None,p)for p in s['paragraphs']]
        for i,s in enumerate(inter+v['ending']):yield f'v{n}-end{i}',s['title'],[(None,p)for p in s['paragraphs']]
    yield from history_sections()
    yield 'cultural-sources','Cultural reading notes',[(None,CONTEXT_INTRO)]+[(label,p)for c in cultural_sources()for label,p in [(c['id']+'. '+c['title'],c['note']),('Read scope',c['scope']),('Source',c['url'])]]
    yield 'credits','Credits and source limits',[(None,p)for p in front['attribution']]

def all_sections(volumes,front):
    for sid,title,ps in base_sections(volumes,front):
        yield sid,title,ps+[(CHORUS_LABEL,line)for line in CHORUS_LINES]

def write_text_and_epub(volumes,front):
    secs=list(all_sections(volumes,front));md=[f'# {TITLE}',f'\n{AUTHOR}\n\nThe Coalition Edition 3.0 / {DATE}\n']
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
        conversation_nav='<h2>Historical field guide</h2><p><a href="history-intro.xhtml">'+html.escape(HISTORY_TITLE)+'</a></p><h2>Six long conversations</h2><ol>'+''.join(f'<li><a href="v{v["number"]}-inter{(deep_discussion(v)[0]+1)*10-1}.xhtml">{v["number"]}. {html.escape(DISCUSSION_TOPICS[v["number"]])}</a></li>'for v in volumes)+'</ol>'
        navx='<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1>'+conversation_nav+'<h2>Complete contents</h2><ol>'+''.join(nav)+'</ol></nav></body></html>'
        z.writestr('OEBPS/nav.xhtml',navx)
        opf=f'<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:ttd:panorama:20260920:coalition:3</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title><dc:creator>{html.escape(AUTHOR)}</dc:creator><dc:language>en</dc:language><meta property="dcterms:modified">2026-09-20T00:00:00Z</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="style.css" media-type="text/css"/>'+''.join(manifest)+'</manifest><spine>'+''.join(spine)+'</spine></package>'
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
    books=[];locations={};counts={};discussions=[]
    for v in vols:
        if args.preview and not v['games']:continue
        if args.preview:v=dict(v,games=v['games'][:2])
        path,loc,count=write_book(v,front);books.append(path);locations.update({k:{'volume':v['number'],'page':p}for k,p in loc.items()});counts[path.name]=count;print(path.name,count,flush=True)
        di,deep=deep_discussion(v)
        discussions.append({'id':f'D{v["number"]:02d}','volume':v['number'],'page':DISCUSSION_LOCATIONS[v['number']][f'D{v["number"]:02d}'],'title':deep['title'],'topic':DISCUSSION_TOPICS[v['number']],'words':sum(words(p)for p in deep['paragraphs']),'epub_file':f'v{v["number"]}-inter{(di+1)*10-1}.xhtml','paragraphs':deep['paragraphs']})
    if args.preview:return
    history_index=[{'id':h['id'],'title':h['title'],'period':h['period'],'volume':1,'page':DISCUSSION_LOCATIONS[1][h['id']]}for h in load_history()]
    combined=PdfWriter();offset=0
    for no,b in enumerate(books,1):
        r=PdfReader(b);page_ids={p.indirect_reference.idnum:i for i,p in enumerate(r.pages)}
        for p in r.pages:
            original_annotations=p.pop(NameObject('/Annots'),None)
            combined.add_page(p)
            if original_annotations is not None:p[NameObject('/Annots')]=original_annotations
        parent=combined.add_outline_item(f'Volume {no}',offset)
        for d in discussions:
            if d['volume']==no:d['omnibus_page']=offset+d['page'];combined.add_outline_item('Conversation: '+d['title'],offset+d['page']-1,parent=parent)
        if no==1:
            history_parent=combined.add_outline_item('Historical field guide',DISCUSSION_LOCATIONS[1]['HISTORY']-1,parent=parent)
            for h in history_index:combined.add_outline_item(h['id']+' - '+h['title'],h['page']-1,parent=history_parent)
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
    dump(OUT/'discussion-index.json',discussions);write_cultural_notes();write_history_notes(history_index)
    wc,chapters=write_text_and_epub(vols,front)
    evidence=make_evidence(games)
    corpus={'title':TITLE,'edition':'3.0 - The Coalition Edition','checked':DATE,'scope':'240 editorial candidates, including conditional and detour entries; no full-game accessibility certification','privacy':'No personal or clinical history included','games':games}
    dump(OUT/'game-corpus.json',corpus);dump(OUT/'evidence-ledger.json',evidence);dump(OUT/'page-index.json',locations)
    dump(OUT/'routing-rules.json',{'departments':[{'number':v['number'],'title':v['title']}for v in vols],'moods':MOODS,'emblems':EMBLEMS,'aspects':front['aspects'],'incidents':front['incidents'],'rules':front['rules'],'stamp_tokens':3,'max_modification_actions_per_selection':1,'max_appeals_per_selection':1,'veto_is_free':True})
    summary={'title':TITLE,'games':len(games),'volumes':6,'unique_manuscript_word_count':wc,'word_count_method':'Regex word tokens in single combined Markdown; excludes duplicate PDF introductions, offline app and raw source cache','epub_chapters':chapters,'pdf_pages':counts,'tier_counts':dict(collections.Counter(g['fit_tier']for g in games)),'primary_declaration_records':sum(bool(e['developer_declarations'])for e in evidence),'all_games_have_source_notes':True,'full_playthroughs':0}
    prose=[p for g in games for p in g['scene']]+[g[k]for g in games for k in ATTR_KEYS+['quick_pitch','what_you_do','watch_for']]+[p for v in vols for s in v['opening']+v['interludes']+v['ending']for p in s['paragraphs']]+[p for _,ps in front['preface']+front['rules']for p in ps]+[p for entry in front['aspects']+front['incidents']for p in entry]
    summary['original_comic_and_catalog_prose_word_count']=sum(words(s)for s in prose)
    summary['sustained_dialogues']=[{k:v for k,v in d.items()if k!='paragraphs'}for d in discussions]
    summary['cultural_sources']=len(cultural_sources())
    summary['historical_dossiers']=len(history_index)
    summary['history_field_guide_start_page']=DISCUSSION_LOCATIONS[1]['HISTORY']
    summary['history_source_records']=len({c['url']for h in load_history()for c in h['source_records']})
    summary['historical_field_guide_words']=sum(words(p)for _,_,ps in history_sections()for _,p in ps)
    summary['history_source_prose_words']=sum(words(p)for h in load_history()for p in h['paragraphs'])
    summary['repeated_chorus_uses_per_pdf_page']=15
    summary['epub_chorus_scope']='15 uses at each chapter boundary; screen pages are reflowable'
    summary['repeated_chorus_in_manuscript_word_count']=True
    dump(OUT/'build-report.json',summary)
    import csv
    with(OUT/'game-index.csv').open('w',newline='',encoding='utf-8-sig')as f:
        fields=['id','title','volume','page','input','pace','memory','native_coop','fit_tier','source_urls'];w=csv.DictWriter(f,fields);w.writeheader()
        for g in games:w.writerow({**{k:g[k]for k in fields if k in g},**locations[g['id']],'source_urls':' | '.join(g['source_urls'])})
    (OUT/'Source-Notes.md').write_text('# Source notes\n\nChecked '+DATE+'. Research notes are editorial screening, not full playthroughs. Raw store descriptions are excluded from the publication.\n\n'+'\n\n'.join(f'## {g["id"]}: {g["title"]}\n\n{g["source_note"]}\n\n'+'\n'.join('- '+u for u in g['source_urls'])for g in games),encoding='utf8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
