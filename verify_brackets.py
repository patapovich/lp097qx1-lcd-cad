#!/usr/bin/env python3
"""Assembly check for the photo-frame brackets.
 - top view: frame 182x242, panel (view-centered), active rect, both brackets, ear pockets.
 - side section (Y-Z at X=0): glass | lip | panel slot | back wall, total 15.
Writes images/brackets_assembly.png, images/brackets_section.png
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

G = json.load(open("geometry.json"))
HW, HH = G["outline_wh"][0] / 2, G["outline_wh"][1] / 2
TH = G["z"]["th"]; ACT = G["active"]; BEZ = G["bezel"]

FRAME_W, FRAME_H = 182.0, 242.0
HFW, HFH = FRAME_W / 2, FRAME_H / 2
VIEW_CENTER = True
SHIFT_X = -ACT["cx"] if VIEW_CENTER else 0.0
SHIFT_Y = -ACT["cy"] if VIEW_CENTER else 0.0
TOTAL_Z, SLOT_CLR, LIP_Y = 15.0, 0.15, 3.0
FIT_CLR, SEAT_CLR, POCKET_CLR, EAR_CLR, EAR_Z = 0.2, 0.1, 0.3, 1.5, 0.7
LX = (FRAME_W - FIT_CLR) / 2
FLANGE_Z0 = TH + SLOT_CLR


MIRROR_X = True
SX = -SHIFT_X if MIRROR_X else SHIFT_X      # panel-center X (mirror-aware)


def fx(gx):
    """geometry X -> frame X (panel shift, mirror-aware)."""
    return (-gx if MIRROR_X else gx) + SX


def ear_span(name):
    p = G["ears"][name]
    xs = [q[0] for q in p]; ys = [q[1] for q in p]
    return min(xs), max(xs), min(ys), max(ys)


def pocket_rect(name):
    """ear pocket bbox in frame coords (matches build_brackets.make_bracket)."""
    exmin, exmax, eymin, eymax = ear_span(name)
    ax0, ax1 = exmin + SHIFT_X, exmax + SHIFT_X
    if MIRROR_X:
        ax0, ax1 = -ax1, -ax0
    ay0, ay1 = eymin + SHIFT_Y, eymax + SHIFT_Y
    return ax0 - EAR_CLR, ax1 + EAR_CLR, ay0 - EAR_CLR, ay1 + EAR_CLR


def ear_frame_bbox(name):
    """actual ear bbox in frame coords (panel-shifted, mirror-aware)."""
    exmin, exmax, eymin, eymax = ear_span(name)
    ax0, ax1 = exmin + SHIFT_X, exmax + SHIFT_X
    if MIRROR_X:
        ax0, ax1 = -ax1, -ax0
    return ax0, ax1, eymin + SHIFT_Y, eymax + SHIFT_Y


# ---------- TOP VIEW (FRONT, from the glass: ears + brackets handed to match the real panel) ----------
fig, ax = plt.subplots(figsize=(7, 9))
ax.add_patch(Rectangle((-HFW, -HFH), FRAME_W, FRAME_H, fill=False, ec="black", lw=2))   # frame cavity

# brackets FIRST (they are BEHIND the LCD) — light, so the front ears read on top
for side in (+1, -1):
    edgeY = side * (HH + side * SHIFT_Y)
    webInnerY = edgeY + side * SEAT_CLR
    lipInnerY = edgeY - side * LIP_Y
    wallY = side * HFH
    stopL, stopR = SX - HW - POCKET_CLR, SX + HW + POCKET_CLR
    yl, yh = sorted((webInnerY, wallY))
    ax.add_patch(Rectangle((-LX, yl), 2 * LX, yh - yl, fc="#ffe9cf", ec="#b5651d", lw=1.0, alpha=.8))  # web (behind)
    yl, yh = sorted((lipInnerY, webInnerY))
    for x0, x1 in [(-LX, stopL), (stopR, LX)]:
        ax.add_patch(Rectangle((x0, yl), x1 - x0, yh - yl, fc="#ffe9cf", ec="#b5651d", lw=1.0, alpha=.8))
    ax.add_patch(Rectangle((stopL, yl), stopR - stopL, yh - yl, fc="none", ec="#b5651d", lw=0.8, ls=":"))

# panel outline (mirror-aware), semi-transparent so ears show
out = [(fx(x), y + SHIFT_Y) for x, y in G["outline"]]
ax.add_patch(Polygon(out, closed=True, fill=True, fc="#cfe3ff", ec="#1f6fd0", lw=1.2, alpha=.55))
# active area (centered on frame)
ax.add_patch(Rectangle((-ACT["W"] / 2, -ACT["H"] / 2), ACT["W"], ACT["H"],
                       fill=False, ec="#0a8f0a", lw=1.4, ls="--"))
# LUG EARS on TOP (front-side feature) — solid + hole markers, so they're clearly visible
for k in G["ears"]:
    ep = [(fx(x), y + SHIFT_Y) for x, y in G["ears"][k]]
    ax.add_patch(Polygon(ep, closed=True, fill=True, fc="#1f6fd0", ec="#0b3d70", lw=1.0, zorder=5))
    hx, hy = G["holes"][k]
    ax.plot(fx(hx), hy + SHIFT_Y, "o", mfc="white", mec="#0b3d70", ms=6, zorder=6)
# ear pockets (red dashed) — should sit on the ears
for side in (+1, -1):
    for e in (["TL", "TR"] if side > 0 else ["BL", "BR"]):
        px0, px1, py0, py1 = pocket_rect(e)
        ax.add_patch(Rectangle((px0, py0), px1 - px0, py1 - py0, fill=False, ec="red", lw=1.0, ls="--", zorder=4))

ax.axhline(0, color="0.6", lw=0.6); ax.axvline(0, color="0.6", lw=0.6)
ax.plot(0, 0, "+", color="#0a8f0a", ms=14, mew=2, zorder=8)
ax.set_aspect("equal"); ax.set_xlim(-HFW - 6, HFW + 6); ax.set_ylim(-HFH - 6, HFH + 6)
ax.set_title("FRONT view (from glass) — blue=lug ears (front), orange=brackets (behind)\nhanded to match the real panel; green '+' = frame center = active center")
ax.set_xlabel("X (mm)  (+ = right, as seen from the front)"); ax.set_ylabel("Y (mm)")
fig.tight_layout(); fig.savefig("images/brackets_assembly.png", dpi=130); plt.close(fig)
print("wrote images/brackets_assembly.png")

# ---------- EAR-POCKET COVERAGE (per ear zoom) ----------
fig, axes = plt.subplots(1, 4, figsize=(14, 4))
for axc, e in zip(axes, ["TL", "TR", "BL", "BR"]):
    ep = [(x + SHIFT_X, y + SHIFT_Y) for x, y in G["ears"][e]]
    if MIRROR_X:
        ep = [(-x, y) for x, y in ep]
    axc.add_patch(Polygon(ep, closed=True, fc="#9ec8f5", ec="#1f6fd0", lw=1.0))   # actual ear
    bx0, bx1, by0, by1 = ear_frame_bbox(e)
    px0, px1, py0, py1 = pocket_rect(e)
    axc.add_patch(Rectangle((px0, py0), px1 - px0, py1 - py0, fill=False, ec="red", lw=1.5, ls="--"))
    clr = min(bx0 - px0, px1 - bx1, by0 - py0, py1 - by1)                          # min clearance all sides
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    axc.set_xlim(cx - 8, cx + 8); axc.set_ylim(cy - 8, cy + 8); axc.set_aspect("equal")
    axc.set_title(f"{e}  min clr {clr:.2f}mm", fontsize=10)
    axc.grid(True, lw=0.3, alpha=0.5)
fig.suptitle("Ear pocket (red) covers actual ear (blue) — clearance all round (EAR_CLR=1.5)")
fig.tight_layout(); fig.savefig("images/brackets_ear_coverage.png", dpi=120); plt.close(fig)
print("wrote images/brackets_ear_coverage.png")

# ---------- SIDE SECTION (Y-Z at X=0) ----------
fig, ax = plt.subplots(figsize=(9, 4))
ax.axvline(0, color="#2aa3d6", lw=4, alpha=0.5)            # glass plane (Z=0)
ax.text(0, TOTAL_Z + 0.6, "glass", color="#2aa3d6", ha="center")
ax.axvline(TOTAL_Z, color="0.4", lw=4, alpha=0.5)         # frame backing
ax.text(TOTAL_Z, TOTAL_Z + 0.6, "frame back", color="0.4", ha="center")
# panel cross section in Y-Z (screen front on the glass at Z=0)
pTop, pBot = HH + SHIFT_Y, -(HH - SHIFT_Y)
ax.add_patch(Rectangle((0, pBot), TH, pTop - pBot, fc="#cfe3ff", ec="#1f6fd0", label="panel"))
ax.axvline(FLANGE_Z0, color="#b5651d", lw=0.8, ls=":")
ax.text(FLANGE_Z0, HFH + 2, f"shelf {FLANGE_Z0:.2f}\n(behind LCD,\nslot fits 2.60)", color="#b5651d", ha="center", fontsize=8)
for side in (+1, -1):
    edgeY = side * (HH + side * SHIFT_Y)
    webInnerY = edgeY + side * SEAT_CLR; lipInnerY = edgeY - side * LIP_Y; wallY = side * HFH
    yl, yh = sorted((lipInnerY, wallY))
    # web (full Z, in the gap) + rear shelf (behind panel) as Z-Y rectangles (x=Z, y=Y)
    ax.add_patch(Rectangle((0, sorted((webInnerY, wallY))[0]), TOTAL_Z,
                           abs(wallY - webInnerY), fc="#ffd9a8", ec="#b5651d"))           # web full Z, on glass
    ax.add_patch(Rectangle((FLANGE_Z0, yl), TOTAL_Z - FLANGE_Z0, yh - yl,
                           fc="#ffd9a8", ec="#b5651d"))                                     # rear shelf
# press direction: shelf (behind LCD) -> glass
ax.annotate("press", xy=(0.4, 0), xytext=(FLANGE_Z0, 0),
            arrowprops=dict(arrowstyle="->", color="#c00", lw=2), color="#c00", va="center")
ax.text(TOTAL_Z * 0.55, HFH - 6, "ears + pockets on FRONT (glass) face", color="#b5651d", ha="center", fontsize=8)
ax.set_xlim(-1.5, TOTAL_Z + 2); ax.set_ylim(-HFH - 4, HFH + 8)
ax.set_xlabel("Z (mm)  0=glass -> 15=frame back"); ax.set_ylabel("Y (mm)")
ax.set_title("Side section: 2.60 LCD in a 2.75 slot, screen ON glass; shelf BEHIND presses it -> glass (15mm)")
fig.tight_layout(); fig.savefig("images/brackets_section.png", dpi=130); plt.close(fig)
print("wrote images/brackets_section.png")

# ---------- ORIENTATION (assembly + print) ----------
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.axvline(0, color="#2aa3d6", lw=6, alpha=.5); ax.text(0, 6.6, "GLASS\n(front)", color="#2aa3d6", ha="center", va="bottom", fontsize=9)
ax.axvline(TOTAL_Z, color="0.4", lw=6, alpha=.5); ax.text(TOTAL_Z, 6.6, "frame\nbacking", color="0.4", ha="center", va="bottom", fontsize=9)
ax.add_patch(Rectangle((0, -2), TH, 4, fc="#cfe3ff", ec="#1f6fd0")); ax.text(TH/2, -2.4, "LCD\n(screen on glass)", color="#1f6fd0", ha="center", va="top", fontsize=8)
ax.add_patch(Rectangle((FLANGE_Z0, 2.2), TOTAL_Z - FLANGE_Z0, 2.2, fc="#ffd9a8", ec="#b5651d"))   # shelf behind (schematic)
ax.text((FLANGE_Z0 + TOTAL_Z) / 2, 3.3, "shelf BEHIND LCD", color="#b5651d", ha="center", fontsize=8)
ax.add_patch(Rectangle((TOTAL_Z - 0.6, -4.5), 0.6, 3, fc="none", ec="#c00", hatch="///"))
ax.text(TOTAL_Z, -4.8, '"BACK" face\n= print-bed face\n= frame backing', color="#c00", ha="center", va="top", fontsize=8)
ax.annotate("press", xy=(0.5, 0), xytext=(FLANGE_Z0, 0), arrowprops=dict(arrowstyle="->", color="#c00", lw=2.5), color="#c00", va="center", fontsize=11)
ax.text(TH + 0.3, 1.4, "open (screen\nmeets glass)", color="#1f6fd0", ha="left", fontsize=8)
ax.set_xlim(-2, TOTAL_Z + 3); ax.set_ylim(-6, 8); ax.set_yticks([])
ax.set_xlabel("Z (mm)   0 = glass  →  15 = frame back")
ax.set_title("ORIENTATION: open/ear-pocket face → GLASS;  flat \"BACK\" face → frame backing.  Print BACK face on the bed.")
fig.tight_layout(); fig.savefig("images/brackets_orientation.png", dpi=130); plt.close(fig)
print("wrote images/brackets_orientation.png")
