#!/usr/bin/env python3
"""Context-aware ambient overlays for vertical history scenes."""
import argparse, math, os, random
from PIL import Image, ImageDraw

p=argparse.ArgumentParser()
p.add_argument("--context", required=True)
p.add_argument("--duration", type=float, required=True)
p.add_argument("--out", required=True)
a=p.parse_args()
text=a.context.lower()
rules=[
    (("desert","gurun","sand","pasir","egypt","giza","sahara"),"dust"),
    (("arctic","antarctic","kutub","glacier","ice","es","snow","salju","frost"),"snow"),
    (("rain","hujan","storm","badai","monsoon"),"rain"),
    (("underwater","ocean","sea","laut","underwater","samudra"),"underwater"),
    (("volcano","volcanic","lava","gunung berapi","eruption","erupsi"),"embers"),
    (("forest","jungle","hutan","rainforest","pepohonan"),"forest"),
    (("fire","flame","api","forge","tungku"),"embers"),
]
kind="none"
for keys, value in rules:
    if any(k in text for k in keys):
        kind=value
        break
os.makedirs(a.out,exist_ok=True)
W,H=360,640
fps=12
frames=max(1,int(math.ceil(a.duration*fps)))
rng=random.Random(20261116)
count={"dust":38,"snow":46,"rain":75,"underwater":28,"embers":22,"forest":20}.get(kind,0)
particles=[]
for _ in range(count):
    particles.append([rng.uniform(0,W),rng.uniform(0,H),rng.uniform(0.5,2.2),rng.uniform(0,math.tau),rng.uniform(1,3.2)])
for frame in range(frames):
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(im,"RGBA")
    t=frame/fps
    if kind=="forest":
        # Very subtle drifting mist ribbons, not leaf-shaped clutter.
        for j in range(4):
            y=int((H*(.25+j*.18))+math.sin(t*.45+j)*12)
            d.ellipse((-80,y-24,W+80,y+24),fill=(210,225,210,10))
    for x,y,s,phase,alpha in particles:
        if kind=="dust":
            xx=(x+t*(8+s*8)+math.sin(t*.8+phase)*9)%W
            yy=(y-t*(2+s*1.8))%H
            rad=s*1.4
            d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),fill=(238,207,151,int(18+alpha*9)))
        elif kind=="snow":
            xx=(x+t*(2+s*2)+math.sin(t*.7+phase)*8)%W
            yy=(y+t*(9+s*10))%H
            rad=max(1,s*.75)
            d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),fill=(235,246,255,int(45+alpha*18)))
        elif kind=="rain":
            xx=(x-t*12)%W; yy=(y+t*(90+s*50))%H
            d.line((xx,yy,xx-3,yy+12+s*4),fill=(190,215,235,45),width=1)
        elif kind=="underwater":
            xx=(x+math.sin(t*.8+phase)*8)%W
            yy=(y-t*(8+s*5))%H
            rad=s*2
            d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),outline=(190,230,245,38),width=1)
        elif kind=="embers":
            xx=(x+math.sin(t+phase)*10)%W
            yy=(y-t*(12+s*8))%H
            rad=max(1,s*.65)
            d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),fill=(255,151,65,65))
    im.resize((720,1280),Image.Resampling.BILINEAR).save(os.path.join(a.out,f"{frame:05d}.png"))
print(f"Ambient visual: {kind}; frames: {frames}")
