#!/usr/bin/env python3
"""
STEP solid of LP097QX1-SPC1 LCD module for case-mount design, with EXACT traced lug ears.
Datum: origin = module-outline CENTER (X right, Y up). Z=0 rear face, +Z toward screen. Units mm.
Run inside the venv:  cqenv/bin/python build_step.py   ->  lcd_panel.step (+ .stl)

Body & rect sizes = datasheet table. Lug ear silhouettes + hole centers = measured from the
PDF vector drawing (see _ears.json). Lugs are thin flat sheet-metal tabs (LUG_T thick) on the
FRONT (screen) plane, Z (TH-LUG_T)..TH (all 4; user-confirmed from the physical part).
"""
import json, math
import cadquery as cq

OUT_W, OUT_H, TH = 167.12, 208.88, 2.60
HOLE_D = 2.40
LUG_T = 0.30      # lug sheet-metal thickness (measured ~0.26-0.30mm frame gauge)
FRONT_EARS = {"TL", "TR", "BL", "BR"}   # all 4 ears on the FRONT (screen) plane (user-confirmed)
OUTLINE_R = 0.5            # outline corner radius (small; outer corners are near-sharp)
# Outline is NOT square: the bottom-left ~17mm is raised ~0.95mm (Y=BL_Y) then ramps down
# to the full bottom (-OUT_H/2) over BL_RAMP. Measured from the drawing.
BL_Y = -103.49
BL_RAMP = (-66.0, -63.8)   # raised flat ends at X=-66, ramp reaches full bottom by X=-63.8
# each ear's base edge (axis, edge coord, inward sign) for the build-time fusion overlap:
EAR_EDGE = {"TL": ("x", -OUT_W/2, +1), "TR": ("y", OUT_H/2, -1),
            "BL": ("y", BL_Y, +1), "BR": ("y", -OUT_H/2, +1)}
ACT_W, ACT_H, ACT_CX, ACT_CY, ACT_DEPTH = 147.456, 196.608, -1.30, -0.89, 0.20

def outline_poly(R, n=10):
    """Outline: rounded corners (R) + raised bottom-left step + ramp. CCW from TR."""
    HW, HH = OUT_W/2, OUT_H/2
    p = []
    def arc(cx, cy, a0, a1):
        for i in range(n+1):
            a = math.radians(a0 + (a1-a0)*i/n); p.append((cx+R*math.cos(a), cy+R*math.sin(a)))
    arc(HW-R, HH-R, 0, 90)            # TR
    arc(-HW+R, HH-R, 90, 180)         # TL
    arc(-HW+R, BL_Y+R, 180, 270)      # BL (raised bottom)
    p.append((BL_RAMP[0], BL_Y))      # raised flat -> ramp start
    p.append((BL_RAMP[1], -HH))       # ramp down to full bottom
    arc(HW-R, -HH+R, 270, 360)        # BR
    return p

ears = json.load(open("_ears.json"))
polys, holes = ears["polys"], ears["holes"]

# module body — outline polygon (rounded corners + non-square raised bottom-left), extruded
body = cq.Workplane("XY").polyline(outline_poly(OUTLINE_R)).close().extrude(TH)   # Z 0..TH

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

cq.exporters.export(body, "lcd_panel.step")
cq.exporters.export(body, "lcd_panel.stl")
print("wrote lcd_panel.step + lcd_panel.stl")
