#!/usr/bin/env python3
"""Stage B2: body rectangle edges via mask-boundary medians; BL step; bezel; calibrate."""
import numpy as np, cv2, json
from PIL import Image

panel = np.load("_panel.npy")
H, W = panel.shape
im = np.asarray(Image.open("clean_front.png").convert("L"))

# per-row left/right boundary, per-col top/bottom boundary of the filled mask
rows = np.where(panel.any(axis=1))[0]
cols = np.where(panel.any(axis=0))[0]
leftb  = np.array([np.argmax(panel[y])            for y in rows])
rightb = np.array([W-1-np.argmax(panel[y][::-1])  for y in rows])
topb   = np.array([np.argmax(panel[:,x])          for x in cols])
botb   = np.array([H-1-np.argmax(panel[:,x][::-1])for x in cols])

# body edges = median (ears are localized minority -> median = rectangle edge)
L = int(np.median(leftb)); R = int(np.median(rightb))
T = int(np.median(topb));  B = int(np.median(botb))
print(f"body rect px: L={L} R={R} T={T} B={B}  W={R-L} H={B-T}")

sx = 167.12/(R-L); sy = 208.88/(B-T)   # mm per px
cxpx, cypx = (L+R)/2, (T+B)/2
print(f"scale mm/px x={sx:.5f} y={sy:.5f}  (px/mm {1/sx:.3f},{1/sy:.3f})  center px ({cxpx:.1f},{cypx:.1f})")

def topx(x): return (x-cxpx)*sx          # px x -> mm (X right)
def topy(y): return (cypx-y)*sy          # px y -> mm (Y up)

# --- BL step: bottom boundary (max-y) vs x, left third ---
# botb indexed by cols; map col index -> x
xb = cols
# raised step shows as botb smaller (higher up) for left x. Full bottom = max botb (majority).
full_bot = int(np.median(botb))
# find x-range where bottom is raised >~5px above full
raised = botb < (full_bot - 5)
# restrict to body interior x (ignore ear columns near corners)
inside = (xb > L+30) & (xb < R-30)
rstep = raised & inside
if rstep.any():
    xs_step = xb[rstep]
    # raised plateau y
    plateau = int(np.median(botb[rstep]))
    print(f"BL step: raised bottom present x_px[{xs_step.min()},{xs_step.max()}] plateau_y={plateau}")
    print(f"   -> mm: bottom raised to Y={topy(plateau):.2f} for X in [{topx(xs_step.min()):.1f},{topx(xs_step.max()):.1f}], full bottom Y={topy(full_bot):.2f}")
else:
    print("BL step: none detected")

# report body corners in mm
print(f"OUTLINE mm: X[{topx(L):.2f},{topx(R):.2f}] Y[{topy(B):.2f},{topy(T):.2f}]  ->  {(R-L)*sx:.2f} x {(B-T)*sy:.2f}")

cal = dict(L=L,R=R,T=T,B=B,sx=sx,sy=sy,cxpx=cxpx,cypx=cypx,full_bot=full_bot)
json.dump(cal, open("_cal2.json","w"), indent=1)
print("wrote _cal2.json")
