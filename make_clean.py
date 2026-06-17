#!/usr/bin/env python3
"""Strip non-geometry markings from p17.svg by colour, rasterize clean geometry."""
import cairosvg, numpy as np
from PIL import Image

SRC = "p17.svg"
# colours to remove (whiten): olive dims+centerlines, green active-ref, header grays
REMOVE = [
    "rgb(47.842407%, 47.842407%, 0%)",   # olive  - dimension lines + dash-dot centerlines
    "rgb(0%, 47.842407%, 0%)",           # green  - active-area reference
    "rgb(50.196838%, 50.196838%, 50.196838%)",  # 50% gray - page header text
    "rgb(75.294495%, 75.294495%, 75.294495%)",  # 75% gray - frame
]
# KEEP: rgb(0%,0%,0%) black + rgb(33.198547%...) gray  = object geometry

svg = open(SRC).read()
n = 0
for c in REMOVE:
    n += svg.count(c)
    svg = svg.replace(c, "rgb(100%, 100%, 100%)")
open("p17_clean.svg", "w").write(svg)
print(f"whitened {n} colour refs -> p17_clean.svg")

SCALE = 8                       # 8 * 72dpi = 576 dpi over full 612x792pt page
W = int(612 * SCALE)
cairosvg.svg2png(url="p17_clean.svg", write_to="clean_full.png", output_width=W)
im = np.asarray(Image.open("clean_full.png").convert("RGB"))
print("clean_full.png", im.shape, "scale", SCALE, "px_per_pt", SCALE)

# locate ink bbox (non-white) to crop the drawing region
ink = (im.min(axis=2) < 200)
ys, xs = np.where(ink)
print(f"ink bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]  ({xs.max()-xs.min()}x{ys.max()-ys.min()} px)")
np.save("_clean_scale.npy", np.array([SCALE], float))
