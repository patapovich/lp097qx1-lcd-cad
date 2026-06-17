#!/usr/bin/env python3
"""Regenerate all deliverables from geometry.json (clean-traced)."""
import json, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle as MCirc, Rectangle as MRect

G=json.load(open("geometry.json"))
OW,OH=G["outline_wh"]; HW,HH=OW/2,OH/2
TH=G["z"]["th"]; LUG=G["z"]["lug_t"]; HD=G["hole_d"]
outline=G["outline"]; ears=G["ears"]; holes=G["holes"]
bz=G["bezel"]; act=G["active"]; conn=G["conn"]; BLY=G["bl"]["raised_y"]

# ---------- DXF (R12) helpers ----------
def dxf_open(): return ["0","SECTION","2","ENTITIES"]
def dxf_close(d): d+=["0","ENDSEC","0","EOF"]; return "\n".join(d)+"\n"
def line(d,lay,x1,y1,x2,y2):
    d+=["0","LINE","8",lay,"10",f"{x1:.4f}","20",f"{y1:.4f}","30","0",
        "11",f"{x2:.4f}","21",f"{y2:.4f}","31","0"]
def poly(d,lay,pts,close=True):
    P=list(pts)
    if close: P=P+[P[0]]
    for a,b in zip(P,P[1:]): line(d,lay,a[0],a[1],b[0],b[1])
def circle(d,lay,x,y,r):
    d+=["0","CIRCLE","8",lay,"10",f"{x:.4f}","20",f"{y:.4f}","30","0","40",f"{r:.4f}"]
def point(d,lay,x,y):
    d+=["0","POINT","8",lay,"10",f"{x:.4f}","20",f"{y:.4f}","30","0"]
def rect(d,lay,cx,cy,w,h):
    poly(d,lay,[(cx-w/2,cy-h/2),(cx+w/2,cy-h/2),(cx+w/2,cy+h/2),(cx-w/2,cy+h/2)])

def build_dxf(tf):
    """tf(x,y)->(x,y) datum transform."""
    d=dxf_open()
    poly(d,"OUTLINE",[tf(*p) for p in outline])
    rect2=lambda lay,cx,cy,w,h: poly(d,lay,[tf(cx-w/2,cy-h/2),tf(cx+w/2,cy-h/2),tf(cx+w/2,cy+h/2),tf(cx-w/2,cy+h/2)])
    rect2("BEZEL",bz["cx"],bz["cy"],bz["W"],bz["H"])
    rect2("ACTIVE",act["cx"],act["cy"],act["W"],act["H"])
    for k,poly_pts in ears.items(): poly(d,"EARS",[tf(*p) for p in poly_pts])
    for k,(x,y) in holes.items():
        X,Y=tf(x,y); circle(d,"HOLES",X,Y,HD/2); point(d,"HOLE_CENTERS",X,Y)
    rect2("CONNECTOR",(conn["x"][0]+conn["x"][1])/2,(conn["y"][0]+conn["y"][1])/2,
          conn["x"][1]-conn["x"][0],conn["y"][1]-conn["y"][0])
    return dxf_close(d)

open("lcd_centerdatum.dxf","w").write(build_dxf(lambda x,y:(x,y)))
open("lcd_cornerdatum.dxf","w").write(build_dxf(lambda x,y:(x+HW, HH-y)))   # top-left origin, Y down

# side profile (X-Z section): body W x TH, ear front tab, connector rear, active recess
d=dxf_open()
poly(d,"BODY",[(-HW,0),(HW,0),(HW,TH),(-HW,TH)])
line(d,"LUG_FRONT_PLANE",-HW,TH-LUG,HW,TH-LUG)       # ears live between this and TH
poly(d,"CONNECTOR",[(conn["x"][0],0),(conn["x"][1],0),(conn["x"][1],-conn["depth"]),(conn["x"][0],-conn["depth"])])
line(d,"ACTIVE",-act["W"]/2+act["cx"],TH-0.2, act["W"]/2+act["cx"],TH-0.2)
open("lcd_sideprofile.dxf","w").write(dxf_close(d))
print("wrote 3 DXF")

