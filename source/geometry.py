"""Shared parser and analytic bounds for the master's explicit SVG path subset.

Reject unsupported syntax before exports are written. Extrema use ordinary
floating arithmetic; this is not a machine-checked real-number proof.
"""
import re
import math

def geometry(d):
 token=r'[MLCHVZ]|-?(?:\d*\.\d+|\d+)'
 if re.sub(token+r'|[\s,]', '', d):
  raise ValueError('Only explicit M/L/C/H/V/Z commands and finite decimal coordinates are supported.')
 t=re.findall(token,d);i=0;cur=None;start=None;segments=[];closed=0
 def take(n):
  nonlocal i
  if len(t[i:i+n])!=n:raise ValueError('Incomplete path command.')
  v=[float(x) for x in t[i:i+n]]; i+=n
  if not all(math.isfinite(x) for x in v):raise ValueError('Non-finite coordinate.')
  return v
 while i<len(t):
  c=t[i];i+=1
  if c=='M':
   if start is not None:raise ValueError('Unclosed contour.')
   cur=tuple(take(2));start=cur
  elif c in ['L','H','V']:
   if start is None:raise ValueError('A contour must start with M.')
   v=take(2 if c=='L' else 1);end=tuple(v) if c=='L' else ((v[0],cur[1]) if c=='H' else (cur[0],v[0]))
   segments.append((cur,end));cur=end
  elif c=='C':
   if start is None:raise ValueError('A contour must start with M.')
   v=take(6);p1=tuple(v[:2]);p2=tuple(v[2:4]);end=tuple(v[4:]);segments.append((cur,p1,p2,end));cur=end
  elif c=='Z':
   if start is None:raise ValueError('No open contour to close.')
   if cur!=start:segments.append((cur,start))
   cur=start;start=None;closed+=1
  else:raise ValueError(c)
 if start is not None or not closed:raise ValueError('Every path must contain closed contours.')
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

