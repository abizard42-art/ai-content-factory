#!/usr/bin/env python3
"""Build a review-only vertical Peta Sunyi cut from approved still assets."""
import os, subprocess, pathlib, json, textwrap

ROOT = pathlib.Path("work")
ASSETS = ROOT / "assets"
OUT = pathlib.Path("output")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 30
VOICE = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")

SCENES = [
    (8, "01B", "Di Bandung, ada sebuah rumah yang namanya bikin orang bertanya-tanya: Rumah Kentang. Konon, aroma kentang pernah tercium dari bangunan ini. Tapi cerita di baliknya jauh lebih mengerikan.", "RUMAH KENTANG • BANDUNG"),
    (7, None, "Bangunan yang dikenal sebagai Rumah Kentang ini berada di Jalan Banda Nomor 18, Bandung.", "JL. BANDA NO. 18 • BANDUNG"),
    (10, "03A", "Legenda yang beredar menyebut, aroma kentang rebus berasal dari tragedi seorang anak Belanda yang konon jatuh ke dalam kuali berisi kentang panas.", "LEGENDA YANG BEREDAR"),
    (6, "04A", "Tapi, benarkah tragedi itu pernah terjadi?", "BENARKAH PERNAH TERJADI?"),
    (13, "05B", "Dalam laporan detikJabar tahun 2025, Pramutadi, penjaga lama rumah ini, justru membantah cerita tentang anak yang jatuh ke kuali. Ia menyebut kemungkinan aroma itu berasal dari tanaman yang pernah ada di sekitar rumah.", "KESAKSIAN PENJAGA LAMA • DETIKJABAR, 2025"),
    (9, "06A", "RRI Bandung pada 2024 juga mengutip seorang warga yang telah lama tinggal di sekitar sana. Ia mengaku tidak pernah mencium aroma kentang.", "KESAKSIAN WARGA • RRI BANDUNG, 2024"),
    (12, None, "Namun ada satu hal yang bukan sekadar legenda. Dalam Peraturan Daerah Kota Bandung Nomor 7 Tahun 2018, Rumah Kentang di Jalan Banda Nomor 18 tercantum sebagai Bangunan Cagar Budaya Golongan A.", "CAGAR BUDAYA GOLONGAN A"),
    (11, "08A", "Mungkin misteri terbesar rumah ini bukanlah kisah hantunya, melainkan sejarah panjang bangunan yang masih belum seluruhnya kita ketahui.", "DI BALIK LEGENDA, ADA SEJARAH"),
    (9, None, "Menurutmu, cerita Rumah Kentang ini lahir dari kejadian nyata, atau hanya legenda yang terus diwariskan?", "FAKTA ATAU LEGENDA? • PETA SUNYI"),
]

def run(args):
    subprocess.run(args, check=True)

def main():
    OUT.mkdir(exist_ok=True)
    audio = OUT / "narration.mp3"
    narration = " ".join(s[2] for s in SCENES)
    run(["edge-tts", "--voice", VOICE, "--text", narration, "--write-media", str(audio)])
    clips = []
    for i, (duration, shot, narration_text, title) in enumerate(SCENES, 1):
        src = ASSETS / f"peta-sunyi-{shot}.jpg" if shot else None
        if src and src.exists():
            base = src
        else:
            # A simple generated background card keeps missing documentary assets explicit.
            from PIL import Image, ImageDraw, ImageFont
            base = OUT / f"card-{i:02d}.jpg"
            im = Image.new("RGB", (W, H), (19, 23, 28))
            d = ImageDraw.Draw(im)
            d.rectangle((70, 690, 1010, 1230), outline=(160, 160, 160), width=3)
            d.text((110, 850), "PETA SUNYI", fill=(230,230,230))
            d.text((110, 960), title[:44], fill=(255,255,255))
            d.text((110, 1090), "GRAFIS SEMENTARA • PERLU REVIEW", fill=(190,190,190))
            im.save(base, quality=92)
        # Each segment is normalized to 9:16 and receives a subtle Ken Burns push.
        clip = OUT / f"scene-{i:02d}.mp4"
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},"
            f"zoompan=z='min(zoom+0.00035,1.06)':d={duration*FPS}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
            f"drawtext=text='{title.replace(chr(39), chr(92)+chr(39))}':"
            "fontcolor=white:fontsize=48:box=1:boxcolor=black@0.55:"
            "boxborderw=24:x=(w-text_w)/2:y=h-260"
        )
        run(["ffmpeg","-y","-loop","1","-i",str(base),"-t",str(duration),
             "-vf",vf,"-r",str(FPS),"-pix_fmt","yuv420p","-an",str(clip)])
        clips.append(clip)
    concat = OUT / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips))
    silent = OUT / "picture-track.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    final = OUT / "peta-sunyi-rumah-kentang-review.mp4"
    run(["ffmpeg","-y","-i",str(silent),"-i",str(audio),"-map","0:v:0","-map","1:a:0",
         "-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(final)])
    print(f"RENDER_OK={final}")
    print("REVIEW_ONLY=true; NO PUBLISHING")

if __name__ == "__main__":
    main()
