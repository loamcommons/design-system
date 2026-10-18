#!/usr/bin/env python3
"""Re-measure untouched reference PNGs. Requires numpy and ImageMagick.
Threshold definitions are operational measurements, not recovery of an exact design.
"""
from pathlib import Path
from collections import deque
import numpy as np, subprocess, hashlib, json
from imagemagick import command
R=Path(__file__).resolve().parent.parent
FILES=['loamcommons-logo.png','loamcommons-icon.png','loam-mark.png','loam-social-preview.png','loam-social-preview-wordmark.png']
def runs(v):
 e=np.diff(np.r_[False,v,False].astype(int));return list(zip(np.where(e==1)[0].tolist(),np.where(e==-1)[0].tolist()))
def bbox(mask):
 y,x=np.where(mask);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def components(m):
 seen=np.zeros(m.shape,bool);result=[]
 for y,x in zip(*np.where(m)):
  if seen[y,x]:continue
  seen[y,x]=True;q=deque([(y,x)]);pts=[]
  while q:
   y,x=q.pop();pts.append((y,x))
   for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
    if 0<=yy<m.shape[0] and 0<=xx<m.shape[1] and m[yy,xx] and not seen[yy,xx]:seen[yy,xx]=True;q.append((yy,xx))
  if len(pts)>20:
   cm=np.zeros(m.shape,bool);v=np.array(pts);cm[v[:,0],v[:,1]]=True;result.append(cm)
 return sorted(result,key=lambda x:bbox(x)[0])
report=[]
for f in FILES:
 p=R/'reference'/f;w,h=map(int,subprocess.check_output(command('identify','-format','%w %h',str(p))).split());a=np.frombuffer(subprocess.check_output(command(str(p),'-depth','8','RGBA:-')),np.uint8).reshape(h,w,4)
 mask=(a[:,:,3]>=128)&(a[:,:,:3].mean(2)<128);cols=[(x,y) for x,y in runs(mask.any(0)) if y-x>3];mk=mask.copy();mk[:,cols[0][1]:]=False;cs=components(mk);L=cs[0];x0,y0,x1,y1=bbox(L);H=y1-y0;yy=int(y0+H*.5);stem=int(L[yy].sum())
 stability=[]
 for threshold in [64,128,192]:
  mm=((a[:,:,3]>=threshold)&(a[:,:,:3].mean(2)<128)) if f==FILES[0] else ((a[:,:,3]>=128)&(a[:,:,:3].mean(2)<threshold))
  mm[:,cols[0][1]+2:]=False;stability.append({'threshold':threshold,'mark_union_bbox':bbox(mm)})
 report.append({'file':f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':[w,h],'alpha_min_max':[int(a[:,:,3].min()),int(a[:,:,3].max())],'L_bbox':[x0,y0,x1,y1],'L_stem_px':stem,'L_stem_over_height':stem/H,'L_width_over_height':(x1-x0)/H,'component_bboxes':[bbox(c) for c in cs],'threshold_sensitivity':stability})
(R/'evidence/reproducible-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print('Measured five original references without modifying them.')