# ---------- SCAD ----------
def arr(pts): return "["+",".join(f"[{x:.3f},{y:.3f}]" for x,y in pts)+"]"
scad=f"""// LP097QX1-SPC1 LCD module - CLEAN-traced geometry (center datum, mm, Y up).
// Body=traced outline (full {TH}mm). Ears=thin FRONT tabs ({LUG}mm). Rear FPC boss RIGHT edge.
OUT_W={OW}; OUT_H={OH}; TH={TH}; LUG_T={LUG}; HOLE_D={HD};
ACT_W={act['W']}; ACT_H={act['H']}; ACT_CX={act['cx']}; ACT_CY={act['cy']}; ACT_D=0.20;
CONN=[{conn['x'][0]},{conn['x'][1]},{conn['y'][0]},{conn['y'][1]}]; CONN_D={conn['depth']};
OUTLINE={arr(outline)};
HOLES=[{",".join(f"[{x:.3f},{y:.3f}]" for x,y in holes.values())}];
EARS=[
  {",\n  ".join(arr(p) for p in ears.values())}
];
$fn=96;
difference() {{
  union() {{
    linear_extrude(TH) polygon(OUTLINE);
    for (p=EARS) translate([0,0,TH-LUG_T]) linear_extrude(LUG_T) polygon(p);
    translate([CONN[0],CONN[2],-CONN_D]) cube([CONN[1]-CONN[0],CONN[3]-CONN[2],CONN_D+0.2]);
  }}
  for (h=HOLES) translate([h[0],h[1],-CONN_D-1]) cylinder(d=HOLE_D,h=TH+CONN_D+2);
  translate([ACT_CX-ACT_W/2,ACT_CY-ACT_H/2,TH-ACT_D]) cube([ACT_W,ACT_H,ACT_D+1]);
}}
"""
open("lcd_panel.scad","w").write(scad); print("wrote SCAD")

# ---------- CSV ----------
csv=["lug,Xc,Yc,Xtl,Ytl_down,dia"]
for k,(x,y) in holes.items():
    csv.append(f"{k},{x:.2f},{y:.2f},{x+HW:.2f},{HH-y:.2f},{HD:.2f}")
open("lcd_lugs.csv","w").write("\n".join(csv)+"\n"); print("wrote CSV")

# ---------- reference.txt ----------
def cd(x,y): return f"({x:+.2f},{y:+.2f})"
R=[]
R.append("LP097QX1-SPC1  mechanical reference for case-mount design   (units mm)")
R.append("Source: datasheet p17 FRONT VIEW (printed 16/28). Geometry RE-TRACED from a colour-cleaned")
R.append("render (dimension lines/centerlines/active-reference stripped), self-calibrated to the outline.")
R.append("Accuracy: outline=datasheet nominal; hole centers ~+/-0.05mm relative; ears = traced silhouettes.")
R.append("")
R.append("SIZES:")
R.append(f"  Module outline : {OW}(W) x {OH}(H)  [+/-0.50]   thickness {TH} max ; corners R0.5")
R.append(f"     NON-SQUARE bottom-left: bottom edge raised to Y={BLY} for X[-83.56,{G['bl']['ramp'][0]}], ramps to full bottom (Y={-HH}) by X={G['bl']['ramp'][1]}")
R.append(f"  Bezel/polarizer: {bz['W']}(W) x {bz['H']}(H)   center {cd(bz['cx'],bz['cy'])}")
R.append(f"  Active area    : {act['W']}(W) x {act['H']}(H)   center {cd(act['cx'],act['cy'])}")
R.append(f"  Hole dia       : {HD} nominal (4x mounting-lug holes)")
R.append("")
R.append("== DATUM A: origin = OUTLINE CENTER, X right, Y up  (lcd_centerdatum.dxf) ==")
R.append(f"  OUTLINE  size {OW:.3f} x {OH:.3f}  center (+0.00,+0.00)")
R.append(f"  BEZEL    size {bz['W']:.3f} x {bz['H']:.3f}  center {cd(bz['cx'],bz['cy'])}")
R.append(f"  ACTIVE   size {act['W']:.3f} x {act['H']:.3f}  center {cd(act['cx'],act['cy'])}")
for k,(x,y) in holes.items(): R.append(f"  HOLE {k}  {cd(x,y)}  dia {HD}")
R.append("")
R.append("== DATUM B: origin = OUTLINE TOP-LEFT, X right, Y DOWN  (lcd_cornerdatum.dxf) ==")
for k,(x,y) in holes.items(): R.append(f"  HOLE {k}  ({x+HW:+.2f},{HH-y:+.2f})  dia {HD}")
R.append("")
R.append(f"Lug ears: thin flat SHEET-METAL tabs (thickness {LUG}mm), ALL on the FRONT/screen face (Z {TH-LUG}..{TH}).")
R.append("Exact traced silhouettes (teardrop/gusset, asymmetric per corner). DXF layer EARS; 3D = thin tabs fused to body.")
R.append(f"Rear FPC connector: keep-out boss on RIGHT long edge (X {conn['x'][0]}..{conn['x'][1]}, Y {conn['y'][0]}..{conn['y'][1]}), protrudes ~{conn['depth']}mm BEHIND rear (Z -{conn['depth']}..0). APPROXIMATE.")
open("lcd_reference.txt","w").write("\n".join(R)+"\n"); print("wrote reference.txt")

