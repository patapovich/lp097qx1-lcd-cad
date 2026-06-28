#!/usr/bin/env python3
"""Passe-partout (mat) for the LP097QX1: a 180x240x1.4 board with a centred 45-deg-bevel window
that reveals only the active screen (147.456 x 196.608). The brackets centre the ACTIVE area at the
frame centre, so the window is centred in the board (symmetric).

Bevel: the SCREEN-sized (limiting) opening is on the LCD-facing (back) face, right at the screen
plane; the bevel opens OUT toward the glass/viewer (white bevel faces you). Set BEVEL_TOWARD="lcd"
for the standard picture-mat direction (small opening at the glass).

Outputs: images/passepartout.png (dimensioned drawing) + passepartout.dxf + a printed table.
Run: cqenv/bin/python passepartout.py
"""
import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

G = json.load(open("geometry.json"))
ACT_W, ACT_H = G["active"]["W"], G["active"]["H"]          # 147.456 x 196.608 (the lit screen)

# ---- parameters ----
BOARD_W, BOARD_H = 180.0, 240.0     # mat outer (frame inner 182x242 -> ~1mm clearance/side)
THICK = 1.4                         # mat thickness
BEVEL_DEG = 45.0
OVERLAP = 0.0                       # mat covers this much of the screen edge all round (raise ~1.0
                                    # to guarantee no bezel sliver)
BEVEL_TOWARD = "glass"              # "glass" = bevel opens toward viewer, screen-sized edge on LCD side
                                    # "lcd"   = standard picture-mat, screen-sized edge on glass side

RUN = THICK * math.tan(math.radians(BEVEL_DEG))            # 1.4 at 45 deg
SW, SH = ACT_W - 2 * OVERLAP, ACT_H - 2 * OVERLAP          # SCREEN opening (limiting / crop = visible)
LW, LH = SW + 2 * RUN, SH + 2 * RUN                        # the LARGER opening on the other face

if BEVEL_TOWARD == "glass":     # screen-sized edge on the LCD/back face; flare toward the glass
    glassW, glassH = LW, LH     # glass (front) opening = larger
    lcdW, lcdH = SW, SH         # lcd (back) opening = screen
else:                            # standard: screen-sized edge on the glass/front face
    glassW, glassH = SW, SH
    lcdW, lcdH = LW, LH

gbx, gby = (BOARD_W - glassW) / 2, (BOARD_H - glassH) / 2  # glass-side borders
lbx, lby = (BOARD_W - lcdW) / 2, (BOARD_H - lcdH) / 2      # lcd-side borders

print("=== Passe-partout dimensions (mm) ===")
print(f"Board (outer)        : {BOARD_W} x {BOARD_H} x {THICK}   bevel opens toward {BEVEL_TOWARD.upper()}")
print(f"SCREEN opening (visible/crop): {SW:.3f} x {SH:.3f}  -> on the {'LCD/back' if BEVEL_TOWARD=='glass' else 'glass/front'} face")
print(f"GLASS (front) face opening   : {glassW:.3f} x {glassH:.3f}   borders {gbx:.3f} (L=R) , {gby:.3f} (T=B)")
print(f"LCD   (back)  face opening   : {lcdW:.3f} x {lcdH:.3f}   borders {lbx:.3f} (L=R) , {lby:.3f} (T=B)")
print(f"Bevel: 45 deg, run {RUN:.2f} mm/edge")

# ---------------- DRAWING ----------------
fig = plt.figure(figsize=(11, 8.5))
ax = fig.add_axes([0.05, 0.07, 0.55, 0.86]); ax.set_aspect("equal")
ax.add_patch(Rectangle((0, 0), BOARD_W, BOARD_H, fill=False, ec="black", lw=2))           # board
ax.add_patch(Rectangle((gbx, gby), glassW, glassH, fill=False, ec="#b0b0b0", lw=1.0, ls=(0, (4, 3))))  # glass-side opening
ax.add_patch(Rectangle((lbx, lby), lcdW, lcdH, fill="#dff0ff", ec="#1f6fd0", lw=1.6, fc="#eaf5ff"))    # screen (LCD side)
ax.text(BOARD_W / 2, BOARD_H / 2, "SCREEN window\n(LCD-side, visible)\n%.2f x %.2f" % (SW, SH),
        ha="center", va="center", color="#1f6fd0", fontsize=9)


def dim_h(x0, x1, y, txt, off=0):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color="#c00", lw=1.1))
    ax.text((x0 + x1) / 2, y + off, txt, ha="center", va="bottom", color="#c00", fontsize=8.5)


def dim_v(x, y0, y1, txt, off=0):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color="#c00", lw=1.1))
    ax.text(x + off, (y0 + y1) / 2, txt, ha="left", va="center", color="#c00", fontsize=8.5, rotation=90)


