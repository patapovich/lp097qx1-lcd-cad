#!/usr/bin/env python3
"""Stage B: locate outline/bezel/active straight edges by ink projection (central bands)."""
import numpy as np, cv2
from PIL import Image

im = np.asarray(Image.open("clean_front.png").convert("L"))
H, W = im.shape
ink = (im < 175).astype(np.float32)        # crisp lines only (gray/black), no fat antialias
panel = np.load("_panel.npy")
ys, xs = np.where(panel)
x0,x1,y0,y1 = xs.min(), xs.max(), ys.min(), ys.max()

def peaks(proj, thr, minsep):
    idx = np.where(proj > thr)[0]
    groups=[];
    for i in idx:
        if groups and i-groups[-1][-1] <= minsep: groups[-1].append(i)
        else: groups.append([i])
    # weighted center of each group
    return [(int(np.average(g, weights=proj[g])), float(proj[g].sum())) for g in groups]

# vertical lines: project columns over central y-band (avoid ears/ticks/corners)
yb0,yb1 = int(y0+0.30*(y1-y0)), int(y0+0.70*(y1-y0))
colp = ink[yb0:yb1, :].sum(axis=0)
vth = 0.6*(yb1-yb0)
vlines = peaks(colp, vth, 20)
print("central-band height", yb1-yb0)
print("VERTICAL lines (x, strength):")
for x,s in vlines: print(f"   x={x:4d}  s={s:.0f}")

# horizontal lines: project rows over central x-band
xb0,xb1 = int(x0+0.30*(x1-x0)), int(x0+0.70*(x1-x0))
rowp = ink[:, xb0:xb1].sum(axis=1)
hth = 0.6*(xb1-xb0)
hlines = peaks(rowp, hth, 20)
print("HORIZONTAL lines (y, strength):")
for y,s in hlines: print(f"   y={y:4d}  s={s:.0f}")
