"""Structural/content verification plus full-document render sheets for inspection."""
from pathlib import Path
import json,re,hashlib,zipfile,collections,sys
from xml.etree import ElementTree as ET
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw,ImageFont
from build_panorama import load_data,plain
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs'/'ten-toes-down-panorama'
QA=ROOT/'work'/'panorama-qa';QA.mkdir(exist_ok=True)
front,volumes,games=load_data()
def norm(s):return re.sub(r'[^a-z0-9]','',plain(s).lower())
def strip_furniture(s):
    return '\n'.join(line for line in s.splitlines()if not re.match(r'^(TEN TOES DOWN  /  PANORAMA OF GAMES|VOLUME \d$|THE GAMES ARE REAL\. THE MINISTRIES ARE NOT\.|\d / \d+$)',line.strip()))
report={'games':len(games),'cards_checked':0,'paragraphs_checked':0,'pdf_pages':{},'duplicate_long_paragraphs':[],'short_spill_pages':[],'notes':['Rasterization checks renderability; contact sheets and selected full-resolution pages require separate visual inspection.','No full game playthrough is claimed. All game fit tiers are editorial suggestions.']}
alltexts=[];allparas=[]
source_annotations=[];page_offset=0
pageindex=json.loads((OUT/'page-index.json').read_text(encoding='utf8'))
for v in volumes:
    path=OUT/f'Panorama-Volume-{v["number"]:02d}.pdf';reader=PdfReader(path);texts=[p.extract_text()or''for p in reader.pages];alltexts+=texts
    report['pdf_pages'][path.name]=len(texts);joined=norm('\n'.join(strip_furniture(t)for t in texts))
    id_to_page={p.indirect_reference.idnum:i for i,p in enumerate(reader.pages)}
    for i,p in enumerate(reader.pages):
        for ref in p.get('/Annots',[]):
            a=ref.get_object()
            if a.get('/A',{}).get('/URI'):source_annotations.append((page_offset+i,'uri',str(a['/A']['/URI'])))
            elif a.get('/Dest'):source_annotations.append((page_offset+i,'dest',page_offset+id_to_page[a['/Dest'][0].idnum]))
            else:raise AssertionError('Unexpected source annotation')
    page_offset+=len(reader.pages)
    for g in v['games']:
        for s in [*g['scene'],*[g[k]for k in ['quick_pitch','what_you_do','watch_for','pleasure','burden','first','ruling','source_note']]]:
            assert norm(s)in joined,(g['id'],'Missing text',s[:80]);report['paragraphs_checked']+=1
        assert g['id']in texts[pageindex[g['id']]['page']-1]
        allparas.extend(g['scene']);report['cards_checked']+=1
    for sec in v['opening']+v['interludes']+v['ending']:
        for s in sec['paragraphs']:
            assert norm(s)in joined,(v['number'],'Missing scene text',s[:80]);report['paragraphs_checked']+=1;allparas.append(s)
    assert all(len(t.strip())>35 for t in texts),'Empty page'
    for i,t in enumerate(texts):
        wc=len(strip_furniture(t).split())
        if 5<wc<85 and i>0:report['short_spill_pages'].append({'volume':v['number'],'page':i+1,'words':wc,'start':strip_furniture(t)[:85]})
    # Render every unique volume page, saving contact sheets in groups of sixteen.
    pdf=pdfium.PdfDocument(path);thumbs=[]
    for i in range(len(pdf)):
        img=pdf[i].render(scale=.56).to_pil().convert('RGB')
        assert img.getextrema()!=((255,255),(255,255),(255,255))
        tile=Image.new('RGB',(355,474),'#e4dfd7');img.thumbnail((343,444));tile.paste(img,((355-img.width)//2,7));ImageDraw.Draw(tile).text((9,453),f'Volume {v["number"]} / page {i+1}',fill='black');thumbs.append(tile)
        if len(thumbs)==16 or i==len(pdf)-1:
            sheet=Image.new('RGB',(1420,474*((len(thumbs)+3)//4)),'#d5cec5')
            for k,tile in enumerate(thumbs):sheet.paste(tile,((k%4)*355,(k//4)*474))
            name=QA/f'volume-{v["number"]:02d}-sheet-{i//16+1:02d}.jpg';sheet.save(name,quality=90);thumbs=[]
    print(f'Validated and rendered volume {v["number"]}: {len(texts)} pages',flush=True)
omni=PdfReader(OUT/'Panorama-Complete-Omnibus.pdf');assert len(omni.pages)==len(alltexts)
assert all((p.extract_text()or'')==t for p,t in zip(omni.pages,alltexts))
report['omnibus_page_sequence_matches_volumes']=True
omni_ids={p.indirect_reference.idnum:i for i,p in enumerate(omni.pages)};omni_annotations=[]
for i,p in enumerate(omni.pages):
    for ref in p.get('/Annots',[]):
        a=ref.get_object()
        if a.get('/A',{}).get('/URI'):omni_annotations.append((i,'uri',str(a['/A']['/URI'])))
        elif a.get('/Dest'):omni_annotations.append((i,'dest',omni_ids[a['/Dest'][0].idnum]))
        else:raise AssertionError('Unexpected omnibus annotation')
assert source_annotations==omni_annotations,'Omnibus link targets differ'
report['omnibus_links_preserved']={'all_annotations':len(omni_annotations),'internal_targets':sum(t=='dest'for _,t,_ in omni_annotations),'external_source_links':sum(t=='uri'for _,t,_ in omni_annotations)}
counts=collections.Counter(norm(p)for p in allparas if len(p.split())>=55)
report['duplicate_long_paragraphs']=[{'count':c,'prefix':p[:90]}for p,c in counts.items()if c>1]
assert not report['duplicate_long_paragraphs'],'Long repeated prose'
with zipfile.ZipFile(OUT/'Ten-Toes-Down-Panorama.epub')as z:
    assert z.namelist()[0]=='mimetype'and z.getinfo('mimetype').compress_type==zipfile.ZIP_STORED
    for name in z.namelist():
        if name.endswith(('.xhtml','.opf','.xml')):ET.fromstring(z.read(name))
    ns={'o':'http://www.idpf.org/2007/opf','x':'http://www.w3.org/1999/xhtml'}
    opf=ET.fromstring(z.read('OEBPS/content.opf'));items={x.attrib['id']:x.attrib['href']for x in opf.findall('o:manifest/o:item',ns)}
    for item in opf.findall('o:spine/o:itemref',ns):assert 'OEBPS/'+items[item.attrib['idref']]in z.namelist()
    for name in z.namelist():
        if name.endswith('.xhtml'):
            for a in ET.fromstring(z.read(name)).findall('.//x:a',ns):
                href=a.attrib.get('href','')
                if not href.startswith(('https:','http:','#')):assert 'OEBPS/'+href.split('#')[0]in z.namelist(),href
    report['epub_xml_manifest_spine_links']='passed'
report['pdf_unique_pages_rendered']=len(alltexts)
report['publication_files_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(OUT.iterdir())if p.is_file()and p.name not in ['validation-report.json','publication-receipt.json','SHA256SUMS']}
(OUT/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items()if k!='publication_files_sha256'},indent=2))
