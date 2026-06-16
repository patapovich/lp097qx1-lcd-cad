#!/usr/bin/env python3
"""
STEP solid of LP097QX1-SPC1 LCD module for case-mount design, with EXACT traced lug ears.
Datum: origin = module-outline CENTER (X right, Y up). Z=0 rear face, +Z toward screen. Units mm.
Run inside the venv:  cqenv/bin/python build_step.py   ->  lcd_panel.step (+ .stl)

Body & rect sizes = datasheet table. Lug ear silhouettes + hole centers = measured from the
PDF vector drawing (see _ears.json). Lugs are modelled as thin flat sheet-metal tabs at the
rear face (LUG_T thick), matching the datasheet side-view rear frame gauge (~0.3mm).
"""
import json
import cadquery as cq

OUT_W, OUT_H, TH = 167.12, 208.88, 2.60
HOLE_D = 2.40
LUG_T = 0.30      # lug sheet-metal thickness (measured ~0.26-0.30mm rear frame gauge)
LUG_Z = 0.0       # lug tabs sit on the rear face (Z 0..LUG_T)
ACT_W, ACT_H, ACT_CX, ACT_CY, ACT_DEPTH = 147.456, 196.608, -1.30, -0.89, 0.20

ears = json.load(open("_ears.json"))
polys, holes = ears["polys"], ears["holes"]

# module body
body = cq.Workplane("XY").box(OUT_W, OUT_H, TH, centered=(True, True, False))   # Z 0..TH

# exact lug ears (extrude traced silhouette, fuse to body)
def clean(poly, tol=0.03):
    out = []
    for x, y in poly:
        x, y = float(x), float(y)
        if not out or abs(x-out[-1][0]) > tol or abs(y-out[-1][1]) > tol:
            out.append((x, y))
    if len(out) > 1 and abs(out[0][0]-out[-1][0]) < tol and abs(out[0][1]-out[-1][1]) < tol:
        out.pop()
    return out

for k, poly in polys.items():
    pts = clean(poly)
    ear = cq.Workplane("XY").workplane(offset=LUG_Z).polyline(pts).close().extrude(LUG_T)
    body = body.union(ear)

# drill the 4 mounting holes through ears+body
for k, (x, y) in holes.items():
    cutter = cq.Workplane("XY").center(x, y).circle(HOLE_D/2).extrude(TH + 2).translate((0, 0, -1))
    body = body.cut(cutter)

# active-area reference pocket on front face
pocket = (cq.Workplane("XY").workplane(offset=TH - ACT_DEPTH)
          .center(ACT_CX, ACT_CY).rect(ACT_W, ACT_H).extrude(ACT_DEPTH + 1))
body = body.cut(pocket)

# validate + export
solid = body.val()
bb = solid.BoundingBox()
print(f"solids={len(body.solids().vals())}  volume={solid.Volume():.1f} mm^3")
print(f"bbox X[{bb.xmin:.2f},{bb.xmax:.2f}] Y[{bb.ymin:.2f},{bb.ymax:.2f}] Z[{bb.zmin:.2f},{bb.zmax:.2f}]")
cq.exporters.export(body, "lcd_panel.step")
cq.exporters.export(body, "lcd_panel.stl")
print("wrote lcd_panel.step + lcd_panel.stl")
