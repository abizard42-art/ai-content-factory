#!/usr/bin/env python3
"""Review-only Peta Sunyi renderer v2: scene-aligned narration, subtitles and legible editorial graphics."""
import pathlib, subprocess, textwrap, os, math
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
    im=gradient((17,36,48),(36,65,68)).convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA")
    # Decorative schematic street network, explicitly not a navigational map.
    for i in range(18):
        x=70+i*58
        d.line((x,300,x+((i%4)-2)*90,1550),fill=(177,198,174,55),width=5)
    for j in range(14):
        y=380+j*88
        d.line((80,y,1000,y+((j%3)-1)*45),fill=(177,198,174,45),width=4)
    d.rounded_rectangle((95,180,985,1640),radius=38,outline=(230,218,185,110),width=4)
    centered(d,"BANDUNG",410,font(76,True),(246,239,219,255))
    centered(d,"KAWASAN KOTA",495,font(30),(195,211,197,255))
    d.rounded_rectangle((180,760,900,1110),radius=28,fill=(236,226,199,245))
    centered(d,"JALAN BANDA",865,font(52,True),(27,48,55,255))
    centered(d,"NO. 18",950,font(76,True),(27,48,55,255))
    centered(d,"Lokasi yang disebut dalam sumber",1210,font(29),(242,234,211,255))
    centered(d,"PETA SKEMATIK • BUKAN PETA NAVIGASI",1510,font(25),(226,210,170,255))
    centered(d,"Ilustrasi lokasi, bukan titik koordinat presisi",1560,font(21),(197,208,195,255))
    im.convert("RGB").save(path,quality=94)

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
        run(["edge-tts","--voice",VOICE,"--text",text,"--write-media",str(audio),"--write-subtitles",str(vtt)])
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
        # Burn the word/phrase timing produced by Edge TTS; subtitle remains inside mobile safe area.
        subtitle_filter=f"subtitles={vtt}:force_style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=210,MarginL=90,MarginR=90'"
        vf += ","+subtitle_filter
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
