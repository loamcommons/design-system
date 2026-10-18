#!/usr/bin/env python3
"""Build outlined SVGs and optional PNGs from master.json. No fonts/network needed.
Usage: python3 source/build.py [--render | --check]
Requires Python >=3.10; --render additionally requires rsvg-convert.
"""
from pathlib import Path
import json, hashlib, subprocess, sys
from geometry import geometry
ROOT=Path(__file__).resolve().parent.parent
MASTER=json.loads((ROOT/'source/master.json').read_text())
NS='http://www.w3.org/2000/svg'

def num(v):
    return format(v,'.9g')

def svg(name,color='ink',square=False):
    d=MASTER['layouts'][name]; p=d['padding']; w=d['width']; h=d['height']
    if square:
        assert d['word'] is None
        vw=vh=h+2*p; xpad=(vw-w)/2
    else:
        vw=w+2*p; vh=h+2*p; xpad=p
    title={'loam-mark':'Loam L mark','loamcommons-mark':'Loam Commons LC monogram','loam-wordmark':'Loam','loamcommons-wordmark':'Loam Commons','comparison-symbol-beside':'Comparison A: L symbol beside loam'}[name]
    used=list(d['mark'])+([g for g,_ in MASTER['words'][d['word']]] if d['word'] else [])
    defs=''.join(f'<path id="shape-{g}" d="{MASTER["paths"][g]}"/>' for g in dict.fromkeys(used))
    uses=''.join(f'<use href="#shape-{g}"/>' for g in d['mark'])
    content=f'<g id="mark" transform="scale({num(d["mark_scale"])})">{uses}</g>'
    if d['word']:
        letters=''.join(f'<use href="#shape-{g}" transform="translate({num(x)} 0)"/>' for g,x in MASTER['words'][d['word']])
        content+=f'<g id="word" transform="translate({num(d["text_x"])} {num(d["text_y"])}) scale({num(d["text_scale"])})">{letters}</g>'
    return f'''<svg xmlns="{NS}" width="{num(vw)}" height="{num(vh)}" viewBox="0 0 {num(vw)} {num(vh)}" role="img" aria-labelledby="title" preserveAspectRatio="xMidYMid meet">
<title id="title">{title}</title>
<desc>Loam identity master 1.0.0. Custom outlined lettering. Generated from source/master.json; all L instances share one path. Transparent background.</desc>
<defs>{defs}</defs>
<g fill="{MASTER['colors'][color]}" fill-rule="evenodd" transform="translate({num(xpad)} {num(p)})">{content}</g>
</svg>\n'''

def main():
    for path in MASTER['paths'].values():
        geometry(path)
    for folder in ['svg','png','comparison']:(ROOT/folder).mkdir(exist_ok=True)
    manifest=[]; render_inputs={}
    check='--check' in sys.argv
    if check and '--render' in sys.argv:
        raise SystemExit('Choose --check or --render, not both.')
    for name in MASTER['layouts']:
        folder='comparison' if name.startswith('comparison') else 'svg'
        for color,suffix in [('ink',''),('reverse','-reverse')]:
            p=ROOT/folder/(name+suffix+'.svg')
            content=svg(name,color)
            if check:
                assert p.read_text()==content, f'Stale SVG: {p.relative_to(ROOT)}'
            else:
                p.write_text(content)
            manifest.append(p)
            if MASTER['layouts'][name]['word'] is None:
                q=ROOT/folder/(name+suffix+'-square.svg')
                content=svg(name,color,True)
                if check:
                    assert q.read_text()==content, f'Stale SVG: {q.relative_to(ROOT)}'
                else:
                    q.write_text(content)
                manifest.append(q)
    if check:
        print(f'PASS: {len(manifest)} SVGs match the current generator and master')
        return
    if '--render' in sys.argv:
        for name,sizes in [('loam-mark',[24,48,256,512]),('loamcommons-mark',[48,96,256,512])]:
            for color in ['','-reverse']:
                for size in sizes:
                    p=ROOT/'png'/f'{name}{color}-{size}.png'
                    subprocess.run(['rsvg-convert','--width',str(size),'--height',str(size),str(ROOT/'svg'/f'{name}{color}-square.svg'),'-o',str(p)],check=True)
                    manifest.append(p)
                    source=ROOT/'svg'/f'{name}{color}-square.svg'
                    render_inputs[str(p.relative_to(ROOT))]={'source_svg':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'width':size,'height':size}
        for name,widths in [('loam-wordmark',[144,288,640,1280]),('loamcommons-wordmark',[316,632,1280,2560])]:
            for color in ['','-reverse']:
                for width in widths:
                    p=ROOT/'png'/f'{name}{color}-{width}.png'
                    subprocess.run(['rsvg-convert','--width',str(width),str(ROOT/'svg'/f'{name}{color}.svg'),'-o',str(p)],check=True)
                    manifest.append(p)
                    source=ROOT/'svg'/f'{name}{color}.svg'
                    render_inputs[str(p.relative_to(ROOT))]={'source_svg':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'width':width,'height':'derived aspect ratio'}
    receipt=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in manifest]
    for item in receipt:
        if item['path'] in render_inputs:item['render_input']=render_inputs[item['path']]
    bundle={'master_sha256':hashlib.sha256((ROOT/'source/master.json').read_bytes()).hexdigest(),'assets':receipt}
    (ROOT/'evidence/build-manifest.json').write_text(json.dumps(bundle,indent=2)+'\n')
    print(f'Built {len(manifest)} assets from one master.json')
if __name__=='__main__': main()
