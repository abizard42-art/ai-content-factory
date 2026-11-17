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
SCENES = [
    ("01B", "Di Bandung, ada sebuah rumah yang namanya bikin orang bertanya-tanya: Rumah Kentang. Konon, aroma kentang pernah tercium dari bangunan ini. Tapi cerita di baliknya jauh lebih mengerikan.", "RUMAH KENTANG • BANDUNG", "ai"),
    ("MAP", "Bangunan yang dikenal sebagai Rumah Kentang ini berada di Jalan Banda Nomor 18, Bandung.", "JL. BANDA NO. 18 • BANDUNG", "graphic"),
    ("03A", "Legenda yang beredar menyebut, aroma kentang rebus berasal dari tragedi seorang anak Belanda yang konon jatuh ke dalam kuali berisi kentang panas.", "LEGENDA YANG BEREDAR", "ai"),
    ("04A", "Tapi, benarkah tragedi itu pernah terjadi?", "BENARKAH PERNAH TERJADI?", "ai"),
    ("05B", "Dalam laporan detikJabar tahun 2025, Pramutadi, penjaga lama rumah ini, justru membantah cerita tentang anak yang jatuh ke kuali. Ia menyebut kemungkinan aroma itu berasal dari tanaman yang pernah ada di sekitar rumah.", "KESAKSIAN PENJAGA LAMA • DETIKJABAR, 2025", "ai"),
    ("06A", "RRI Bandung pada 2024 juga mengutip seorang warga yang telah lama tinggal di sekitar sana. Ia mengaku tidak pernah mencium aroma kentang.", "KESAKSIAN WARGA • RRI BANDUNG, 2024", "ai"),
    ("FACT", "Namun ada satu hal yang bukan sekadar legenda. Dalam Peraturan Daerah Kota Bandung Nomor 7 Tahun 2018, Rumah Kentang di Jalan Banda Nomor 18 tercantum sebagai Bangunan Cagar Budaya Golongan A.", "CAGAR BUDAYA GOLONGAN A", "graphic"),
    ("08A", "Mungkin misteri terbesar rumah ini bukanlah kisah hantunya, melainkan sejarah panjang bangunan yang masih belum seluruhnya kita ketahui.", "DI BALIK LEGENDA, ADA SEJARAH", "ai"),
    ("END", "Menurutmu, cerita Rumah Kentang ini lahir dari kejadian nyata, atau hanya legenda yang terus diwariskan?", "FAKTA ATAU LEGENDA?", "graphic"),
]

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
    """Render a real street map from OpenStreetMap road geometry."""
    query = urllib.parse.urlencode({"q": "Roemah Kentang 1908, Jalan Banda 18, Bandung, Indonesia", "format": "jsonv2", "limit": "1"})
    req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + query,
        headers={"User-Agent": "PetaSunyiReviewRenderer/1.0 (documentary video map)"})
    with urllib.request.urlopen(req, timeout=25) as response:
        places = json.loads(response.read().decode("utf-8"))
    if not places:
        raise RuntimeError("Nominatim could not locate Jalan Banda No. 18, Bandung")
    lat, lon = float(places[0]["lat"]), float(places[0]["lon"])
    overpass_query = '[out:json][timeout:40];(way["highway"](around:1100,' + str(lat) + ',' + str(lon) + '););out geom;'
    body = urllib.parse.urlencode({"data": overpass_query}).encode("utf-8")
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=body,
        headers={"User-Agent": "PetaSunyiReviewRenderer/1.0 (documentary video map)",
                 "Content-Type": "application/x-www-form-urlencoded"})
    osm = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=55) as response:
                osm = json.loads(response.read().decode("utf-8"))
            break
        except Exception as exc:
            if attempt == 2:
                raise RuntimeError(f"Could not retrieve OpenStreetMap road data: {exc}") from exc
            time.sleep(3 * (attempt + 1))
    im = Image.new("RGB", (W,H), (239,237,228))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0,0,W,210), fill=(24,43,48,255))
    d.text((72,55), "BANDUNG", font=font(66,True), fill=(250,246,232,255))
    d.text((76,137), "KAWASAN JALAN BANDA", font=font(29,True), fill=(207,218,204,255))
    left,top,right,bottom = 55,235,1025,1705
    d.rounded_rectangle((left,top,right,bottom), radius=24, fill=(247,246,239,255),
                        outline=(202,199,184,255), width=3)
    cos_lat = math.cos(math.radians(lat))
    meters_per_px = max(1100/(right-left-50), 1650/(bottom-top-50))
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
        raise RuntimeError("OpenStreetMap returned no roads around Jalan Banda")
    widths = {"motorway":9,"trunk":8,"primary":7,"secondary":6,"tertiary":5,
              "residential":3,"unclassified":3,"service":2,"living_street":3}
    for highway,name,pts in roads:
        color = (255,255,255,255) if highway in ("primary","secondary","tertiary","trunk") else (210,207,194,255)
        d.line(pts, fill=color, width=widths.get(highway,2), joint="curve")
    labelled = set()
    for highway,name,pts in roads:
        if not name or name in labelled or len(labelled) >= 15:
            continue
        if highway not in ("primary","secondary","tertiary","residential"):
            continue
        x,y = pts[len(pts)//2]
        if left+65 < x < right-65 and top+65 < y < bottom-65:
            ft = font(19 if highway in ("primary","secondary") else 16, highway in ("primary","secondary"))
            bb = d.textbbox((0,0),name,font=ft); tw,th=bb[2]-bb[0],bb[3]-bb[1]
            d.rounded_rectangle((x-tw//2-8,y-th//2-5,x+tw//2+8,y+th//2+5),
                                radius=7,fill=(247,246,239,220))
            d.text((x-tw//2,y-th//2-2),name,font=ft,fill=(79,91,88,255))
            labelled.add(name)
    px,py = project({"lat":lat,"lon":lon})
    d.ellipse((px-27,py-27,px+27,py+27),fill=(176,52,43,255),outline=(255,255,255,255),width=7)
    d.ellipse((px-8,py-8,px+8,py+8),fill=(255,255,255,255))
    label = "RUMAH KENTANG • JL. BANDA 18"
    pf=font(25,True); bb=d.textbbox((0,0),label,font=pf); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    tx=max(left+18,min(right-tw-38,px+38)); ty=max(top+18,min(bottom-th-28,py-68))
    d.rounded_rectangle((tx-12,ty-8,tx+tw+12,ty+th+8),radius=10,fill=(31,57,58,240))
    d.text((tx,ty-2),label,font=pf,fill=(255,250,235,255))
    d.rectangle((0,1730,W,H),fill=(24,43,48,255))
    d.text((62,1760),"PETA JALAN • KAWASAN BANDUNG WETAN",font=font(25,True),fill=(248,244,229,255))
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

def make_end(path):
    im=gradient((12,22,29),(39,54,57)).convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA")
    d.rounded_rectangle((85,390,995,1450),radius=40,outline=(208,194,158,150),width=3)
    centered(d,"PETA SUNYI",690,font(42,True),(221,211,185,255))
    centered(d,"FAKTA ATAU",900,font(72,True),(255,248,229,255))
    centered(d,"LEGENDA?",1010,font(104,True),(255,248,229,255))
    d.line((300,1135,780,1135),fill=(200,177,130,210),width=4)
    centered(d,"Rumah Kentang • Bandung",1230,font(30),(215,216,201,255))
    centered(d,"Tulis pendapatmu di komentar",1320,font(27),(184,202,193,255))
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
        elif current and not re.fullmatch(r"\\d+", line):
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
        phrase = re.sub(r"\\s+", " ", phrase).strip()
        if not phrase:
            continue
        wrapped = textwrap.wrap(phrase, width=34, max_lines=2, placeholder="…")
        safe_text = r"\\N".join(wrapped).replace("{", "(").replace("}", ")")
        events.append(f"Dialogue: 0,{ass_time(cue[0])},{ass_time(cue[1])},Default,,0,0,0,,{safe_text}")
    target = pathlib.Path(vtt_path).with_suffix(".ass")
    target.write_text("\\n".join(header + events) + "\\n", encoding="utf-8")
    if not events or target.stat().st_size == 0:
        raise RuntimeError(f"Subtitle conversion produced no ASS cues for {vtt_path}")
    return target


def probe_duration(path):
    value=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],text=True)
    return float(value.strip())

def main():
    generated={"MAP":OUT/"graphic-map.jpg","FACT":OUT/"graphic-fact.jpg","END":OUT/"graphic-end.jpg"}
    make_map(generated["MAP"]); make_fact(generated["FACT"]); make_end(generated["END"])
    clips=[]
    for i,(shot,text,title,kind) in enumerate(SCENES,1):
        audio=OUT/f"scene-{i:02d}.mp3"
        vtt=OUT/f"scene-{i:02d}.vtt"
        generate_tts(text, audio, vtt)
        duration=probe_duration(audio)+0.35
        src=generated[shot] if shot in generated else ASSETS/f"peta-sunyi-{shot}.jpg"
        if not src.exists(): raise FileNotFoundError(f"Missing visual asset: {src}")
        clip=OUT/f"scene-{i:02d}.mp4"
        vf=(
            f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"zoompan=z='min(zoom+0.00025,1.045)':d={max(1,math.ceil(duration*FPS))}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
            f"drawbox=x=0:y=0:w=iw:h=116:color=black@0.48:t=fill,"
            f"drawtext=text='{title.replace(chr(39), chr(92)+chr(39))}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontcolor=white:fontsize=34:box=0:x=(w-text_w)/2:y=42"
        )
        if kind=="ai":
            vf += ",drawbox=x=0:y=122:w=iw:h=62:color=black@0.62:t=fill"
            vf += ",drawtext=text='REKA ADEGAN  •  ILUSTRASI AI':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontcolor=white:fontsize=25:x=(w-text_w)/2:y=139"
        # Render normalized subtitles on an explicit 1080x1920 ASS canvas.
        ass = convert_vtt_to_ass(vtt)
        vf += f",ass={ass}"
        run(["ffmpeg","-y","-loop","1","-i",str(src),"-i",str(audio),"-t",f"{duration:.3f}",
             "-vf",vf,"-r",str(FPS),"-c:v","libx264","-preset","veryfast","-crf","20",
             "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest",str(clip)])
        clips.append(clip)
        print(f"SCENE_OK={i}; duration={duration:.2f}s; subtitle={vtt.name}")
    concat=OUT/"concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips))
    final=OUT/"peta-sunyi-rumah-kentang-review.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(final)])
    print(f"RENDER_OK={final}; duration={probe_duration(final):.2f}s")
    print("REVIEW_ONLY=true; NO PUBLISHING")

if __name__=="__main__":
    main()
