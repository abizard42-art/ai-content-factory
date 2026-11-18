#!/usr/bin/env python3
"""Review-only Peta Sunyi renderer v2: scene-aligned narration, subtitles and legible editorial graphics."""
import pathlib, subprocess, textwrap, os, math, time, json, urllib.parse, urllib.request, re, html
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = pathlib.Path("work")
ASSETS = ROOT / "assets"
OUT = pathlib.Path("output")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 30
VOICE = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")

# Stickman intentionally removed: the location, atmosphere and evidence lead the story.
CONFIG = {}
SCENES = []

def run(args):
    subprocess.run(args, check=True)

def generate_tts(text, audio, subtitles):
    """Retry transient Edge Read Aloud websocket failures without leaving partial files."""
    command = ["edge-tts", "--voice", VOICE, "--text", text,
               "--write-media", str(audio), "--write-subtitles", str(subtitles)]
    delays = [2, 4, 8, 15, 25]
    for attempt in range(len(delays) + 1):
        try:
            subprocess.run(command, check=True, timeout=120)
            if not audio.exists() or audio.stat().st_size == 0:
                raise RuntimeError("Edge TTS returned without an audio file")
            if not subtitles.exists() or subtitles.stat().st_size == 0:
                raise RuntimeError("Edge TTS returned without a subtitle file")
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, RuntimeError) as exc:
            audio.unlink(missing_ok=True)
            subtitles.unlink(missing_ok=True)
            if attempt >= len(delays):
                raise RuntimeError(
                    f"Edge TTS failed after {attempt + 1} attempts for this scene: {exc}"
                ) from exc
            delay = delays[attempt]
            print(f"TTS_RETRY={attempt + 1}; waiting {delay}s; reason={exc}", flush=True)
            time.sleep(delay)

def font(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)

def gradient(top, bottom):
    im = Image.new("RGB", (W,H))
    p = im.load()
    for y in range(H):
        t=y/(H-1)
        c=tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
        for x in range(W): p[x,y]=c
    return im

