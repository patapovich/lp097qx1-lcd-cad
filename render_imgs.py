#!/usr/bin/env python3
"""3D model views (front/rear iso) + per-ear overlay images."""
import json, numpy as np, cv2, cairosvg
import cadquery as cq
from PIL import Image

body = cq.importers.importStep("lcd_panel.step")
for name,dirv in [("model_3d",(1,-1,1)),("model_rear3d",(-1,-1,-1))]:
    cq.exporters.export(body, name+".svg",
        opt={"projectionDir":dirv,"showAxes":False,"width":900,"height":1000,
             "strokeColor":(40,40,40),"strokeWidth":0.4})
    cairosvg.svg2png(url=name+".svg", write_to=f"images/{name}.png", output_width=900)
    print("wrote images/"+name+".png")

# per-ear overlay images (clean render + traced ear poly + hole)
G=json.load(open("geometry.json")); c=json.load(open("_cal2.json"))
sx,sy,cx,cy=c["sx"],c["sy"],c["cxpx"],c["cypx"]; L,R,T,B=c["L"],c["R"],c["T"],c["B"]
def PX(p): return (int(round(cx+p[0]/sx)),int(round(cy-p[1]/sy)))
im=cv2.cvtColor(np.asarray(Image.open("clean_front.png").convert("L")),cv2.COLOR_GRAY2BGR)
cor={"TL":(L,T),"TR":(R,T),"BL":(L,B),"BR":(R,B)}
for k,poly in G["ears"].items():
    ov=im.copy()
    cv2.polylines(ov,[np.array([PX(p) for p in poly],np.int32).reshape(-1,1,2)],True,(0,0,255),2)
    x,y=PX(G["holes"][k]); cv2.circle(ov,(x,y),int(round(G["hole_d"]/2/sx)),(0,180,0),2)
    ex,ey=cor[k]; m=240
    crop=ov[max(0,ey-m):ey+m, max(0,ex-m):ex+m]
    Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB)).resize((460,460),Image.NEAREST).save(f"images/ear_{k}.png")
    print(f"wrote images/ear_{k}.png")
