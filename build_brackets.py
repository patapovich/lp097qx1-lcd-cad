#!/usr/bin/env python3
"""Two 3D-printable back-press brackets that center the LP097QX1 LCD in a photo frame and
push it from BEHIND onto the frame glass.

Frame inner cavity 182 (W) x 242 (H) mm. Brackets sit on the SHORT sides (top + bottom
edges of the portrait panel), friction-fit between the frame side walls. The VIEW (active) area
is centered in the frame, not the outline (active is offset by (-1.30,-0.89), so the panel is
shifted (+1.30,+0.89)).

Frame coords here: origin = frame center, X right, Y up, Z = 0 at the glass, +Z back into
the cavity. Each bracket is an L / back-press section (no front lip — the screen sits flat on
the glass):
  web front at Z 0 on the glass | panel slot (Z 0..TH+SLOT_CLR) open | rear shelf (Z TH+SLOT_CLR..TOTAL_Z).
The slot fits the 2.60 panel (TH + SLOT_CLR); the rear shelf sits entirely BEHIND the panel, so the
frame backing pushes the bracket -> shelf -> LCD onto the glass (push from behind). The back face
(Z=TOTAL_Z) bottoms on the frame backing.

The lug ears are on the LCD FRONT, recessed ~0.25 mm (tabs at Z ~0.25..0.55, toward the glass),
so their clearance pockets are cut on the FRONT face. That shape-keys the part: it only seats with
the ears in the front pockets (glass side), which keeps the press shelf at the back.

Ear pockets are placed at each tab's ACTUAL frame position (panel view-shift applied in X and Y),
so they track the asymmetric lug layout (TL left-edge, TR top-edge, BL/BR bottom-edge). MIRROR_X
flips handedness if a panel is the other way round (default False = matches the traced front view).

Run: cqenv/bin/python build_brackets.py
 -> bracket_top/bottom .step/.stl + *_thin.stl (5mm test prints)
"""
import json
import cadquery as cq

G = json.load(open("geometry.json"))
HW, HH = G["outline_wh"][0] / 2, G["outline_wh"][1] / 2      # panel half outline 83.56, 104.44
TH = G["z"]["th"]                                            # 2.60 panel thickness
ACT = G["active"]                                            # active offset (cx,cy) on outline

# ---- frame + fit parameters (tune these) ----
FRAME_W, FRAME_H = 182.0, 242.0
HFW, HFH = FRAME_W / 2, FRAME_H / 2                          # 91, 121
VIEW_CENTER = True                                           # center active area (True) or outline (False)
SHIFT_X = -ACT["cx"] if VIEW_CENTER else 0.0                # +1.30
SHIFT_Y = -ACT["cy"] if VIEW_CENTER else 0.0                # +0.89

TOTAL_Z = 15.0          # bracket thickness (glass -> frame backing) = cavity depth
SLOT_CLR = 0.15         # Z clearance: panel slot = TH + SLOT_CLR (shelf sits BEHIND the panel)
LIP_Y   = 3.0           # how far the rear shelf overhangs onto the panel border
FIT_CLR = 0.2           # friction: bracket length = FRAME_W - FIT_CLR
SEAT_CLR = 0.1          # play between panel edge and channel web
POCKET_CLR = 0.3        # play between panel corner and the X end-stops
EAR_CLR = 1.5           # margin around an ear pocket (X + Y)
EAR_ON_BACK = False     # lug ears are on the LCD FRONT (recessed ~0.25mm) -> clear them on the front
EAR_Z   = 0.7           # shallow front pocket depth (clears the ~0.25..0.55 recessed front ear tabs)
MIRROR_X = False        # negate all X (ear spans + SHIFT_X) if the panel is handed the other way
THIN_Z  = 5.0           # thickness of the thin test-print variants

LX = (FRAME_W - FIT_CLR) / 2                                 # half bracket length in X
FLANGE_Z0 = TH + SLOT_CLR                                    # rear shelf front face (2.75) - behind the panel


def b(x0, x1, y0, y1, z0, z1):
    """axis-aligned box from two corners."""
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=(False, False, False))
            .translate((x0, y0, z0)))