dim_h(0, BOARD_W, -10, f"{BOARD_W:.0f}")
dim_v(-10, 0, BOARD_H, f"{BOARD_H:.0f}")
dim_h(lbx, lbx + lcdW, lby + lcdH + 4, f"screen {SW:.2f}")
dim_v(lbx + lcdW + 4, lby, lby + lcdH, f"screen {SH:.2f}")
dim_h(0, lbx, lby - 8, f"{lbx:.2f}")                                       # lcd-side border (screen)
ax.set_xlim(-22, BOARD_W + 24); ax.set_ylim(-20, BOARD_H + 10)
ax.set_title("Passe-partout — window = active screen (centred)")
ax.axis("off")

# ---- bevel cross-section (top = FRONT/glass, bottom = BACK/LCD) ----
bx = fig.add_axes([0.62, 0.30, 0.30, 0.40]); T = THICK; r = RUN
# inner window edges (left edge): glass-face at xg, lcd-face at xl ; screen edge is the smaller opening
xg = 0.0 if BEVEL_TOWARD == "lcd" else -r        # glass-face inner edge
xl = -r if BEVEL_TOWARD == "lcd" else 0.0        # lcd-face inner edge
bx.add_patch(Polygon([(-12, 0), (xl, 0), (xg, T), (-12, T)], closed=True, fc="#eedcc0", ec="#7a5c33"))
bx.annotate("", (xg, T + 0.25), (xg + 4, T + 0.25), arrowprops=dict(arrowstyle="->", color="#1f6fd0"))
bx.text(xg + 4.3, T + 0.3, "FRONT\n(glass)", va="center", fontsize=8, color="#1f6fd0")
bx.annotate("", (xl, -0.25), (xl + 4, -0.25), arrowprops=dict(arrowstyle="->", color="#0a8f0a"))
bx.text(xl + 4.3, -0.6, "BACK\n(LCD)\nscreen edge" if BEVEL_TOWARD == "glass" else "BACK\n(LCD)",
        va="center", fontsize=8, color="#0a8f0a")
bx.annotate("", (-12, 0), (-12, T), arrowprops=dict(arrowstyle="<->", color="#c00", lw=1))
bx.text(-12.6, T / 2, f"{T} thick", rotation=90, ha="right", va="center", color="#c00", fontsize=8)
bx.text(min(xg, xl) - 0.4, T / 2, "45°", ha="right", va="center", fontsize=9, color="#7a5c33")
bx.set_xlim(-14, 9); bx.set_ylim(-2.4, T + 2.4); bx.set_aspect("equal"); bx.axis("off")
bx.set_title("Bevel section (opens toward glass)", fontsize=9)

# ---- table ----
tx = fig.add_axes([0.63, 0.05, 0.35, 0.2]); tx.axis("off")
rows = [
    ("Board (outer)", f"{BOARD_W:.0f} x {BOARD_H:.0f} x {THICK}"),
    ("SCREEN window (visible)", f"{SW:.2f} x {SH:.2f}"),
    ("GLASS face opening", f"{glassW:.2f} x {glassH:.2f}"),
    ("  glass border L/R, T/B", f"{gbx:.2f} , {gby:.2f}"),
    ("LCD face opening (= screen)", f"{lcdW:.2f} x {lcdH:.2f}"),
    ("  LCD border L/R, T/B", f"{lbx:.2f} , {lby:.2f}"),
    ("Bevel", f"45°, run {r:.2f}, toward {BEVEL_TOWARD}"),
]
tx.table(cellText=rows, colWidths=[0.6, 0.4], loc="center", cellLoc="left").scale(1, 1.3)
tx.set_title("Dimensions (mm)", fontsize=9)

fig.savefig("images/passepartout.png", dpi=130)
print("wrote images/passepartout.png")

# ---------------- DXF (R12) ----------------
def rect(cx, cy, w, h):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    return [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]


ox, oy = BOARD_W / 2, BOARD_H / 2
lines = {"BOARD": rect(ox, oy, BOARD_W, BOARD_H),
         "WINDOW_SCREEN": rect(ox, oy, SW, SH),          # LCD-side, the visible crop
         "WINDOW_GLASS": rect(ox, oy, glassW, glassH)}   # glass-side (larger, bevel mouth)
out = ["0", "SECTION", "2", "ENTITIES"]
for layer, segs in lines.items():
    for (x0, y0, x1, y1) in segs:
        out += ["0", "LINE", "8", layer,
                "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0.0",
                "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0.0"]
out += ["0", "ENDSEC", "0", "EOF"]
open("passepartout.dxf", "w").write("\n".join(out) + "\n")
print("wrote passepartout.dxf  (layers BOARD / WINDOW_SCREEN / WINDOW_GLASS)")
