#!/usr/bin/env python3
"""
STEP solid of LP097QX1-SPC1 LCD module for case-mount design, with EXACT traced lug ears.
Datum: origin = module-outline CENTER (X right, Y up). Z=0 rear face, +Z toward screen. Units mm.
Run inside the venv:  cqenv/bin/python build_step.py   ->  lcd_panel.step (+ .stl)

Body & rect sizes = datasheet table. Lug ear silhouettes + hole centers = measured from the
PDF vector drawing (see _ears.json). Lugs are thin flat sheet-metal tabs (LUG_T thick) on the
FRONT (screen) plane, Z (TH-LUG_T)..TH (all 4; user-confirmed from the physical part).
"""
import json
import cadquery as cq

OUT_W, OUT_H, TH = 167.12, 208.88, 2.60
HOLE_D = 2.40
LUG_T = 0.30      # lug sheet-metal thickness (measured ~0.26-0.30mm frame gauge)
FRONT_EARS = {"TL", "TR", "BL", "BR"}   # all 4 ears on the FRONT (screen) plane (user-confirmed)
# each ear's base edge (axis, edge coord, inward sign) — used to overlap the tab into the body
# for a clean fused solid. The stored _ears.json polygons stay at the edge (clean for DXF).
EAR_EDGE = {"TL": ("x", -167.12/2, +1), "TR": ("y", 208.88/2, -1),
            "BL": ("y", -208.88/2, +1), "BR": ("y", -208.88/2, +1)}
ACT_W, ACT_H, ACT_CX, ACT_CY, ACT_DEPTH = 147.456, 196.608, -1.30, -0.89, 0.20

ears = json.load(open("_ears.json"))
polys, holes = ears["polys"], ears["holes"]

# module body — outline corners are rounded (R measured from drawing), not a sharp rectangle
OUTLINE_R = 0.5   # module outline corner radius (small; outer corners are near-sharp)
BL_NOTCH = 1.2    # bottom-left corner chamfer/notch leg (detected from drawing, approximate)
body = (cq.Workplane("XY").box(OUT_W, OUT_H, TH, centered=(True, True, False))
        .edges("|Z").fillet(OUTLINE_R))   # Z 0..TH, 4 rounded vertical corners

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

def overlap_base(pts, k, amt=1.0, tol=0.5):
    """Push the tab's base verts ~amt mm into the body so the union fuses cleanly."""
    ax, E, s = EAR_EDGE[k]
    out = []
    for x, y in pts:
        if ax == "x" and ((s > 0 and x >= E - tol) or (s < 0 and x <= E + tol)):
            x = E + s * amt
        if ax == "y" and ((s > 0 and y >= E - tol) or (s < 0 and y <= E + tol)):
            y = E + s * amt
        out.append((x, y))
    return out

for k, poly in polys.items():
    pts = clean(overlap_base(clean(poly), k))
    z0 = (TH - LUG_T) if k in FRONT_EARS else 0.0   # front (screen) face vs rear face
    ear = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(LUG_T)
    body = body.union(ear)

# rear FPC connector keep-out boss (RIGHT long edge, upper-third; protrudes behind rear).
# Footprint measured from the rear view (approximate); depth ~1.2mm behind the rear face.
CONN_X = (58.0, 83.56); CONN_Y = (26.0, 44.0); CONN_DEPTH = 1.2
conn = (cq.Workplane("XY").workplane(offset=-CONN_DEPTH)
        .center((CONN_X[0]+CONN_X[1])/2, (CONN_Y[0]+CONN_Y[1])/2)
        .rect(CONN_X[1]-CONN_X[0], CONN_Y[1]-CONN_Y[0]).extrude(CONN_DEPTH + 0.2))  # 0.2 overlap into body
body = body.union(conn)

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
# bottom-left corner notch (chamfer) — the BL outline corner is cut, per the drawing
notch = (cq.Workplane("XY").workplane(offset=-CONN_DEPTH - 1)
         .polyline([(-OUT_W/2 - 1, -OUT_H/2 - 1), (-OUT_W/2 + BL_NOTCH, -OUT_H/2 - 1),
                    (-OUT_W/2 - 1, -OUT_H/2 + BL_NOTCH)]).close().extrude(TH + CONN_DEPTH + 2))
body = body.cut(notch)

cq.exporters.export(body, "lcd_panel.step")
cq.exporters.export(body, "lcd_panel.stl")
print("wrote lcd_panel.step + lcd_panel.stl")
