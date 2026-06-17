#!/usr/bin/env python3
"""Stage A2: filled silhouette + outer contour of outline+ears from CLEAN crop."""
import numpy as np, cv2
from scipy import ndimage as ndi
from PIL import Image

im = np.asarray(Image.open("clean_front.png").convert("L"))
H, W = im.shape
ink = (im < 215).astype(np.uint8)
# close corner gaps (faint line breaks), then fill enclosed interior
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
closed = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, k)
filled = ndi.binary_fill_holes(closed).astype(np.uint8)
# largest connected component = front panel (outline+ears); drop side strips/arrows/ticks
n, lab, stats, _ = cv2.connectedComponentsWithStats(filled, 8)
big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
panel = (lab == big).astype(np.uint8)
area = int(panel.sum())
ys, xs = np.where(panel)
print(f"panel area={area}px  bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]  ({xs.max()-xs.min()}x{ys.max()-ys.min()})")
np.save("_panel.npy", panel.astype(bool))

cnts, _ = cv2.findContours(panel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cnt = max(cnts, key=cv2.contourArea).reshape(-1, 2)
print("outer contour pts", len(cnt), "contour area", cv2.contourArea(cnt))
np.save("_outer.npy", cnt)

dbg = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
cv2.drawContours(dbg, [cnt.reshape(-1,1,2)], -1, (0,0,255), 3)
Image.fromarray(cv2.cvtColor(dbg, cv2.COLOR_BGR2RGB)).resize((760,int(760*H/W))).save("dbg_outer.png")
print("wrote dbg_outer.png")
