#!/usr/bin/env python3
"""Overlay geometry.json (outline+ears+holes) on the clean render to confirm exact match."""
import numpy as np, cv2, json, math
from PIL import Image
G=json.load(open("geometry.json")); c=json.load(open("_cal2.json"))
sx,sy=c["sx"],c["sy"]; cx,cy=c["cxpx"],c["cypx"]; L,R,T,B=c["L"],c["R"],c["T"],c["B"]
def PX(p): return (int(round(cx+p[0]/sx)), int(round(cy-p[1]/sy)))
im=cv2.cvtColor(np.asarray(Image.open("clean_front.png").convert("L")),cv2.COLOR_GRAY2BGR)
# outline (blue)
op=np.array([PX(p) for p in G["outline"]],np.int32)
cv2.polylines(im,[op.reshape(-1,1,2)],True,(255,0,0),2)
# ears (red)
for k,poly in G["ears"].items():
    ep=np.array([PX(p) for p in poly],np.int32)
    cv2.polylines(im,[ep.reshape(-1,1,2)],True,(0,0,255),2)
# holes (green)
for k,(x,y) in G["holes"].items():
    cv2.circle(im,PX((x,y)),int(round(G["hole_d"]/2/sx)),(0,180,0),2)
    cv2.drawMarker(im,PX((x,y)),(0,180,0),cv2.MARKER_CROSS,18,1)
Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((760,int(760*im.shape[0]/im.shape[1]))).save("verify_full.png")
# corner montage
cor={"TL":(L,T),"TR":(R,T),"BL":(L,B),"BR":(R,B)};m=300;til={}
for k,(x,y) in cor.items():
    til[k]=Image.fromarray(cv2.cvtColor(im[max(0,y-m):y+m,max(0,x-m):x+m],cv2.COLOR_BGR2RGB)).resize((520,520),Image.NEAREST)
mon=Image.new("RGB",(1060,1060),"white")
mon.paste(til["TL"],(0,0));mon.paste(til["TR"],(540,0));mon.paste(til["BL"],(0,540));mon.paste(til["BR"],(540,540))
mon.save("verify_corners.png");print("wrote verify_full.png, verify_corners.png")
