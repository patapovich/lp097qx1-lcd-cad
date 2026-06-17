#!/usr/bin/env python3
"""Stage C: split outer contour into 4 ear lobes (runs outside body rect). Save ear polys (mm)."""
import numpy as np, cv2, json
from PIL import Image

cnt = np.load("_outer.npy").astype(float)         # outer contour px (N,2) ordered
c = json.load(open("_cal2.json"))
L,R,T,B = c["L"],c["R"],c["T"],c["B"]; sx,sy=c["sx"],c["sy"]; cx,cy=c["cxpx"],c["cypx"]
def MM(p): return ((p[0]-cx)*sx, (cy-p[1])*sy)     # px->mm, Y up

M = 5
x,y = cnt[:,0], cnt[:,1]
outside = (x < L-M) | (x > R+M) | (y < T-M) | (y > B+M)
N = len(cnt)
# contiguous cyclic runs of outside==True
runs=[]; i=0
# rotate so index 0 is inside (so runs don't wrap)
start = np.argmax(~outside)
order = np.roll(np.arange(N), -start)
os = outside[order]
i=0
while i < N:
    if os[i]:
        j=i
        while j<N and os[j]: j+=1
        runs.append(order[i:j]); i=j
    else: i+=1
print(f"{len(runs)} outside-runs; sizes {[len(r) for r in runs]}")

def quad(idx):
    pts = cnt[idx]; mx,my = pts[:,0].mean(), pts[:,1].mean()
    return ("T" if my < cy else "B"), ("L" if mx < cx else "R")

ears={}
for r in runs:
    if len(r) < 30: continue           # skip connector ticks / tiny notches
    vy,vx = quad(r); key=vy+vx
    pts = cnt[r]
    # extend run endpoints onto the body edge for a clean base, then to mm
    poly_px = [tuple(p) for p in pts]
    poly_mm = [MM(p) for p in poly_px]
    span_mm = (max(p[0] for p in poly_mm)-min(p[0] for p in poly_mm),
               max(p[1] for p in poly_mm)-min(p[1] for p in poly_mm))
    ears.setdefault(key, []).append((len(r), poly_px, poly_mm, span_mm))
    print(f"  run -> {key}  n={len(r)}  span {span_mm[0]:.1f}x{span_mm[1]:.1f}mm  centroid mm {MM(pts.mean(axis=0))}")

# keep the largest run per corner
final={}
for k,v in ears.items():
    v.sort(key=lambda t:-t[0]); final[k]=v[0]
print("corners found:", sorted(final))
np.save("_ear_runs.npy", {k:np.array(v[1]) for k,v in final.items()}, allow_pickle=True)
json.dump({k:v[2] for k,v in final.items()}, open("_ears_mm.json","w"))
print("wrote _ears_mm.json + _ear_runs.npy")
