from pathlib import Path
import json,base64,subprocess
R=Path(__file__).resolve().parent.parent;M=json.loads((R/'source/master.json').read_text())
def img(name,x,y,scale=1,reverse=False,square=False):
 folder='comparison' if name.startswith('comparison') else 'svg';suffix=('-reverse' if reverse else '')+('-square' if square else '');raw=(R/folder/(name+suffix+'.svg')).read_bytes();d=M['layouts'][name];w=(d['height'] if square else d['width'])+2*d['padding'];h=d['height']+2*d['padding']
 return f'<image x="{x}" y="{y}" width="{w*scale}" height="{h*scale}" href="data:image/svg+xml;base64,{base64.b64encode(raw).decode()}"/>'
def text(x,y,s,size=18,color='#151515'):return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}">{s}</text>'
s='<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1400"><rect width="1500" height="1400" fill="white"/>'
s+=text(40,45,'REVISED FAMILY — SAME TWO ARRANGEMENTS',26)
s+=text(40,80,'A and B below are matched at a 100 px lettering x-height. Geometry shared; no L-specific cut.')
s+=text(40,135,'A · original Commons proportions restored',18)+img('comparison-symbol-beside',40,155,100/396)
s+=text(900,135,'B · diagonal clearance opened',18)+img('loam-wordmark',870,230,100/880)
s+=text(40,555,'One LC / L geometry',20)+img('loamcommons-mark',40,585,.15,False,True)+img('loam-mark',290,585,.15,False,True)
s+=text(650,555,'Commons · corrected equal m counters',20)+img('loamcommons-wordmark',625,610,.125)
s+=text(40,855,'Actual-size specimens: screen minima. Do not infer physical size from an image viewer.',18)
s+=img('loam-mark',40,895,24/1400,False,True)+img('loamcommons-mark',110,884,48/1400,False,True)
s+=img('comparison-symbol-beside',230,875,40/1000)+img('loam-wordmark',470,885,32/1022)+img('loamcommons-wordmark',800,870,48/1000)
s+=text(40,975,'L 24 / LC 48 px canvas',14)+text(230,975,'A · 40 px ink',14)+text(470,975,'B · 32 px ink',14)+text(800,975,'Commons · 48 px ink',14)
s+='<rect x="0" y="1010" width="1500" height="390" fill="#151515"/>'
s+=text(40,1050,'Same paths in reverse',18,'white')
s+=img('loam-mark',40,1105,24/1400,True,True)+img('loamcommons-mark',110,1094,48/1400,True,True)+img('comparison-symbol-beside',230,1085,40/1000,True)+img('loam-wordmark',470,1095,32/1022,True)+img('loamcommons-wordmark',800,1080,48/1000,True)
s+=img('loam-wordmark',40,1200,.1,True)+text(680,1240,'Measured minimum L–o clearance: 92.2 / H1000',18,'white')+text(680,1270,'Shared LC channel: 48 / H1000',18,'white')+text(680,1300,'No asserted human recognition validation',18,'white')
s+='</svg>'
(R/'evidence/final-review.svg').write_text(s);subprocess.run(['rsvg-convert',str(R/'evidence/final-review.svg'),'-o',str(R/'evidence/final-review.png')],check=True)
