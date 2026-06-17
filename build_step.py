#!/usr/bin/env python3
"""STEP/STL solid of LP097QX1-SPC1 from CLEAN-traced geometry (geometry.json).
Datum: origin = module-outline CENTER (X right, Y up). Z=0 rear, +Z toward screen. mm.
Run: cqenv/bin/python build_step.py  -> lcd_panel.step (+ .stl)

Body = full-thickness traced outline (rect + R0.5 + bottom-left raised step/ramp).
Ears = 4 thin (LUG_T) flat tabs on the FRONT face (Z TH-LUG_T..TH), traced silhouettes, fused.
Holes ⌀ datasheet through. Rear FPC connector boss on right edge. Active-area pocket on front.
"""
import json, math
import cadquery as cq

G = json.load(open("geometry.json"))
TH   = G["z"]["th"]; LUG_T = G["z"]["lug_t"]
HOLE_D = G["hole_d"]
HW, HH = G["outline_wh"][0]/2, G["outline_wh"][1]/2
BL_Y = G["bl"]["raised_y"]
# body edge each ear attaches to (axis, edge value, inward sign) for fusion overlap
EAR_EDGE = {"TL": ("x", -HW, +1), "TR": ("y", HH, -1),
            "BL": ("y", BL_Y, +1), "BR": ("y", -HH, +1)}

def clean(poly, tol=0.02):
    out=[]
    for x,y in poly:
        x,y=float(x),float(y)
        if not out or abs(x-out[-1][0])>tol or abs(y-out[-1][1])>tol: out.append((x,y))
    if len(out)>1 and abs(out[0][0]-out[-1][0])<tol and abs(out[0][1]-out[-1][1])<tol: out.pop()
    return out

def overlap_base(pts, k, amt=1.0, tol=0.4):
    """push the tab's base verts ~amt mm into the body so the union fuses cleanly."""
    ax,E,s = EAR_EDGE[k]; out=[]
    for x,y in pts:
        if ax=="x" and abs(x-E)<tol: x=E+s*amt
        if ax=="y" and abs(y-E)<tol: y=E+s*amt
        out.append((x,y))
    return out

# ---- body: traced outline, full thickness ----
body = cq.Workplane("XY").polyline(clean(G["outline"])).close().extrude(TH)

# ---- ears: thin flat tabs on the FRONT face, fused ----
z0 = TH - LUG_T
for k, poly in G["ears"].items():
    pts = clean(overlap_base(clean(poly), k))
    ear = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(LUG_T)
    body = body.union(ear)

# ---- rear FPC connector keep-out boss (right long edge) ----
cxs,cxe = G["conn"]["x"]; cys,cye = G["conn"]["y"]; cd = G["conn"]["depth"]
conn = (cq.Workplane("XY").workplane(offset=-cd)
        .center((cxs+cxe)/2,(cys+cye)/2).rect(cxe-cxs,cye-cys).extrude(cd+0.2))
body = body.union(conn)

# ---- drill the 4 mounting holes through ears+body ----
for k,(x,y) in G["holes"].items():
    body = body.cut(cq.Workplane("XY").center(x,y).circle(HOLE_D/2).extrude(TH+2).translate((0,0,-1)))

# ---- active-area reference pocket on front face ----
A=G["active"]; AD=0.20
body = body.cut(cq.Workplane("XY").workplane(offset=TH-AD)
                .center(A["cx"],A["cy"]).rect(A["W"],A["H"]).extrude(AD+1))

solid=body.val(); bb=solid.BoundingBox()
print(f"solids={len(body.solids().vals())}  volume={solid.Volume():.1f} mm^3")
print(f"bbox X[{bb.xmin:.2f},{bb.xmax:.2f}] Y[{bb.ymin:.2f},{bb.ymax:.2f}] Z[{bb.zmin:.2f},{bb.zmax:.2f}]")
cq.exporters.export(body,"lcd_panel.step"); cq.exporters.export(body,"lcd_panel.stl")
print("wrote lcd_panel.step + lcd_panel.stl")
