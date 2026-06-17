#!/usr/bin/env python3
"""Stage D: hole circle-fit (per ear) + bottom-edge profile (BL step)."""
import numpy as np, cv2, json
from PIL import Image

c=json.load(open("_cal2.json")); L,R,T,B=c["L"],c["R"],c["T"],c["B"]
sx,sy=c["sx"],c["sy"]; cx,cy=c["cxpx"],c["cypx"]
def MX(x): return (x-cx)*sx
def MY(y): return (cy-y)*sy
gray = np.asarray(Image.open("clean_front.png").convert("L"))
panel = np.load("_panel.npy")

# approx hole centres (px) from ear-run centroids to seed search windows
runs = np.load("_ear_runs.npy", allow_pickle=True).item()
seeds = {k:(p[:,0].mean(), p[:,1].mean()) for k,p in runs.items()}

holes={}
for k,(hx,hy) in seeds.items():
    win=140
    x0,y0=int(hx-win),int(hy-win)
    sub=gray[max(0,y0):y0+2*win, max(0,x0):x0+2*win]
    ox,oy=max(0,x0),max(0,y0)
    circ=cv2.HoughCircles(sub, cv2.HOUGH_GRADIENT, dp=1, minDist=80,
                          param1=120, param2=18, minRadius=12, maxRadius=24)
    if circ is None:
        print(k,"NO CIRCLE"); continue
    circ=circ[0]
    # pick circle nearest the seed
    cxs,cys=hx-ox,hy-oy
    circ=sorted(circ, key=lambda z:(z[0]-cxs)**2+(z[1]-cys)**2)[0]
    px,py,r=circ[0]+ox, circ[1]+oy, circ[2]
    holes[k]=dict(px=float(px),py=float(py),r=float(r),
                  X=round(float(MX(px)),3),Y=round(float(MY(py)),3),dia=round(float(2*r*sx),3))
    print(f"{k}: center px({px:.1f},{py:.1f}) r={r:.1f}px  -> X={MX(px):.2f} Y={MY(py):.2f} dia={2*r*sx:.3f}mm")
json.dump(holes, open("_holes2.json","w"), indent=1)

# --- bottom-edge profile (BL step) ---
H,W=panel.shape
botprof=[]
for x in range(L, R+1):
    col=np.where(panel[:,x])[0]
    if len(col): botprof.append((x, col.max()))
botprof=np.array(botprof)
# exclude ear columns (where bottom dips far below median = ear protrusion)
fb=int(np.median(botprof[:,1]))
ear_col=botprof[:,1] > fb+25      # ears protrude below
body_bot=botprof[~ear_col]
# raised step = body bottom above (smaller y) than full bottom
print(f"\nfull bottom y={fb} -> Y={MY(fb):.2f}mm")
raised = body_bot[body_bot[:,1] < fb-6]
if len(raised):
    print(f"raised-bottom cols X[{MX(raised[:,0].min()):.1f},{MX(raised[:,0].max()):.1f}] "
          f"plateau Y={MY(int(np.median(raised[:,1]))):.2f}mm  (raise {MY(int(np.median(raised[:,1])))-MY(fb):.2f})")
np.save("_botprof.npy", botprof)
# plot profile mm
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.figure(figsize=(10,3))
plt.plot([MX(x) for x in botprof[:,0]],[MY(y) for y in botprof[:,1]],".",ms=1)
plt.axhline(MY(fb),color="g",lw=.5); plt.title("bottom edge profile (mm)"); plt.xlabel("X"); plt.ylabel("Y")
plt.gca().invert_xaxis(); plt.tight_layout(); plt.savefig("bottom_profile2.png",dpi=90)
print("wrote _holes2.json, bottom_profile2.png")
