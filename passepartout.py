#!/usr/bin/env python3
"""Passe-partout (mat) for the LP097QX1: a 180x240x1.4 board with a centred 45-deg-bevel window
that reveals only the active screen (147.456 x 196.608). The brackets centre the ACTIVE area at the
frame centre, so the window is centred in the board (symmetric).

Outputs: images/passepartout.png (dimensioned drawing) + passepartout.dxf (cut lines) + a printed
dimension table.
Run: cqenv/bin/python passepartout.py   (uses matplotlib; DXF is hand-rolled, no deps)
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

G = json.load(open("geometry.json"))
ACT_W, ACT_H = G["active"]["W"], G["active"]["H"]          # 147.456 x 196.608 (the lit screen)

# ---- parameters ----
BOARD_W, BOARD_H = 180.0, 240.0     # mat outer size (frame inner is 182x242 -> ~1mm clearance/side)
THICK = 1.4                         # mat thickness
BEVEL_DEG = 45.0                    # cutter angle
OVERLAP = 0.0                       # mat covers this much of the screen edge all round (raise to ~1.0
                                    # to guarantee no bezel sliver if alignment is imperfect)

import math
RUN = THICK * math.tan(math.radians(BEVEL_DEG))            # horizontal bevel run = 1.4 at 45 deg
FW, FH = ACT_W - 2 * OVERLAP, ACT_H - 2 * OVERLAP          # FRONT (visible) window = what you see
BW, BH = FW + 2 * RUN, FH + 2 * RUN                        # BACK window (bevel flares toward the LCD)
fbx, fby = (BOARD_W - FW) / 2, (BOARD_H - FH) / 2          # front border L/R, T/B
bbx, bby = (BOARD_W - BW) / 2, (BOARD_H - BH) / 2          # back border

print("=== Passe-partout dimensions (mm) ===")
print(f"Board (outer)        : {BOARD_W} x {BOARD_H}  x {THICK} thick")
print(f"FRONT window (visible): {FW:.3f} x {FH:.3f}   (= active screen{'' if OVERLAP==0 else f' - {OVERLAP} overlap'})")
print(f"  front borders       : {fbx:.3f} (L=R)   {fby:.3f} (T=B)")
print(f"BACK window           : {BW:.3f} x {BH:.3f}   (45deg bevel, +{RUN:.2f}/edge toward LCD)")
print(f"  back borders        : {bbx:.3f} (L=R)   {bby:.3f} (T=B)")

# ---------------- DRAWING ----------------
fig = plt.figure(figsize=(11, 8.5))
ax = fig.add_axes([0.05, 0.07, 0.55, 0.86]); ax.set_aspect("equal")
# board
ax.add_patch(Rectangle((0, 0), BOARD_W, BOARD_H, fill=False, ec="black", lw=2))
# front window (solid) + back window (dashed = bevel flare)
ax.add_patch(Rectangle((bbx, bby), BW, BH, fill=False, ec="#b0b0b0", lw=1.0, ls=(0, (4, 3))))
ax.add_patch(Rectangle((fbx, fby), FW, FH, fill="#dff0ff", ec="#1f6fd0", lw=1.6, fc="#eaf5ff"))
ax.text(BOARD_W / 2, BOARD_H / 2, "WINDOW\n(screen)\n%.2f x %.2f" % (FW, FH),
        ha="center", va="center", color="#1f6fd0", fontsize=9)

def dim_h(x0, x1, y, txt, off=0):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color="#c00", lw=1.1))
    ax.text((x0 + x1) / 2, y + off, txt, ha="center", va="bottom", color="#c00", fontsize=8.5)

def dim_v(x, y0, y1, txt, off=0):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color="#c00", lw=1.1))
    ax.text(x + off, (y0 + y1) / 2, txt, ha="left", va="center", color="#c00", fontsize=8.5, rotation=90)

dim_h(0, BOARD_W, -10, f"{BOARD_W:.0f}")                         # outer width
dim_v(-10, 0, BOARD_H, f"{BOARD_H:.0f}")                         # outer height
dim_h(fbx, fbx + FW, fby + FH + 4, f"window {FW:.2f}")           # window width
dim_v(fbx + FW + 4, fby, fby + FH, f"window {FH:.2f}")           # window height
dim_h(0, fbx, fby - 8, f"{fbx:.2f}")                             # left border
dim_v(fbx + FW + 18, fby + FH, BOARD_H, f"{fby:.2f}")            # top border
ax.set_xlim(-22, BOARD_W + 24); ax.set_ylim(-20, BOARD_H + 10)
ax.set_title("Passe-partout — FRONT (viewer) face   [centred window]")
ax.axis("off")

# ---- bevel cross-section detail (right) ----
bx = fig.add_axes([0.62, 0.30, 0.30, 0.40])
T = THICK; r = RUN; scale = 1
# section: top = FRONT/glass (small opening), bottom = BACK/LCD (large opening). show left edge of window.
# draw mat material as two trapezoids on each side; here show the left edge bevel
x_face_front = 0.0          # front inner edge (window edge, viewer)
x_face_back = -r            # back inner edge (flares outward toward LCD)
# mat body to the left
bx.add_patch(plt.Polygon([(-12, 0), (x_face_back, 0), (x_face_front, T), (-12, T)],
                         closed=True, fc="#eedcc0", ec="#7a5c33"))
bx.annotate("", (x_face_front, T + 0.25), (x_face_front + 4, T + 0.25), arrowprops=dict(arrowstyle="->", color="#1f6fd0"))
bx.text(x_face_front + 4.3, T + 0.3, "FRONT\n(glass)", va="center", fontsize=8, color="#1f6fd0")
bx.annotate("", (x_face_back, -0.25), (x_face_back + 4, -0.25), arrowprops=dict(arrowstyle="->", color="#0a8f0a"))
bx.text(x_face_back + 4.3, -0.55, "BACK\n(LCD)", va="center", fontsize=8, color="#0a8f0a")
bx.annotate("", (-12, 0), (-12, T), arrowprops=dict(arrowstyle="<->", color="#c00", lw=1))
bx.text(-12.6, T / 2, f"{T} thick", rotation=90, ha="right", va="center", color="#c00", fontsize=8)
bx.text(x_face_back - 0.4, T / 2, "45°", ha="right", va="center", fontsize=9, color="#7a5c33")
bx.set_xlim(-14, 9); bx.set_ylim(-2.2, T + 2.4); bx.set_aspect("equal"); bx.axis("off")
bx.set_title("Bevel section (window edge)", fontsize=9)

# ---- dimension table (bottom right) ----
tx = fig.add_axes([0.63, 0.06, 0.35, 0.2]); tx.axis("off")
rows = [
    ("Board (outer)", f"{BOARD_W:.0f} x {BOARD_H:.0f} x {THICK}"),
    ("FRONT window (visible)", f"{FW:.2f} x {FH:.2f}"),
    ("  front border L/R, T/B", f"{fbx:.2f} , {fby:.2f}"),
    ("BACK window (bevel)", f"{BW:.2f} x {BH:.2f}"),
    ("  back border L/R, T/B", f"{bbx:.2f} , {bby:.2f}"),
    ("Bevel", f"45°, run {r:.2f} mm"),
]
tx.table(cellText=rows, colWidths=[0.62, 0.38], loc="center", cellLoc="left").scale(1, 1.35)
tx.set_title("Dimensions (mm)", fontsize=9)

fig.savefig("images/passepartout.png", dpi=130)
print("wrote images/passepartout.png")

# ---------------- DXF (R12) ----------------
def rect(cx, cy, w, h):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    return [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]

ox, oy = BOARD_W / 2, BOARD_H / 2
lines = {"BOARD": rect(ox, oy, BOARD_W, BOARD_H),
         "WINDOW_FRONT": rect(ox, oy, FW, FH),
         "WINDOW_BACK": rect(ox, oy, BW, BH)}
out = ["0", "SECTION", "2", "ENTITIES"]
for layer, segs in lines.items():
    for (x0, y0, x1, y1) in segs:
        out += ["0", "LINE", "8", layer,
                "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0.0",
                "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0.0"]
out += ["0", "ENDSEC", "0", "EOF"]
open("passepartout.dxf", "w").write("\n".join(out) + "\n")
print("wrote passepartout.dxf  (layers BOARD / WINDOW_FRONT / WINDOW_BACK)")
