#!/usr/bin/env python3
"""Finite artifact audit: exact path identity and analytic cubic extrema, not reader validation."""
from pathlib import Path
import json,re,math,hashlib,subprocess,struct,sys,xml.etree.ElementTree as ET
from imagemagick import command
ROOT=Path(__file__).resolve().parent.parent
M=json.loads((ROOT/'source/master.json').read_text());NS={'s':'http://www.w3.org/2000/svg'}

def geometry(d):
 t=re.findall(r'[MLCHVZ]|-?(?:\d*\.\d+|\d+)',d);i=0;cur=None;start=None;segments=[];closed=0
 def take(n):
  nonlocal i
  v=[float(x) for x in t[i:i+n]]; i+=n
  assert all(math.isfinite(x) for x in v)
  return v
 while i<len(t):
  c=t[i];i+=1
  if c=='M':
   assert start is None,'unclosed contour'
   cur=tuple(take(2));start=cur
  elif c in ['L','H','V']:
   v=take(2 if c=='L' else 1);end=tuple(v) if c=='L' else ((v[0],cur[1]) if c=='H' else (cur[0],v[0]))
   segments.append((cur,end));cur=end
  elif c=='C':
   v=take(6);p1=tuple(v[:2]);p2=tuple(v[2:4]);end=tuple(v[4:]);segments.append((cur,p1,p2,end));cur=end
  elif c=='Z':
   if cur!=start:segments.append((cur,start))
   cur=start;start=None;closed+=1
  else:raise ValueError(c)
 assert start is None and closed
 return segments,closed

def bounds(segments):
 vals=[[],[]]
 for seg in segments:
  for k in [0,1]:
   q=[p[k] for p in seg];vals[k]+=q[:1]+q[-1:]
   if len(q)==4:
    a=-q[0]+3*q[1]-3*q[2]+q[3]; b=2*(q[0]-2*q[1]+q[2]);c=q[1]-q[0]
    roots=[]
    if abs(a)<1e-12:
     if abs(b)>1e-12:roots=[-c/b]
    elif b*b-4*a*c>=0:
     disc=math.sqrt(b*b-4*a*c); roots=[(-b+disc)/(2*a),(-b-disc)/(2*a)]
    for x in roots:
     if 0<x<1:vals[k].append((1-x)**3*q[0]+3*(1-x)**2*x*q[1]+3*(1-x)*x*x*q[2]+x**3*q[3])
 return [min(vals[0]),min(vals[1]),max(vals[0]),max(vals[1])]

