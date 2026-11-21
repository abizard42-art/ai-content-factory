#!/usr/bin/env python3
"""Review-only Peta Sunyi renderer v2: scene-aligned narration, subtitles and legible editorial graphics."""
import pathlib, subprocess, textwrap, os, math, time, json, urllib.parse, urllib.request, re, html
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = pathlib.Path("work")
ASSETS = ROOT / "assets"
OUT = pathlib.Path("output")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 30
VOICE = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")
SPEAKER_VOICES = {}
VISUAL_STYLE = "cinematic"

# Stickman intentionally removed: the location, atmosphere and evidence lead the story.
CONFIG = {}
SCENES = []

def run(args):
    subprocess.run(args, check=True)

def generate_tts(text, audio, subtitles, voice=None):
    """Retry transient Edge Read Aloud websocket failures without leaving partial files."""
    command = ["edge-tts", "--voice", voice or VOICE, "--text", text,
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
    headers = {"User-Agent": "PetaSunyiReviewRenderer/2.0 (documentary video map)"}
    coordinates = cfg.get("coordinates")
    if coordinates:
        lat, lon = float(coordinates["lat"]), float(coordinates["lon"])
        print(f"MAP_COORDINATES_OK={lat},{lon}", flush=True)
    else:
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

def convert_vtt_to_ass(vtt_path, speaker="NARATOR", source_text=None, audio_duration=None):
    """Render every spoken-script word; split captions into <=6-word cards without truncation."""
    lines = pathlib.Path(vtt_path).read_text(encoding="utf-8-sig").splitlines()
    cues, current = [], None
    for raw in lines:
        line = raw.strip()
        if not line:
            if current:
                cues.append(current)
                current = None
            continue
        if line == "WEBVTT" or line.startswith(("NOTE", "STYLE")):
            continue
        if "-->" in line:
            if current:
                cues.append(current)
            parts = line.split()
            current = {"start": parts[0], "end": parts[2], "text": []}
        elif current and not re.fullmatch(r"\d+", line):
            current["text"].append(line)
    if current:
        cues.append(current)

    def seconds(value):
        bits = value.replace(",", ".").split(":")
        if len(bits) == 2:
            hours, minutes, secs = 0, int(bits[0]), float(bits[1])
        else:
            hours, minutes, secs = int(bits[0]), int(bits[1]), float(bits[2])
        return hours * 3600 + minutes * 60 + secs

    def ass_time(value):
        value = max(0.0, value)
        hours = int(value // 3600)
        minutes = int((value % 3600) // 60)
        secs = value % 60
        whole = int(secs)
        centis = int(round((secs - whole) * 100))
        if centis >= 100:
            whole += 1
            centis = 0
        return f"{hours}:{minutes:02d}:{whole:02d}.{centis:02d}"

    def clean(value):
        value = html.unescape(re.sub(r"<[^>]+>", "", value))
        return re.sub(r"\s+", " ", value).strip()

    def tokens(value):
        return re.findall(r"[0-9a-zA-ZÀ-ÿ]+", clean(value).lower())

    timed_chunks = []
    vtt_source = " ".join(clean(t) for cue in cues for t in cue["text"])
    use_fallback = not cues
    if source_text is not None and tokens(vtt_source) != tokens(source_text):
        use_fallback = True

    if use_fallback:
        if not source_text or not audio_duration or audio_duration <= 0:
            raise RuntimeError(f"VTT cues missing or incomplete and no valid script fallback: {vtt_path}")
        words = clean(source_text).split()
        print(f"SUBTITLE_SCRIPT_FALLBACK=true; vtt_words={len(tokens(vtt_source))}; script_words={len(tokens(source_text))}", flush=True)
        total = max(1, len(words))
        for offset in range(0, len(words), 6):
            chunk = words[offset:offset + 6]
            start = audio_duration * offset / total
            end = audio_duration * min(offset + len(chunk), total) / total
            timed_chunks.append((start, end, chunk))
    else:
        for cue in cues:
            words = clean(" ".join(cue["text"])).split()
            if not words:
                continue
            start, end = seconds(cue["start"]), seconds(cue["end"])
            span = max(0.01, end - start)
            total = len(words)
            for offset in range(0, total, 6):
                chunk = words[offset:offset + 6]
                chunk_start = start + span * offset / total
                chunk_end = start + span * min(offset + len(chunk), total) / total
                timed_chunks.append((chunk_start, chunk_end, chunk))

    header = [
        "[Script Info]", "Title: Peta Sunyi subtitles", "ScriptType: v4.00+",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "PlayResX: 1080",
        "PlayResY: 1920", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,DejaVu Sans,34,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,110,110,245,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    events = []
    speaker_tag = re.sub(r"[^A-Z0-9 _-]", "", str(speaker).upper())[:24]
    for start, end, words in timed_chunks:
        if not words:
            continue
        caption = " ".join(words[:3]) + (r"\N" + " ".join(words[3:]) if len(words) > 3 else "")
        safe_text = (r"{\an8\fs25\b1\c&H00C9C9C9&}" + speaker_tag + r"\N{\rDefault}") + caption.replace("{", "(").replace("}", ")")
        events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{safe_text}")
    target = pathlib.Path(vtt_path).with_suffix(".ass")
    target.write_text("\n".join(header + events) + "\n", encoding="utf-8")
    if not events or target.stat().st_size == 0:
        raise RuntimeError(f"Subtitle conversion produced no ASS cues for {vtt_path}")
    print(f"SUBTITLE_CUES={len(events)}; max_words=6; script_fallback={str(use_fallback).lower()}", flush=True)
    return target

def make_rough_pencil(source, target):
    """Apply a restrained graphite/storyboard treatment to generated stills."""
    with Image.open(source) as original:
        base = ImageOps.autocontrast(original.convert("L"))
        edges = base.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.5))
        edges = Image.eval(edges, lambda px: 255 if px > 30 else 0)
        graphite = Image.blend(base, Image.eval(edges, lambda px: 255-px), 0.42)
        graphite = Image.eval(graphite, lambda px: max(0, min(255, int((px-118)*1.30+128))))
        paper = Image.new("L", graphite.size, 226)
        Image.blend(paper, graphite, 0.92).convert("RGB").save(target, quality=94)

def probe_duration(path):
    value=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],text=True)
    return float(value.strip())