# ---------- images: overview_2d ----------
fig,ax=plt.subplots(figsize=(6,7.4))
ax.add_patch(MPoly(outline,closed=True,fill=False,ec="black",lw=1.5))
ax.add_patch(MRect((bz["cx"]-bz["W"]/2,bz["cy"]-bz["H"]/2),bz["W"],bz["H"],fill=False,ec="0.4",lw=.8))
ax.add_patch(MRect((act["cx"]-act["W"]/2,act["cy"]-act["H"]/2),act["W"],act["H"],fill=False,ec="green",lw=.8,ls="--"))
for k,p in ears.items(): ax.add_patch(MPoly(p,closed=True,fc="#ffcccc",ec="red",lw=1))
for k,(x,y) in holes.items():
    ax.add_patch(MCirc((x,y),HD/2,fill=False,ec="blue",lw=1)); ax.plot(x,y,"b+")
    ax.annotate(f"{k}\n({x:.1f},{y:.1f})",(x,y),fontsize=6,ha="center",va="center")
ax.add_patch(MRect((conn["x"][0],conn["y"][0]),conn["x"][1]-conn["x"][0],conn["y"][1]-conn["y"][0],fc="none",ec="orange",lw=1,ls=":"))
ax.set_aspect("equal"); ax.set_xlim(-95,90); ax.set_ylim(-115,115); ax.grid(alpha=.3)
ax.set_title("LP097QX1-SPC1 (center datum, mm)"); ax.set_xlabel("X"); ax.set_ylabel("Y")
plt.tight_layout(); plt.savefig("images/overview_2d.png",dpi=110); plt.close()

# lug_planes side schematic
fig,ax=plt.subplots(figsize=(8,2.6))
ax.add_patch(MRect((-HW,0),OW,TH,fc="#eeeeee",ec="k"))
ax.add_patch(MRect((-HW,TH-LUG),OW,LUG,fc="#ffcccc",ec="r",lw=.8))     # ear front plane band
ax.add_patch(MRect((conn["x"][0],-conn["depth"]),conn["x"][1]-conn["x"][0],conn["depth"],fc="#ffe0b0",ec="orange"))
ax.annotate(f"front ears Z {TH-LUG:.2f}..{TH:.2f}",(0,TH),(0,TH+0.6),fontsize=8,ha="center",color="r",arrowprops=dict(arrowstyle="->",color="r"))
ax.annotate(f"rear FPC boss -{conn['depth']:.1f}",(conn['x'][1],-conn['depth']),(40,-1.6),fontsize=8,color="orange",arrowprops=dict(arrowstyle="->",color="orange"))
ax.text(-HW+4,TH/2,f"TH {TH}",fontsize=9,va="center")
ax.set_aspect("equal"); ax.set_xlim(-95,95); ax.set_ylim(-2.5,4); ax.set_title("Side (X-Z) — ear/connector Z planes"); ax.set_xlabel("X"); ax.set_ylabel("Z")
plt.tight_layout(); plt.savefig("images/lug_planes.png",dpi=110); plt.close()
print("wrote overview_2d.png, lug_planes.png")
