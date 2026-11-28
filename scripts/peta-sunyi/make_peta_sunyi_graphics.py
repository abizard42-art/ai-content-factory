#!/usr/bin/env python3
"""Create legible, source-aware timeline and evidence graphics for Peta Sunyi episodes."""
import json, pathlib, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

cfg_path = pathlib.Path(sys.argv[1])
out_dir = pathlib.Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
W, H = 1080, 1920
BG = (24, 31, 34); PANEL = (235, 226, 204); INK = (39, 48, 48)
GOLD = (174, 143, 91); MUTED = (105, 111, 99); RED = (116, 53, 48)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(size, bold=False): return ImageFont.truetype(BOLD if bold else FONT, size)
def wrap(draw, text, x, y, width, size=25, fill=INK, bold=False, leading=1.35):
    ft=f(size,bold); words=text.split(); line=""; lines=[]
    for word in words:
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=ft)[2] <= width: line=test
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    for line in lines:
        draw.text((x,y),line,font=ft,fill=fill); y += int(size*leading)
    return y
def base(kicker,title):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,210),fill=(16,24,27))
    d.text((72,48),kicker,font=f(25,True),fill=GOLD)
    wrap(d,title,72,96,920,48,(244,236,218),True,1.2)
    d.line((72,220,1008,220),fill=GOLD,width=3)
    d.text((72,1830),"PETA SUNYI  •  CATATAN INVESTIGASI",font=f(21,True),fill=(198,185,155))
    return im,d
def timeline():
    im,d=base("URUTAN SUMBER","TIGA TITIK WAKTU")
    items=cfg.get("timeline",[])
    y=340; xline=126
    d.line((xline,y,xline,y+1120),fill=GOLD,width=6)
    for i,item in enumerate(items):
        cy=y+i*370
        d.ellipse((xline-20,cy-20,xline+20,cy+20),fill=RED,outline=PANEL,width=4)
        d.rounded_rectangle((190,cy-62,980,cy+270),radius=22,fill=PANEL,outline=GOLD,width=3)
        d.text((225,cy-30),item.get("date",""),font=f(34,True),fill=RED)
        d.text((225,cy+28),item.get("title",""),font=f(27,True),fill=INK)
        wrap(d,item.get("detail",""),225,cy+82,700,23,INK,False)
        d.text((225,cy+208),item.get("status",""),font=f(19,True),fill=MUTED)
    im.save(out_dir/"peta-sunyi-TIMELINE.jpg",quality=95)
def evidence():
    im,d=base("PEMERIKSAAN SILANG","DUA FILM • DUA JEJAK SUMBER")
    items=cfg.get("evidence_board",[])
    y=310
    for item in items:
        d.rounded_rectangle((68,y,1012,y+650),radius=24,fill=PANEL,outline=GOLD,width=3)
        wrap(d,item.get("label",""),105,y+34,860,29,RED,True)
        d.text((105,y+105),"SUMBER A",font=f(20,True),fill=MUTED)
        yy=wrap(d,item.get("left",""),105,y+145,830,24,INK,False)
        d.line((105,yy+15,970,yy+15),fill=GOLD,width=2)
        d.text((105,yy+38),"SUMBER B",font=f(20,True),fill=MUTED)
        yy=wrap(d,item.get("right",""),105,yy+78,830,24,INK,False)
        d.rounded_rectangle((98,y+520,982,y+610),radius=15,fill=(42,62,60))
        wrap(d,item.get("verdict",""),125,y+545,830,21,(245,236,215),True)
        y += 700
    im.save(out_dir/"peta-sunyi-EVIDENCE.jpg",quality=95)
timeline(); evidence()
print("PETA_SUNYI_GRAPHICS_OK=TIMELINE,EVIDENCE")
