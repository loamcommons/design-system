from pathlib import Path
import json,base64,subprocess
R=Path(__file__).resolve().parent.parent;M=json.loads((R/'source/master.json').read_text());raw=base64.b64encode((R/'reference/loamcommons-logo.png').read_bytes()).decode()
# Crop by viewport only. The original PNG bytes remain intact inside the SVG.
def old(y,opacity=1):return f'<svg x="35" y="{y}" width="1501" height="191" viewBox="520 272 1501 191"><image width="2172" height="724" opacity="{opacity}" href="data:image/png;base64,{raw}"/></svg>'
def new(y,fill='#151515',opacity=1):return '<g fill="'+fill+'" fill-rule="evenodd" opacity="'+str(opacity)+'" transform="translate(35 '+str(y+68.04)+') scale(.12)">'+''.join('<path d="'+M['paths'][g]+'" transform="translate('+str(x)+' 0)"/>' for g,x in M['words']['loam commons'])+'</g>'
def t(y,x):return f'<text x="35" y="{y}" font-family="Arial,sans-serif" font-size="18">{x}</text>'
s='<svg xmlns="http://www.w3.org/2000/svg" width="1580" height="920"><rect width="1580" height="920" fill="white"/>'+t(35,'Original alpha artwork — 120 px nominal x-height')+old(65)+t(325,'Reconstructed outlines — same x-height and source-derived glyph origins')+new(355)+t(615,'Overlay: original black at 35% opacity; reconstruction blue at 55% (diagnostic colors only)')+old(645,.35)+new(645,'#0065cc',.55)+t(900,'Measured original o side stroke: 29/120 = .242 x-height. Master: .241. Original l: 32/120 = .267. Master: .267.')+'</svg>'
(R/'evidence/type-overlay.svg').write_text(s);subprocess.run(['rsvg-convert',str(R/'evidence/type-overlay.svg'),'-o',str(R/'evidence/type-overlay.png')],check=True)