def ear_span(name):
    pts = G["ears"][name]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def make_bracket(side, tz=TOTAL_Z, mirror=MIRROR_X):
    """side = +1 top, -1 bottom. tz = total Z thickness. mirror = negate X (handedness)."""
    sx = -SHIFT_X if mirror else SHIFT_X         # panel X offset (active centering), mirrored if needed
    edgeY = side * (HH + side * SHIFT_Y)         # panel short edge in frame Y (top +105.33 / bottom -103.55)
    # gap-side ordering helpers (work in 'outboard' = away from center)
    wallY = side * HFH                            # frame end wall (+121 / -121)
    webInnerY = edgeY + side * SEAT_CLR           # web inner face, 0.1 off the panel edge
    lipInnerY = edgeY - side * LIP_Y              # lip/flange reach onto panel border (toward center)

    # outboard ordering for box building
    def yspan(a, c):                              # return (lo,hi) regardless of side
        return (min(a, c), max(a, c))

    # X end-stops that locate the panel (centered on sx)
    stopL = sx - HW - POCKET_CLR
    stopR = sx + HW + POCKET_CLR

    parts = []
    # 1. web / gap filler: full length, full Z, web inner face -> frame wall (front at Z0 on glass)
    yl, yh = yspan(webInnerY, wallY)
    parts.append(b(-LX, LX, yl, yh, 0, tz))
    # 2. end stops: close the pocket sides, full Z, shelf reach -> web (locate panel corners in X)
    yl, yh = yspan(lipInnerY, webInnerY)
    parts.append(b(-LX, stopL, yl, yh, 0, tz))
    parts.append(b(stopR, LX, yl, yh, 0, tz))
    # 3. rear shelf BEHIND the panel border (front face at TH+SLOT_CLR) -> frame backing presses it -> LCD to glass
    parts.append(b(stopL, stopR, yl, yh, FLANGE_Z0, tz))

    br = parts[0]
    for p in parts[1:]:
        br = br.union(p)

    # 5. ear-clearance pockets: lugs are on the LCD FRONT (recessed ~0.25mm). Clear each ear by its
    #    ACTUAL frame bbox (panel shift applied in X and Y, mirror-aware) + EAR_CLR, cut on the front
    #    (Z 0..EAR_Z). cut() only removes existing material, so this clears whichever way the tab pokes
    #    (TR top, BL/BR bottom, TL left-edge corner graze) with full clearance.
    z0 = (TH - 0.6) if EAR_ON_BACK else 0.0
    z1 = tz if EAR_ON_BACK else min(EAR_Z, tz)
    ears = ["TL", "TR"] if side > 0 else ["BL", "BR"]
    for e in ears:
        exmin, exmax, eymin, eymax = ear_span(e)
        ax0, ax1 = exmin + SHIFT_X, exmax + SHIFT_X      # ear bbox in frame X (panel shift)
        if mirror:
            ax0, ax1 = -ax1, -ax0                        # reflect about frame center
        ay0, ay1 = eymin + SHIFT_Y, eymax + SHIFT_Y      # ear bbox in frame Y
        cut = b(ax0 - EAR_CLR, ax1 + EAR_CLR, ay0 - EAR_CLR, ay1 + EAR_CLR, z0, z1)
        br = br.cut(cut)

    return br


for name, side in [("bracket_top", +1), ("bracket_bottom", -1)]:
    br = make_bracket(side)
    s = br.val(); bb = s.BoundingBox()
    print(f"{name}: solids={len(br.solids().vals())}  vol={s.Volume():.0f} mm^3  "
          f"bbox X[{bb.xmin:.2f},{bb.xmax:.2f}] Y[{bb.ymin:.2f},{bb.ymax:.2f}] Z[{bb.zmin:.2f},{bb.zmax:.2f}]")
    cq.exporters.export(br, name + ".step")
    cq.exporters.export(br, name + ".stl")
    print(f"  wrote {name}.step + {name}.stl")
    # thin test-print variant (same XY/fit/slot/ear pockets, shorter Z)
    thin = make_bracket(side, THIN_Z)
    cq.exporters.export(thin, name + "_thin.stl")
    print(f"  wrote {name}_thin.stl  (Z={THIN_Z})")
    # integrity: must be a single valid solid (no artifacts)
    assert len(br.solids().vals()) == 1 and s.isValid(), f"{name}: not a single valid solid!"

print("all brackets: single valid solids OK")
