#!/usr/bin/env python3
"""Peta Sunyi long-form horror renderer: 16:9, multi-speaker TTS, subtitles, pencil stills."""
import json, os, pathlib, re, subprocess, textwrap, html, math, time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = pathlib.Path("work")
ASSETS = ROOT / "assets"
OUT = pathlib.Path("output")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1920, 1080, 25
DEFAULT_VOICE = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")

def run(args):
    subprocess.run(args, check=True)

def font(size, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, size)

def duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)], text=True).strip())

def tts(text, audio, vtt, voice):
    delays = [2,4,8,15]
    for attempt in range(len(delays)+1):
        try:
            subprocess.run(["edge-tts","--voice",voice,"--text",text,"--write-media",str(audio),"--write-subtitles",str(vtt)],check=True,timeout=150)
            if audio.stat().st_size and vtt.stat().st_size:
                return
            raise RuntimeError("TTS menghasilkan file kosong")
        except Exception:
            audio.unlink(missing_ok=True); vtt.unlink(missing_ok=True)
            if attempt == len(delays):
                raise
            time.sleep(delays[attempt])

def pencil(source, target):
    with Image.open(source) as im:
        gray = ImageOps.autocontrast(im.convert("L"))
        edges = gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.7))
        edges = Image.eval(edges, lambda p: 255 if p > 26 else 0)
        sketch = Image.blend(gray, Image.eval(edges, lambda p: 255-p), 0.38)
        sketch = Image.eval(sketch, lambda p: max(0,min(255,int((p-112)*1.22+128))))
        paper = Image.new("L", sketch.size, 226)
        Image.blend(paper, sketch, 0.94).convert("RGB").save(target, quality=94)

def ass_time(s):
    p=s.replace(",",".").split(":")
    if len(p)==2: h,m,sec=0,int(p[0]),float(p[1])
    else: h,m,sec=int(p[0]),int(p[1]),float(p[2])
    whole=int(sec); cs=round((sec-whole)*100)
    if cs>=100: whole+=1; cs=0
    return f"{h}:{m:02d}:{whole:02d}.{cs:02d}"

def subtitles(vtt, target, speaker):
    lines=pathlib.Path(vtt).read_text(encoding="utf-8-sig").splitlines()
    cues=[]; cur=[]
    for line in lines:
        line=line.strip()
        if not line:
            if cur: cues.append(cur); cur=[]
        elif "-->" in line:
            if cur: cues.append(cur)
            p=line.split(); cur=[p[0],p[2]]
        elif cur and line!="WEBVTT" and not line.isdigit():
            cur.append(line)
    if cur: cues.append(cur)
    head=[
      "[Script Info]","Title: Peta Sunyi Long Form","ScriptType: v4.00+","WrapStyle: 2",
      "ScaledBorderAndShadow: yes","PlayResX: 1920","PlayResY: 1080","","[V4+ Styles]",
      "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
      "Style: Default,DejaVu Sans,44,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,0,0,1,3,1,2,180,180,85,1","","[Events]",
      "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    ev=[]
    for c in cues:
        if len(c)<3: continue
        phrase=" ".join(html.unescape(re.sub(r"<[^>]+>","",x)).strip() for x in c[2:])
        phrase=re.sub(r"\s+"," ",phrase).strip()
        if not phrase: continue
        wrapped=textwrap.wrap(phrase,width=58)[:2]
        tag=re.sub(r"[^A-Z0-9 _-]","",speaker.upper())[:22]
        text=r"{\an8\fs30\b1\c&H00D6D6D6&}"+tag+r"\N{\rDefault}"+r"\N".join(wrapped).replace("{","(").replace("}",")")
        ev.append(f"Dialogue: 0,{ass_time(c[0])},{ass_time(c[1])},Default,,0,0,0,,{text}")
    pathlib.Path(target).write_text("\n".join(head+ev)+"\n",encoding="utf-8")
    if not ev: raise RuntimeError(f"Tidak ada cue subtitle: {vtt}")
    return target

def main():
    cfg_path=pathlib.Path(os.getenv("EPISODE_CONFIG","episodes/peta-sunyi/long-horror-lembang-camping.json"))
    cfg=json.loads(cfg_path.read_text(encoding="utf-8"))
    eid=cfg["episode_id"]
    voices=cfg.get("speaker_voices",{})
    style=cfg.get("visual_style","rough_pencil")
    clips=[]
    for i,scene in enumerate(cfg["scenes"],1):
        speaker=scene.get("speaker","NARATOR")
        voice=voices.get(speaker,DEFAULT_VOICE)
        audio=OUT/f"long-{i:02d}.mp3"; vtt=OUT/f"long-{i:02d}.vtt"
        tts(scene["text"],audio,vtt,voice)
        length=duration(audio)+0.45
        src=ASSETS/f"peta-sunyi-{scene['shot']}.jpg"
        if not src.exists(): raise FileNotFoundError(f"Aset visual tidak ditemukan: {src}")
        if style=="rough_pencil":
            styled=OUT/f"long-{i:02d}-pencil.jpg"; pencil(src,styled); src=styled
        ass=subtitles(vtt,OUT/f"long-{i:02d}.ass",speaker)
        title=scene.get("title","").replace("\\","\\\\").replace("'","\\'")
        vf=(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"zoompan=z='min(zoom+0.00018,1.035)':d={max(1,math.ceil(length*FPS))}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
            "drawbox=x=0:y=0:w=iw:h=100:color=black@0.55:t=fill,"
            f"drawtext=text='{title}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            "fontcolor=white:fontsize=38:x=(w-text_w)/2:y=29,"
            "drawbox=x=0:y=100:w=iw:h=42:color=black@0.58:t=fill,"
            "drawtext=text='REKA ADEGAN • ILUSTRASI AI':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            "fontcolor=white:fontsize=23:x=(w-text_w)/2:y=108,"
            f"ass={ass}")
        clip=OUT/f"long-{i:02d}.mp4"
        run(["ffmpeg","-y","-loop","1","-i",str(src),"-i",str(audio),"-t",f"{length:.3f}",
             "-vf",vf,"-r",str(FPS),"-c:v","libx264","-preset","veryfast","-crf","20",
             "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest",str(clip)])
        clips.append(clip)
        print(f"LONG_SCENE_OK={i}; speaker={speaker}; seconds={length:.1f}")
    concat=OUT/"long-concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips),encoding="utf-8")
    final=OUT/f"{eid}-long-review.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(final)])
    print(f"LONG_RENDER_OK={final}; duration={duration(final):.1f}s; format=1920x1080")
    print("REVIEW_ONLY=true; NO PUBLISHING")

if __name__=="__main__":
    main()