def main():
 info={g:{'bounds':bounds(geometry(d)[0]),'closed_contours':geometry(d)[1],'cubic_segments':sum(len(s)==4 for s in geometry(d)[0]),'path_sha256':hashlib.sha256(d.encode()).hexdigest()} for g,d in M['paths'].items()}
 # The m's two inner arches are translations, so equal aperture construction is explicit.
 mcurves=[s for s in geometry(M['paths']['m'])[0] if len(s)==4]
 right=mcurves[4:6];left=mcurves[6:8]
 assert len(right)==len(left)==2
 for r,l in zip(right,left):
  assert all(abs((rp[0]-lp[0])-612.5)<1e-8 and abs(rp[1]-lp[1])<1e-8 for rp,lp in zip(r,l))
 assert 612.5-233==1225-845.5==379.5
 originals=json.loads((ROOT/'evidence/source-inventory.json').read_text())
 for item in originals:
  p=ROOT/'reference'/item['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],'source changed'
 manifest=json.loads((ROOT/'evidence/build-manifest.json').read_text())
 assert manifest['master_sha256']==hashlib.sha256((ROOT/'source/master.json').read_bytes()).hexdigest()
 expected_files={i['path'] for i in manifest['assets']}
 actual_files={str(p.relative_to(ROOT)) for folder in ['svg','comparison','png'] for p in (ROOT/folder).iterdir() if p.is_file()}
 assert expected_files==actual_files,'stale or unrecorded export'
 for item in manifest['assets']:
  p=ROOT/item['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
  if 'render_input' in item:
   ri=item['render_input'];assert hashlib.sha256((ROOT/ri['source_svg']).read_bytes()).hexdigest()==ri['source_sha256']
 receipts=[]
 for p in sorted(list((ROOT/'svg').glob('*.svg'))+list((ROOT/'comparison').glob('*.svg'))):
  tree=ET.fromstring(p.read_text());vb=list(map(float,tree.attrib['viewBox'].split()));ids={}
  assert tree.attrib['preserveAspectRatio']=='xMidYMid meet'
  assert len(tree.findall('.//s:text',NS))==0
  for node in tree.findall('.//s:path',NS):
   g=node.attrib['id'].removeprefix('shape-');assert node.attrib['d']==M['paths'][g];ids[node.attrib['id']]=g
  assert sum(g=='L' for g in ids.values())==1
  for use in tree.findall('.//s:use',NS):assert use.attrib['href'][1:] in ids
  for e in tree.iter():assert e.tag not in ['{'+NS['s']+'}image','{'+NS['s']+'}script','{'+NS['s']+'}foreignObject']
  name=p.stem.replace('-reverse','').replace('-square','');d=M['layouts'][name];bs=[]
  # Check actual serialized transforms, not just independently recomputed bounds.
  fmt=lambda n:format(n,'.9g')
  expected_w=d['height']+2*d['padding'] if '-square' in p.stem else d['width']+2*d['padding']
  assert abs(vb[2]-expected_w)<1e-6
  outer=tree.find('s:g',NS);xp=(expected_w-d['width'])/2
  assert outer.attrib=={'fill':M['colors']['reverse' if '-reverse' in p.stem else 'ink'],'fill-rule':'evenodd','transform':f'translate({fmt(xp)} {fmt(d["padding"])})'}
  mark=outer.find('s:g[@id="mark"]',NS);assert mark.attrib['transform']==f'scale({fmt(d["mark_scale"])})'
  assert [u.attrib['href'] for u in mark]==['#shape-'+g for g in d['mark']]
  if d['word']:
   word=outer.find('s:g[@id="word"]',NS)
   assert word.attrib['transform']==f'translate({fmt(d["text_x"])} {fmt(d["text_y"])}) scale({fmt(d["text_scale"])})'
   assert [u.attrib for u in word]==[{'href':'#shape-'+g,'transform':f'translate({fmt(x)} 0)'} for g,x in M['words'][d['word']]]
  for g in d['mark']:
   b=info[g]['bounds'];bs.append([v*d['mark_scale'] for v in b])
  if d['word']:
   for g,x in M['words'][d['word']]:
    b=info[g]['bounds'];s=d['text_scale'];bs.append([(b[0]+x)*s+d['text_x'],b[1]*s+d['text_y'],(b[2]+x)*s+d['text_x'],b[3]*s+d['text_y']])
  ink=[min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)]
  assert ink[0]>=-1e-6 and ink[1]>=-1e-6 and ink[2]<=d['width']+1e-6 and ink[3]<=d['height']+1e-6,(name,ink)
  assert abs((vb[3]-d['height'])/2-d['padding'])<1e-6
  receipts.append({'file':str(p.relative_to(ROOT)),'ink_bounds':ink,'viewBox':vb,'shared_L_exact':True})
 pngs=[]
 for p in sorted((ROOT/'png').glob('*.png')):
  b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',b[16:24]);expected=int(p.stem.split('-')[-1]);assert w==expected
  if '-mark' in p.stem:assert w==h
  color_type=b[25];assert color_type in (4,6),'alpha required'
  rgba=subprocess.check_output(command(str(p),'-depth','8','RGBA:-'));alpha=rgba[3::4];assert alpha[0]==0 and max(alpha)==255
  expected_color=(255,255,255) if '-reverse-' in p.name else (21,21,21)
  opaque_colors={(r,g,b) for r,g,b,a in zip(rgba[0::4],rgba[1::4],rgba[2::4],alpha) if a==255}
  assert opaque_colors=={expected_color},(p,opaque_colors)
  # Guard transparent outer edges in every derived raster.
  assert all(v==0 for v in alpha[:w]+alpha[-w:]+alpha[::w]+alpha[w-1::w])
  pngs.append({'file':str(p.relative_to(ROOT)),'size':[w,h],'alpha':True,'clear_border':True,'opaque_color':expected_color})
 result={'claim':'Finite generated artifact integrity; not a proof of perception or renderer equivalence','source_hashes_unchanged':True,'m_equal_counter_and_arch_constraint':True,'glyphs':info,'svg':receipts,'png':pngs,'tool_versions':{'python':__import__('sys').version.split()[0],'librsvg':subprocess.check_output(['rsvg-convert','--version']).decode().strip(),'imagemagick':subprocess.check_output(command('-version')).decode().splitlines()[0]},'result':'PASS'}
 if '--check' not in sys.argv:
  (ROOT/'evidence/verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(f'PASS: {len(receipts)} SVGs, {len(pngs)} PNGs; all original hashes unchanged')
if __name__=='__main__':main()