def main():
    global CONFIG, SCENES
    config_path = pathlib.Path(os.getenv("EPISODE_CONFIG", "episodes/peta-sunyi/rs-dustira-cimahi.json"))
    CONFIG = json.loads(config_path.read_text(encoding="utf-8"))
    episode_id = CONFIG["episode_id"]
    SCENES = [(s["shot"], s["text"], s["title"], s["kind"], s.get("speaker", "NARATOR")) for s in CONFIG["scenes"]]
    SPEAKER_VOICES.update(CONFIG.get("speaker_voices", {}))
    global VISUAL_STYLE
    VISUAL_STYLE = CONFIG.get("visual_style", "cinematic")
    generated={"MAP":OUT/"graphic-map.jpg","FACT":OUT/"graphic-fact.jpg","END":OUT/"graphic-end.jpg"}
    make_map(generated["MAP"]); make_fact(generated["FACT"]); make_end(generated["END"])
    clips=[]
    for i,(shot,text,title,kind,speaker) in enumerate(SCENES,1):
        audio=OUT/f"scene-{i:02d}.mp3"
        vtt=OUT/f"scene-{i:02d}.vtt"
        voice = SPEAKER_VOICES.get(speaker, VOICE)
        generate_tts(text,audio,vtt,voice=voice)
        duration=probe_duration(audio)+0.35
        src=generated[shot] if shot in generated else ASSETS/f"peta-sunyi-{shot}.jpg"
        if not src.exists(): raise FileNotFoundError(f"Missing visual asset: {src}")
        if kind == "ai" and VISUAL_STYLE == "rough_pencil":
            styled = OUT/f"scene-{i:02d}-pencil.jpg"
            make_rough_pencil(src, styled)
            src = styled
        clip=OUT/f"scene-{i:02d}.mp4"
        vf=(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"zoompan=z='min(zoom+0.00025,1.045)':d={max(1,math.ceil(duration*FPS))}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
            f"drawbox=x=0:y=0:w=iw:h=116:color=black@0.48:t=fill,"
            f"drawtext=text='{title.replace(chr(39), chr(92)+chr(39))}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontcolor=white:fontsize=34:box=0:x=(w-text_w)/2:y=42")
        if kind=="ai":
            vf+=",drawbox=x=0:y=122:w=iw:h=62:color=black@0.62:t=fill"
            vf+=",drawtext=text='REKA ADEGAN  •  ILUSTRASI AI':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontcolor=white:fontsize=25:x=(w-text_w)/2:y=139"
        episode_label = CONFIG.get("episode_label")
        if episode_label:
            safe_label = str(episode_label).replace("'", "\\'")
            vf += ",drawbox=x=910:y=194:w=140:h=48:color=black@0.62:t=fill"
            vf += f",drawtext=text='{safe_label}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontcolor=white:fontsize=23:x=930:y=205"
        ass=convert_vtt_to_ass(vtt,speaker=speaker,source_text=text,audio_duration=probe_duration(audio))
        vf+=f",ass={ass}"
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