def centered(draw, text, y, fnt, fill, anchor="mm"):
    draw.text((W//2,y), text, font=fnt, fill=fill, anchor=anchor)

def make_map(path):
    """Render an episode-specific street map from OpenStreetMap road geometry."""
    cfg = CONFIG.get("map", {})
    query = cfg.get("query", "")
    if not query:
        raise RuntimeError("Episode config is missing map.query")
    # Prefer verified episode coordinates when supplied; use Nominatim only as a fallback.
    if cfg.get("lat") is not None and cfg.get("lon") is not None:
        lat, lon = float(cfg["lat"]), float(cfg["lon"])
        print(f"MAP_COORDINATES_CONFIGURED={lat},{lon}; source=episode_config", flush=True)
    else:
        headers = {"User-Agent": "PetaSunyiReviewRenderer/2.0 (documentary video map)"}
        params = urllib.parse.urlencode({"q": query, "format": "jsonv2", "limit": "1"})
        req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + params, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            places = json.loads(response.read().decode("utf-8"))
        if not places:
            raise RuntimeError("Nominatim could not resolve episode location: " + query)
        place = places[0]
        lat, lon = float(place["lat"]), float(place["lon"])
        print("MAP_GEOCODE_OK=" + place.get("display_name", query), flush=True)
    overpass_query = '[out:json][timeout:40];(way["highway"](around:1000,' + str(lat) + ',' + str(lon) + '););out geom;'
    body = urllib.parse.urlencode({"data": overpass_query}).encode("utf-8")
    osm_req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=body,
        headers={"User-Agent": "PetaSunyiReviewRenderer/2.0", "Content-Type": "application/x-www-form-urlencoded"})
    osm = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(osm_req, timeout=55) as response:
                osm = json.loads(response.read().decode("utf-8"))
            break
        except Exception as exc:
            if attempt == 2:
                raise RuntimeError(f"Could not retrieve OpenStreetMap road data: {exc}") from exc
            time.sleep(3 * (attempt + 1))
    im = Image.new("RGB", (W,H), (239,237,228))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0,0,W,210), fill=(24,43,48,255))
    d.text((72,55), cfg.get("title","LOKASI"), font=font(66,True), fill=(250,246,232,255))
    d.text((76,137), cfg.get("subtitle","PETA LOKASI"), font=font(29,True), fill=(207,218,204,255))
    left,top,right,bottom = 55,235,1025,1705
    d.rounded_rectangle((left,top,right,bottom), radius=24, fill=(247,246,239,255), outline=(202,199,184,255), width=3)
    cos_lat = math.cos(math.radians(lat))
    meters_per_px = max(1000/(right-left-50), 1500/(bottom-top-50))
    def project(p):
        xm = (float(p["lon"])-lon)*111320*cos_lat
        ym = (lat-float(p["lat"]))*111320
        return (int((left+right)/2+xm/meters_per_px), int((top+bottom)/2+ym/meters_per_px))
    roads = []
    for el in osm.get("elements", []):
        if el.get("type") != "way" or len(el.get("geometry",[])) < 2:
            continue
        tags = el.get("tags", {})
        pts = [project(p) for p in el["geometry"]]
        if any(left <= x <= right and top <= y <= bottom for x,y in pts):
            roads.append((tags.get("highway","residential"), tags.get("name",""), pts))
    if not roads:
        raise RuntimeError("OpenStreetMap returned no roads around " + query)
    widths = {"primary":7,"secondary":6,"tertiary":5,"residential":3,"service":2}
    for highway,name,pts in roads:
        color = (255,255,255,255) if highway in ("primary","secondary","tertiary") else (210,207,194,255)
        d.line(pts, fill=color, width=widths.get(highway,2), joint="curve")
    labelled=set()
    for highway,name,pts in roads:
        if not name or name in labelled or len(labelled)>=15 or highway not in ("primary","secondary","tertiary","residential"):
            continue
        x,y=pts[len(pts)//2]
        if left+65<x<right-65 and top+65<y<bottom-65:
            ft=font(18,highway in ("primary","secondary")); bb=d.textbbox((0,0),name,font=ft); tw,th=bb[2]-bb[0],bb[3]-bb[1]
            d.rounded_rectangle((x-tw//2-8,y-th//2-5,x+tw//2+8,y+th//2+5),radius=7,fill=(247,246,239,220))
            d.text((x-tw//2,y-th//2-2),name,font=ft,fill=(79,91,88,255)); labelled.add(name)
    px,py=project({"lat":lat,"lon":lon})
    d.ellipse((px-27,py-27,px+27,py+27),fill=(176,52,43,255),outline=(255,255,255,255),width=7)
    d.ellipse((px-8,py-8,px+8,py+8),fill=(255,255,255,255))
    label=cfg.get("pin_label","LOKASI")
    pf=font(24,True); bb=d.textbbox((0,0),label,font=pf); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    tx=max(left+18,min(right-tw-38,px+38)); ty=max(top+18,min(bottom-th-28,py-68))
    d.rounded_rectangle((tx-12,ty-8,tx+tw+12,ty+th+8),radius=10,fill=(31,57,58,240))
    d.text((tx,ty-2),label,font=pf,fill=(255,250,235,255))
    d.rectangle((0,1730,W,H),fill=(24,43,48,255))
    d.text((62,1760),cfg.get("footer","PETA JALAN"),font=font(25,True),fill=(248,244,229,255))
    d.text((62,1810),"Data peta: © OpenStreetMap contributors",font=font(21),fill=(214,220,204,255))
    d.text((62,1855),"Penanda lokasi bersifat indikatif",font=font(18),fill=(185,199,188,255))
    im.save(path,quality=95)

def make_fact(path):
    im=gradient((25,43,48),(51,68,65)).convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA")
    d.rounded_rectangle((76,260,1004,1650),radius=36,fill=(239,231,208,248),outline=(205,187,148,255),width=5)
    d.text((140,360),"ARSIP • KOTA BANDUNG",font=font(29,True),fill=(86,99,88,255))
    d.line((140,425,940,425),fill=(151,157,135,255),width=3)
    d.text((140,520),"PERDA KOTA BANDUNG",font=font(37,True),fill=(35,53,57,255))
    d.text((140,580),"NOMOR 7 TAHUN 2018",font=font(39,True),fill=(35,53,57,255))
    d.text((140,760),"RUMAH KENTANG",font=font(52,True),fill=(35,53,57,255))
    d.text((140,840),"Jl. Banda No. 18",font=font(40),fill=(67,82,78,255))
    d.rounded_rectangle((130,1030,950,1370),radius=24,fill=(39,76,72,255))
    centered(d,"BANGUNAN CAGAR BUDAYA",1120,font(34,True),(241,234,212,255))
    centered(d,"GOLONGAN A",1240,font(66,True),(255,255,255,255))
    centered(d,"Visualisasi informasi • sumber: JDIH Kota Bandung",1510,font(23),(82,94,83,255))
    im.convert("RGB").save(path,quality=95)

def make_fact(path):
    cfg = CONFIG.get("fact", {})
    im=gradient((25,43,48),(51,68,65)).convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA")
    d.rounded_rectangle((76,250,1004,1660),radius=36,fill=(239,231,208,248),outline=(205,187,148,255),width=5)
    d.text((140,340),cfg.get("heading","CATATAN SEJARAH"),font=font(38,True),fill=(35,53,57,255))
    d.line((140,420,940,420),fill=(151,157,135,255),width=3)
    lines=cfg.get("lines",[])
    y=540
    for line in lines:
        wrapped=textwrap.wrap(line,width=30)
        for part in wrapped:
            d.text((140,y),part,font=font(31,True),fill=(43,62,61,255)); y+=52
        y+=45
    d.rounded_rectangle((125,1280,955,1510),radius=24,fill=(39,76,72,255))
    centered(d,cfg.get("highlight","FAKTA DAN LEGENDA"),1395,font(34,True),(255,255,255,255))
    centered(d,"Informasi diringkas dari sumber yang dicantumkan",1580,font(20),(82,94,83,255))
    im.convert("RGB").save(path,quality=95)

def make_end(path):
    cfg=CONFIG.get("end",{})
    im=gradient((12,22,29),(39,54,57)).convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA")
    d.rounded_rectangle((85,390,995,1450),radius=40,outline=(208,194,158,150),width=3)
    centered(d,"PETA SUNYI",650,font(42,True),(221,211,185,255))
    centered(d,cfg.get("title","JEJAK SEJARAH"),900,font(68,True),(255,248,229,255))
    centered(d,cfg.get("subtitle","MISTERI LOKAL"),1040,font(29,True),(215,216,201,255))
    d.line((300,1160,780,1160),fill=(200,177,130,210),width=4)
    centered(d,cfg.get("cta","TULIS PENDAPATMU"),1280,font(29),(184,202,193,255))
    im.convert("RGB").save(path,quality=95)

def convert_vtt_to_ass(vtt_path):
    """Convert WebVTT to ASS with an explicit 1080x1920 canvas and bottom-safe subtitle style."""
    lines = pathlib.Path(vtt_path).read_text(encoding="utf-8-sig").splitlines()
    cues, current = [], []
    for raw in lines:
        line = raw.strip()
        if not line:
            if current:
                cues.append(current); current = []
            continue
        if line == "WEBVTT" or line.startswith("NOTE") or line.startswith("STYLE"):
            continue
        if "-->" in line:
            if current:
                cues.append(current)
            parts = line.split()
            current = [parts[0], parts[2]]
        elif current and not re.fullmatch(r"\d+", line):
            current.append(line)
    if current:
        cues.append(current)

    def ass_time(value):
        bits = value.replace(",", ".").split(":")
        if len(bits) == 2:
            hours, minutes, seconds = 0, int(bits[0]), float(bits[1])
        else:
            hours, minutes, seconds = int(bits[0]), int(bits[1]), float(bits[2])
        whole = int(seconds)
        centis = int(round((seconds - whole) * 100))
        if centis >= 100:
            whole += 1; centis = 0
        return f"{hours}:{minutes:02d}:{whole:02d}.{centis:02d}"

    header = [
        "[Script Info]",
        "Title: Peta Sunyi subtitles",
        "ScriptType: v4.00+",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,DejaVu Sans,34,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,110,110,245,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    events = []
    for cue in cues:
        if len(cue) < 3:
            continue
        phrase = " ".join(html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in cue[2:])
        phrase = re.sub(r"\s+", " ", phrase).strip()
        if not phrase:
            continue
        wrapped = textwrap.wrap(phrase, width=34, max_lines=2, placeholder="…")
        safe_text = r"\N".join(wrapped).replace("{", "(").replace("}", ")")
        events.append(f"Dialogue: 0,{ass_time(cue[0])},{ass_time(cue[1])},Default,,0,0,0,,{safe_text}")
    target = pathlib.Path(vtt_path).with_suffix(".ass")
    target.write_text("\n".join(header + events) + "\n", encoding="utf-8")
    if not events or target.stat().st_size == 0:
        raise RuntimeError(f"Subtitle conversion produced no ASS cues for {vtt_path}")
    return target


def probe_duration(path):
    value=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],text=True)
    return float(value.strip())


def motion_profile(shot, kind, duration):
    """Return deterministic, subtle camera motion for each Peta Sunyi scene."""
    # Direction changes keep a sequence of stills from feeling like one repeated slideshow effect.
    profiles = {
        "01A": "push_left", "03A": "push_right", "04A": "push_left",
        "05A": "push_right", "06A": "pull_center", "07A": "push_left",
        "08A": "push_center", "END": "pull_center",
        "MAP": "graphic_right", "FACT": "graphic_left",
    }
    profile = profiles.get(shot, "push_center" if kind == "ai" else "graphic_right")
    frames = max(1, math.ceil(duration * FPS))
    if profile == "pull_center":
        z = "max(1.0,1.055-on*0.00028)"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)"
    elif profile == "push_left":
        z = "min(zoom+0.00024,1.05)"
        x = "iw*0.38-iw/zoom*0.38"
        y = "ih/2-(ih/zoom/2)"
    elif profile == "push_right":
        z = "min(zoom+0.00024,1.05)"
        x = "iw*0.62-iw/zoom*0.62"
        y = "ih/2-(ih/zoom/2)"
    elif profile == "graphic_left":
        z = "min(zoom+0.00010,1.025)"
        x = "iw*0.43-iw/zoom*0.43"
        y = "ih/2-(ih/zoom/2)"
    elif profile == "graphic_right":
        z = "min(zoom+0.00010,1.025)"
        x = "iw*0.57-iw/zoom*0.57"
        y = "ih/2-(ih/zoom/2)"
    else:
        z = "min(zoom+0.00024,1.05)"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)"
    return {"profile": profile, "frames": frames, "zoom": z, "x": x, "y": y}


def main():
    global CONFIG, SCENES
    config_path = pathlib.Path(os.getenv("EPISODE_CONFIG", "episodes/peta-sunyi/rs-dustira-cimahi.json"))
    CONFIG = json.loads(config_path.read_text(encoding="utf-8"))
    episode_id = CONFIG["episode_id"]
    SCENES = [(s["shot"], s["text"], s["title"], s["kind"], s.get("ambient_context", "")) for s in CONFIG["scenes"]]
    generated={"MAP":OUT/"graphic-map.jpg","FACT":OUT/"graphic-fact.jpg","END":OUT/"graphic-end.jpg"}
    make_map(generated["MAP"]); make_fact(generated["FACT"]); make_end(generated["END"])
    clips=[]
    for i,(shot,text,title,kind,ambient_context) in enumerate(SCENES,1):
        audio=OUT/f"scene-{i:02d}.mp3"
        vtt=OUT/f"scene-{i:02d}.vtt"
        generate_tts(text,audio,vtt)
        duration=probe_duration(audio)+0.35
        src=generated[shot] if shot in generated else ASSETS/f"peta-sunyi-{shot}.jpg"
        if not src.exists(): raise FileNotFoundError(f"Missing visual asset: {src}")
        clip=OUT/f"scene-{i:02d}.mp4"
        motion=motion_profile(shot,kind,duration)
        vf=(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"zoompan=z='{motion['zoom']}':d={motion['frames']}:"
            f"x='{motion['x']}':y='{motion['y']}':s={W}x{H}:fps={FPS},"
            f"drawbox=x=0:y=0:w=iw:h=116:color=black@0.48:t=fill,"
            f"drawtext=text='{title.replace(chr(39), chr(92)+chr(39))}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontcolor=white:fontsize=34:box=0:x=(w-text_w)/2:y=42")
        if kind=="ai":
            vf+=",vignette=PI/5,noise=alls=2:allf=t"
        else:
            vf+=",noise=alls=1:allf=t"
        ambient_dir = OUT / f"ambient-{i:02d}"
        if ambient_context:
            run(["python", "scripts/background_motion.py", "--context", ambient_context,
                 "--duration", f"{duration:.3f}", "--out", str(ambient_dir)])
        print(f"MOTION_PROFILE={shot}; type={motion['profile']}; zoom={motion['zoom']}; ambient={ambient_context or 'off'}", flush=True)
        if kind=="ai":
            vf+=",drawbox=x=0:y=122:w=iw:h=62:color=black@0.62:t=fill"
            vf+=",drawtext=text='REKA ADEGAN  •  ILUSTRASI AI':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontcolor=white:fontsize=25:x=(w-text_w)/2:y=139"
        ass=convert_vtt_to_ass(vtt)
        vf+=f",ass={ass}"
        if ambient_context:
            ambient_input = str(ambient_dir / "%05d.png")
            filter_graph = (
                f"[0:v]{vf}[base];"
                f"[2:v]scale={W}:{H},format=rgba[ambient];"
                f"[base][ambient]overlay=shortest=1:format=auto[v]"
            )
            run(["ffmpeg","-y","-loop","1","-i",str(src),"-i",str(audio),
                 "-framerate","12","-i",ambient_input,"-t",f"{duration:.3f}",
                 "-filter_complex",filter_graph,"-map","[v]","-map","1:a",
                 "-r",str(FPS),"-c:v","libx264","-preset","veryfast","-crf","20",
                 "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest",str(clip)])
        else:
            run(["ffmpeg","-y","-loop","1","-i",str(src),"-i",str(audio),"-t",f"{duration:.3f}",
                 "-vf",vf,"-r",str(FPS),"-c:v","libx264","-preset","veryfast","-crf","20",
                 "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest",str(clip)])
        clips.append(clip)
        print(f"SCENE_OK={i}; shot={shot}; duration={duration:.2f}s; subtitle={vtt.name}")
    concat=OUT/"concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips))
    final=OUT/f"{episode_id}-review.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(final)])
    print(f"RENDER_OK={final}; duration={probe_duration(final):.2f}s")
    print("REVIEW_ONLY=true; NO PUBLISHING")



if __name__ == "__main__":
    main()
