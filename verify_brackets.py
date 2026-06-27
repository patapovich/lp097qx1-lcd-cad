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
TOTAL_Z, PRELOAD, LIP_Y = 15.0, 0.15, 3.0
FIT_CLR, SEAT_CLR, POCKET_CLR, EAR_CLR, EAR_Z = 0.2, 0.1, 0.3, 1.5, 2.0
LX = (FRAME_W - FIT_CLR) / 2
FLANGE_Z0 = TH - PRELOAD


def ear_span(name):
    p = G["ears"][name]
    xs = [q[0] for q in p]; ys = [q[1] for q in p]
    return min(xs), max(xs), min(ys), max(ys)


# ---------- TOP VIEW ----------
fig, ax = plt.subplots(figsize=(7, 9))
# frame cavity
ax.add_patch(Rectangle((-HFW, -HFH), FRAME_W, FRAME_H, fill=False, ec="black", lw=2))
# panel outline (shifted = view centered)
out = [(x + SHIFT_X, y + SHIFT_Y) for x, y in G["outline"]]
ax.add_patch(Polygon(out, closed=True, fill=True, fc="#cfe3ff", ec="#1f6fd0", lw=1.2))
# ears
for k in G["ears"]:
    ep = [(x + SHIFT_X, y + SHIFT_Y) for x, y in G["ears"][k]]
    ax.add_patch(Polygon(ep, closed=True, fill=True, fc="#9ec8f5", ec="#1f6fd0", lw=0.8))
# active area (centered on frame)
ax.add_patch(Rectangle((ACT["cx"] + SHIFT_X - ACT["W"] / 2, ACT["cy"] + SHIFT_Y - ACT["H"] / 2),
                       ACT["W"], ACT["H"], fill=False, ec="#0a8f0a", lw=1.4, ls="--"))

# brackets
for side in (+1, -1):
    edgeY = side * (HH + side * SHIFT_Y)
    webInnerY = edgeY + side * SEAT_CLR
    lipInnerY = edgeY - side * LIP_Y
    wallY = side * HFH
    stopL, stopR = SHIFT_X - HW - POCKET_CLR, SHIFT_X + HW + POCKET_CLR
    yl, yh = sorted((webInnerY, wallY))
    ax.add_patch(Rectangle((-LX, yl), 2 * LX, yh - yl, fc="#ffd9a8", ec="#b5651d", lw=1.0))   # web
    yl, yh = sorted((lipInnerY, webInnerY))
    for x0, x1 in [(-LX, stopL), (stopR, LX)]:                                                 # end stops
        ax.add_patch(Rectangle((x0, yl), x1 - x0, yh - yl, fc="#ffd9a8", ec="#b5651d", lw=1.0))
    ax.add_patch(Rectangle((stopL, yl), stopR - stopL, yh - yl, fc="none", ec="#b5651d",        # rear shelf (behind panel)
                           lw=0.8, ls=":"))
    # ear pockets (white notch)
    for e in (["TL", "TR"] if side > 0 else ["BL", "BR"]):
        exmin, exmax, eymin, eymax = ear_span(e)
        tipY = (eymax if side > 0 else eymin) + SHIFT_Y
        a, c = sorted((edgeY - side * 2.0, tipY + side * EAR_CLR))
        ax.add_patch(Rectangle((exmin - EAR_CLR, a), (exmax - exmin) + 2 * EAR_CLR, c - a,
                               fc="white", ec="red", lw=1.0, ls="--"))

ax.axhline(0, color="0.6", lw=0.6); ax.axvline(0, color="0.6", lw=0.6)
ax.plot(0, 0, "+", color="#0a8f0a", ms=14, mew=2)
ax.set_aspect("equal"); ax.set_xlim(-HFW - 6, HFW + 6); ax.set_ylim(-HFH - 6, HFH + 6)
ax.set_title("Bracket assembly (top view) — green '+' = frame center = active center")
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.tight_layout(); fig.savefig("images/brackets_assembly.png", dpi=130); plt.close(fig)
print("wrote images/brackets_assembly.png")

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
ax.text(FLANGE_Z0, HFH + 2, f"shelf {FLANGE_Z0:.2f}\n(0.15 proud)", color="#b5651d", ha="center", fontsize=8)
for side in (+1, -1):
    edgeY = side * (HH + side * SHIFT_Y)
    webInnerY = edgeY + side * SEAT_CLR; lipInnerY = edgeY - side * LIP_Y; wallY = side * HFH
    yl, yh = sorted((lipInnerY, wallY))
    # web (full Z, in the gap) + rear shelf (behind panel) as Z-Y rectangles (x=Z, y=Y)
    ax.add_patch(Rectangle((0, sorted((webInnerY, wallY))[0]), TOTAL_Z,
                           abs(wallY - webInnerY), fc="#ffd9a8", ec="#b5651d"))           # web full Z, on glass
    ax.add_patch(Rectangle((FLANGE_Z0, yl), TOTAL_Z - FLANGE_Z0, yh - yl,
                           fc="#ffd9a8", ec="#b5651d"))                                     # rear shelf
ax.set_xlim(-1.5, TOTAL_Z + 2); ax.set_ylim(-HFH - 4, HFH + 8)
ax.set_xlabel("Z (mm)  0=glass -> 15=frame back"); ax.set_ylabel("Y (mm)")
ax.set_title("Side section: screen ON glass (Z0), rear shelf 0.15 proud presses LCD forward — total 15mm")
fig.tight_layout(); fig.savefig("images/brackets_section.png", dpi=130); plt.close(fig)
print("wrote images/brackets_section.png")
