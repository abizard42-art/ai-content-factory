#!/usr/bin/env python3
"""Subtle context-aware moving light and atmospheric overlays for history scenes."""
import argparse, math, os, random
from PIL import Image, ImageDraw, ImageFilter

p=argparse.ArgumentParser()
p.add_argument("--context",required=True)
p.add_argument("--duration",type=float,required=True)
p.add_argument("--out",required=True)
a=p.parse_args()
t=a.context.lower()
rules=[
    (("desert","gurun","sand","pasir","egypt","giza","sahara"),(255,218,155),"desert"),
    (("arctic","antarctic","kutub","glacier","ice","snow","salju"),(190,220,255),"cold"),
    (("underwater","ocean","sea","laut","samudra"),(100,190,220),"water"),
    (("forest","jungle","hutan","rainforest","pepohonan"),(175,220,165),"forest"),
    (("volcano","lava","eruption","erupsi","fire","flame","api"),(255,125,55),"fire"),
]
color,kind=((255,220,170),"neutral")
for keys,c,k in rules:
    if any(word in t for word in keys):
        color,kind=c,k
        break
os.makedirs(a.out,exist_ok=True)
W,H=360,640
fps=12
frames=max(1,int(math.ceil(a.duration*fps)))
rng=random.Random(20261117)
# A few broad, soft light shafts drift slowly; deliberately restrained.
shafts=[(rng.uniform(-W*.2,W*1.2),rng.uniform(.08,.48),rng.uniform(35,85),rng.uniform(.7,1.5),rng.uniform(0,math.tau)) for _ in range(3)]
for frame in range(frames):
    sec=frame/fps
    layer=Image.new("RGBA",(W,H),(0,0,0,0))
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    gd=ImageDraw.Draw(glow,"RGBA")
    for x0,y0,width,speed,phase in shafts:
        x=x0+math.sin(sec*speed*.22+phase)*22
        top=int(H*y0)
        # Wide translucent beam, fading toward the bottom.
        points=[(x-width*.25,top),(x+width*.25,top),(x+width*1.1,H),(x-width*1.1,H)]
        gd.polygon(points,fill=(*color,9 if kind!="fire" else 12))
    glow=glow.filter(ImageFilter.GaussianBlur(24))
    layer=Image.alpha_composite(layer,glow)
    d=ImageDraw.Draw(layer,"RGBA")
    if kind in ("desert","cold","forest","neutral"):
        # Slowly shifting atmospheric veil, not a solid fog layer.
        y=int(H*(.48+.035*math.sin(sec*.28)))
        d.rectangle((0,y,W,H),fill=(*color,3 if kind!="cold" else 4))
    elif kind=="water":
        # Soft moving caustic bands.
        for j in range(5):
            y=int(H*(.18+j*.16)+math.sin(sec*.55+j)*9)
            d.ellipse((-80,y-16,W+80,y+16),outline=(*color,12),width=3)
    elif kind=="fire":
        # A subtle warm pulse near the lower frame.
        pulse=int(5+3*(1+math.sin(sec*1.7)))
        d.ellipse((W*.12,H*.56,W*.88,H*1.18),fill=(*color,pulse))
    layer.resize((720,1280),Image.Resampling.BILINEAR).save(os.path.join(a.out,f"{frame:05d}.png"))
print(f"Background motion: {kind}; frames: {frames}")
