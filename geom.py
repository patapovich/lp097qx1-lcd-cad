#!/usr/bin/env python3
"""Consolidate clean-traced geometry -> geometry.json (center datum, mm)."""
import numpy as np, cv2, json, math

c=json.load(open("_cal2.json")); L,R,T,B=c["L"],c["R"],c["T"],c["B"]
sx,sy=c["sx"],c["sy"]; cx,cy=c["cxpx"],c["cypx"]
def MX(x): return (x-cx)*sx
def MY(y): return (cy-y)*sy
HW,HH = 167.12/2, 208.88/2     # =83.56,104.44

# ---- bezel rectangle (inner rounded rect) from clean image ----
g=np.asarray(__import__("PIL.Image",fromlist=["Image"]).open("clean_front.png").convert("L"))
ink=(g<175).astype(np.uint8)
cnts,_=cv2.findContours(ink,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
bez=None
for ct in cnts:
    a=cv2.contourArea(ct)
    if 5.0e6 < a < 7.2e6:
        x,y,w,h=cv2.boundingRect(ct)
        if x>L+10 and x+w<R-10:    # strictly inside outline
            bez=(x,y,w,h); break
if bez:
    x,y,w,h=bez
    bz=dict(W=round(w*sx,3),H=round(h*sy,3),cx=round(MX(x+w/2),3),cy=round(MY(y+h/2),3))
    print("BEZEL detected:",bz)
else:
    bz=dict(W=151.608,H=201.01,cx=-1.27,cy=-0.86); print("BEZEL fallback table")

# active area: datasheet size, offset relative to bezel (active centered in bezel window approx)
act=dict(W=147.456,H=196.608,cx=bz["cx"]-0.03,cy=bz["cy"]-0.03)

# ---- outline polygon: rect + R0.5 corners + BL raised step + ramp ----
R0=0.5
BL_Y=-103.48; RAMP_HI=-65.8; RAMP_LO=-62.7    # raised bottom-left + ramp (measured)
def arc(cx0,cy0,a0,a1,n=8):
    return [(cx0+R0*math.cos(math.radians(a)),cy0+R0*math.sin(math.radians(a)))
            for a in np.linspace(a0,a1,n)]
outline=[]
outline+=arc(HW-R0, HH-R0, 0, 90)          # TR corner
outline+=arc(-HW+R0, HH-R0, 90,180)        # TL corner
outline+=arc(-HW+R0, BL_Y+R0,180,270)      # BL corner (at raised bottom)
outline+=[(RAMP_HI, BL_Y),(RAMP_LO,-HH)]   # raised flat end -> ramp down to full bottom
outline+=arc(HW-R0,-HH+R0,270,360)         # BR corner
print(f"outline {len(outline)} pts; BL raised Y={BL_Y} ramp X[{RAMP_HI},{RAMP_LO}]")

# ---- ears: close each traced arc along its body edge ----
runs=np.load("_ear_runs.npy",allow_pickle=True).item()
EDGE={"TL":("x",-HW),"TR":("y",HH),"BL":("y",BL_Y),"BR":("y",-HH)}  # body edge each ear attaches to
ears={}
for k,p in runs.items():
    pts=[(MX(px),MY(py)) for px,py in p]
    ax,ev=EDGE[k]
    # snap endpoints onto the body edge so the lobe closes flush
    def snap(pt):
        x,y=pt
        return (x,ev) if ax=="y" else (ev,y)
    pts=[snap(pts[0])]+pts[1:-1]+[snap(pts[-1])]
    ears[k]=[[round(x,3),round(y,3)] for x,y in pts]
    xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
    print(f"ear {k}: {len(pts)}pts  X[{min(xs):.1f},{max(xs):.1f}] Y[{min(ys):.1f},{max(ys):.1f}]")

# ---- holes: measured centers, nominal dia 2.40 ----
h2=json.load(open("_holes2.json"))
holes={k:[round(v["X"],3),round(v["Y"],3)] for k,v in h2.items()}
HOLE_D=2.40

geom=dict(
  outline=[[round(x,3),round(y,3)] for x,y in outline],
  ears=ears, holes=holes, hole_d=HOLE_D,
  bezel=bz, active=act,
  z=dict(th=2.60, lug_t=0.30, front=True),
  conn=dict(x=[58.0,83.56], y=[26.0,44.0], depth=1.2),   # rear FPC boss (approx, right edge)
  outline_wh=[167.12,208.88], bl=dict(raised_y=BL_Y, ramp=[RAMP_HI,RAMP_LO]),
)
json.dump(geom, open("geometry.json","w"), indent=1)
print("wrote geometry.json")
