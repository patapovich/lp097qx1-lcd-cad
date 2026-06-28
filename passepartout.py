#!/usr/bin/env python3
"""Passe-partout (mat) for the LP097QX1: a 180x240x1.4 board with a centred 45-deg-bevel window
that reveals only the active screen (147.456 x 196.608). The brackets centre the ACTIVE area at the
frame centre, so the window is centred in the board (symmetric).

Bevel: the SCREEN-sized (limiting) opening is on the LCD-facing (back) face, right at the screen
plane; the bevel opens OUT toward the glass/viewer. Set BEVEL_TOWARD="lcd" for the standard
picture-mat direction (small opening at the glass).

The drawing is a HAND-MARKING guide: mark on the LCD-facing side, measure each border from the board
edge, join with a straightedge, then 45-deg bevel-cut.

Outputs: images/passepartout.png + passepartout.dxf + printed table.
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
BOARD_W, BOARD_H = 180.0, 240.0
THICK = 1.4
BEVEL_DEG = 45.0
OVERLAP = 0.0                       # raise ~1.0 to cover the screen edge (no bezel sliver)
BEVEL_TOWARD = "glass"              # "glass" (screen edge on LCD side) | "lcd" (standard)

RUN = THICK * math.tan(math.radians(BEVEL_DEG))
SW, SH = ACT_W - 2 * OVERLAP, ACT_H - 2 * OVERLAP          # SCREEN opening (visible crop = mark line)
LW, LH = SW + 2 * RUN, SH + 2 * RUN
if BEVEL_TOWARD == "glass":
    glassW, glassH, lcdW, lcdH = LW, LH, SW, SH
else:
    glassW, glassH, lcdW, lcdH = SW, SH, LW, LH
gbx, gby = (BOARD_W - glassW) / 2, (BOARD_H - glassH) / 2
lbx, lby = (BOARD_W - lcdW) / 2, (BOARD_H - lcdH) / 2

# the line you MARK (screen window) on the marking face, as offsets from the board edges:
mbx, mby = (BOARD_W - SW) / 2, (BOARD_H - SH) / 2          # border to screen window
xL, xR = mbx, BOARD_W - mbx                                # window left/right X (from left edge)
yB, yT = mby, BOARD_H - mby                                # window bottom/top Y (from bottom edge)

print("=== Passe-partout MARKING (mm), mark on the LCD-facing side ===")
print(f"Board {BOARD_W} x {BOARD_H} x {THICK}.  Screen window {SW:.2f} x {SH:.2f} (centred).")
print(f"Border from each edge: {mbx:.2f} (left & right) , {mby:.2f} (top & bottom)")
print(f"Window corners from bottom-left: ({xL:.2f},{yB:.2f}) ({xR:.2f},{yB:.2f}) ({xL:.2f},{yT:.2f}) ({xR:.2f},{yT:.2f})")
print(f"Bevel 45 deg, run {RUN:.2f}/edge, opens toward {BEVEL_TOWARD}. Glass-face opening {glassW:.2f} x {glassH:.2f}.")

# ---------------- MARKING DRAWING ----------------
fig = plt.figure(figsize=(12.5, 9.0))
ax = fig.add_axes([0.07, 0.08, 0.58, 0.85])
ax.set_aspect("equal")
# board + ruler grid
ax.add_patch(Rectangle((0, 0), BOARD_W, BOARD_H, fill=False, ec="black", lw=2.2))
ax.set_xticks(range(0, int(BOARD_W) + 1, 20)); ax.set_xticks(range(0, int(BOARD_W) + 1, 10), minor=True)
ax.set_yticks(range(0, int(BOARD_H) + 1, 20)); ax.set_yticks(range(0, int(BOARD_H) + 1, 10), minor=True)
ax.grid(which="major", color="#cfcfcf", lw=0.6); ax.grid(which="minor", color="#ececec", lw=0.4)
ax.set_axisbelow(True)
# glass-face opening (reference, faint) + screen window (the MARK line, bold)
ax.add_patch(Rectangle((gbx, gby), glassW, glassH, fill=False, ec="#bbbbbb", lw=1.0, ls=(0, (4, 3))))
ax.add_patch(Rectangle((xL, yB), SW, SH, fill=False, ec="#1f6fd0", lw=2.2))
ax.text((xL + xR) / 2, (yB + yT) / 2, "MARK THIS WINDOW\n(screen, LCD-side)\n%.2f x %.2f" % (SW, SH),
        ha="center", va="center", color="#1f6fd0", fontsize=10, fontweight="bold")

red = dict(arrowstyle="<->", color="#c00", lw=1.2)
# border offsets from EACH edge (so you can measure from whichever edge)
ax.annotate("", (0, yB - 14), (xL, yB - 14), arrowprops=red)
ax.text(xL / 2, yB - 18, f"{mbx:.2f}", color="#c00", ha="center", va="top", fontsize=10, fontweight="bold")
ax.annotate("", (xR, yB - 14), (BOARD_W, yB - 14), arrowprops=red)
ax.text((xR + BOARD_W) / 2, yB - 18, f"{mbx:.2f}", color="#c00", ha="center", va="top", fontsize=10, fontweight="bold")
ax.annotate("", (xL - 14, 0), (xL - 14, yB), arrowprops=red)
ax.text(xL - 18, yB / 2, f"{mby:.2f}", color="#c00", ha="right", va="center", rotation=90, fontsize=10, fontweight="bold")
ax.annotate("", (xL - 14, yT), (xL - 14, BOARD_H), arrowprops=red)
ax.text(xL - 18, (yT + BOARD_H) / 2, f"{mby:.2f}", color="#c00", ha="right", va="center", rotation=90, fontsize=10, fontweight="bold")
# overall outer dims
ax.annotate("", (0, -34), (BOARD_W, -34), arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
ax.text(BOARD_W / 2, -38, f"{BOARD_W:.0f}", ha="center", va="top", fontsize=10)
ax.annotate("", (-34, 0), (-34, BOARD_H), arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
ax.text(-38, BOARD_H / 2, f"{BOARD_H:.0f}", ha="right", va="center", rotation=90, fontsize=10)

# edge tick marks at the mark lines + corner coordinates (from bottom-left)
for x in (xL, xR):
    for y0, y1 in [(0, -6), (BOARD_H, BOARD_H + 6)]:
        ax.plot([x, x], [y0, y1], color="#c00", lw=1.6, clip_on=False)
for y in (yB, yT):
    for x0, x1 in [(0, -6), (BOARD_W, BOARD_W + 6)]:
        ax.plot([x0, x1], [y, y], color="#c00", lw=1.6, clip_on=False)
for (cx, cy) in [(xL, yB), (xR, yB), (xL, yT), (xR, yT)]:
    ax.plot(cx, cy, "o", mfc="white", mec="#1f6fd0", ms=7, zorder=5)
    ax.annotate(f"({cx:.2f}, {cy:.2f})", (cx, cy),
                textcoords="offset points", xytext=(8 if cx < BOARD_W / 2 else -8, 8 if cy < BOARD_H / 2 else -8),
                ha="left" if cx < BOARD_W / 2 else "right", va="bottom" if cy < BOARD_H / 2 else "top",
                fontsize=8, color="#0b3d70", zorder=6)
ax.set_xlim(-46, BOARD_W + 12); ax.set_ylim(-50, BOARD_H + 12)
ax.set_xlabel("mm from left edge"); ax.set_ylabel("mm from bottom edge")
ax.set_title("MARKING GUIDE — mark on the LCD-facing side, origin = bottom-left corner")

# ---- bevel cross-section ----
bx = fig.add_axes([0.69, 0.62, 0.28, 0.28]); T = THICK; r = RUN
xg = 0.0 if BEVEL_TOWARD == "lcd" else -r
xl = -r if BEVEL_TOWARD == "lcd" else 0.0
bx.add_patch(Polygon([(-11, 0), (xl, 0), (xg, T), (-11, T)], closed=True, fc="#eedcc0", ec="#7a5c33"))
bx.annotate("", (xg, T + 0.25), (xg + 3.6, T + 0.25), arrowprops=dict(arrowstyle="->", color="#1f6fd0"))
bx.text(xg + 3.9, T + 0.3, "glass", va="center", fontsize=8, color="#1f6fd0")
bx.annotate("", (xl, -0.25), (xl + 3.6, -0.25), arrowprops=dict(arrowstyle="->", color="#0a8f0a"))
bx.text(xl + 3.9, -0.55, "LCD\n(screen edge)" if BEVEL_TOWARD == "glass" else "LCD", va="center", fontsize=8, color="#0a8f0a")
bx.text(-11.4, T / 2, f"{T}", rotation=90, ha="right", va="center", color="#c00", fontsize=8)
bx.text(min(xg, xl) - 0.3, T / 2, "45°", ha="right", va="center", fontsize=9, color="#7a5c33")
bx.set_xlim(-13, 9); bx.set_ylim(-2.2, T + 2.2); bx.set_aspect("equal"); bx.axis("off")
bx.set_title("bevel (opens toward glass)", fontsize=9)

# ---- marking steps + table ----
tax = fig.add_axes([0.67, 0.07, 0.31, 0.46]); tax.axis("off")
steps = (
    "HOW TO MARK (LCD-facing side):\n"
    f"1. Board {BOARD_W:.0f} x {BOARD_H:.0f}, square the corners.\n"
    f"2. From left & right edges mark {mbx:.2f}.\n"
    f"3. From top & bottom edges mark {mby:.2f}.\n"
    "4. Mark at both ends of each edge,\n   join with a straightedge -> rectangle.\n"
    f"5. 45 deg bevel-cut along the line,\n   blade leaning so the cut opens to the\n   GLASS side. Window = {SW:.2f} x {SH:.2f}.\n"
    "(round to ~16.3 / ~21.7 if marking by eye)"
)
tax.text(0, 1.0, steps, va="top", ha="left", fontsize=9, family="monospace")
rows = [["board", f"{BOARD_W:.0f} x {BOARD_H:.0f} x {THICK}"],
        ["screen window", f"{SW:.2f} x {SH:.2f}"],
        ["border L/R", f"{mbx:.2f}"],
        ["border T/B", f"{mby:.2f}"],
        ["glass-face opening", f"{glassW:.2f} x {glassH:.2f}"],
        ["bevel", f"45°, {r:.2f}/edge -> glass"]]
t = tax.table(cellText=rows, colWidths=[0.55, 0.45], loc="lower left", cellLoc="left", bbox=[0, -0.02, 1, 0.42])
t.auto_set_font_size(False); t.set_fontsize(8.5)

fig.savefig("images/passepartout.png", dpi=130)
print("wrote images/passepartout.png")

# ---------------- DXF (R12) ----------------
def rect(cx, cy, w, h):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    return [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]


ox, oy = BOARD_W / 2, BOARD_H / 2
lines = {"BOARD": rect(ox, oy, BOARD_W, BOARD_H),
         "WINDOW_SCREEN": rect(ox, oy, SW, SH),
         "WINDOW_GLASS": rect(ox, oy, glassW, glassH)}
out = ["0", "SECTION", "2", "ENTITIES"]
for layer, segs in lines.items():
    for (x0, y0, x1, y1) in segs:
        out += ["0", "LINE", "8", layer,
                "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0.0",
                "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0.0"]
out += ["0", "ENDSEC", "0", "EOF"]
open("passepartout.dxf", "w").write("\n".join(out) + "\n")
print("wrote passepartout.dxf  (layers BOARD / WINDOW_SCREEN / WINDOW_GLASS)")
