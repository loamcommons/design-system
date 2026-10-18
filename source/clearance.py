#!/usr/bin/env python3
"""Adaptive convex-hull distance bounds for finite Bezier boundary pairs.
Numerical certificate under floating arithmetic; not a machine-checked real proof.
"""
import math,heapq,itertools,json
from pathlib import Path
from geometry import geometry
R=Path(__file__).resolve().parent.parent

def box(p):return (min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p))
def lower(a,b):
 a=box(a);b=box(b);return math.hypot(max(0,a[0]-b[2],b[0]-a[2]),max(0,a[1]-b[3],b[1]-a[3]))
def split(p):
 levels=[p]
 while len(levels[-1])>1:levels.append(tuple(((a[0]+b[0])/2,(a[1]+b[1])/2) for a,b in zip(levels[-1],levels[-1][1:])))
 return tuple(x[0] for x in levels),tuple(x[-1] for x in levels[::-1])
def mid(p):return split(p)[0][-1]
def extent(p):b=box(p);return math.hypot(b[2]-b[0],b[3]-b[1])
def clearance(a,b,tol=.01):
 heap=[];count=itertools.count();hi=math.inf
 for p in a:
  for q in b:
   hi=min(hi,math.dist(mid(p),mid(q)),*(math.dist(u,v) for u in (p[0],p[-1]) for v in (q[0],q[-1])))
   heapq.heappush(heap,(lower(p,q),next(count),p,q))
 while heap:
  lo,_,p,q=heapq.heappop(heap)
  if hi-lo<=tol:return {'lower':round(lo,4),'upper':round(hi,4),'tolerance':tol}
  if lo>=hi:continue
  children=[(x,q) for x in split(p)] if extent(p)>=extent(q) else [(p,x) for x in split(q)]
  for pp,qq in children:
   hi=min(hi,math.dist(mid(pp),mid(qq)))
   lb=lower(pp,qq)
   if lb<hi:heapq.heappush(heap,(lb,next(count),pp,qq))
 raise RuntimeError('empty queue')
def mapped(seg,s=1,x=0,y=0):return [tuple((a*s+x,b*s+y) for a,b in p) for p in seg]
def main():
 m=json.loads((R/'source/master.json').read_text());L=geometry(m['paths']['L'])[0];C=geometry(m['paths']['C'])[0];o=geometry(m['paths']['o'])[0][:4]
 old=clearance(L,mapped(o,.88,800,120));new=clearance(L,mapped(o,.88,m["layouts"]["loam-wordmark"]["text_x"],120));lc=clearance(L,C)
 result={'method':'adaptive Bezier convex-hull lower bound, evaluated-point upper bound; ordinary binary floating arithmetic','L_to_o_at_x800':old,'L_to_o_final':new,'L_to_C':lc,'units':'L height=1000'}
 (R/'evidence/clearance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
