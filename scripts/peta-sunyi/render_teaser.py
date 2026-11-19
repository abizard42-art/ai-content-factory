#!/usr/bin/env python3
"""Render a vertical Peta Sunyi teaser from five stills and one Edge TTS narration."""
import json, os, pathlib, re, subprocess, math

ROOT = pathlib.Path("output/teaser")
ROOT.mkdir(parents=True, exist_ok=True)
CFG = json.loads(pathlib.Path("episodes/peta-sunyi/teaser-lembang.json").read_text(encoding="utf-8"))

def run(args):
    subprocess.run(args, check=True)

def probe(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)], text=True).strip())

def ass_time(seconds):
    cs = int(round(max(0, seconds) * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, c = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"

def main():
    audio = ROOT / "teaser.mp3"
    if not audio.exists() or audio.stat().st_size == 0:
        raise RuntimeError("File TTS teaser tidak ditemukan.")
    images = [pathlib.Path(f"work/teaser/shot-{i:02d}.jpg") for i in range(1, 6)]
    for p in images:
        if not p.exists() or p.stat().st_size == 0:
            raise FileNotFoundError(f"Visual teaser tidak ditemukan: {p}")
    total = probe(audio)
    # Subtitle chunks: short, mobile-readable, with timings distributed over narration.
    words = re.findall(r"\S+", CFG["narration"])
    chunks = [words[i:i+5] for i in range(0, len(words), 5)]
    ass = ROOT / "teaser.ass"
    header = [
      "[Script Info]", "Title: Peta Sunyi Teaser Lembang", "ScriptType: v4.00+",
      "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
      "[V4+ Styles]",
      "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
      "Style: Default,DejaVu Sans,58,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,1,0,0,0,100,100,0,0,1,4,2,2,90,90,260,1", "", "[Events]",
      "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    events = []
    count = max(1, len(chunks))
    for i, chunk in enumerate(chunks):
        start = total * i / count
        end = total * (i + 1) / count
        caption = " ".join(chunk).replace("{","(").replace("}",")")
        events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{caption}")
    ass.write_text("\n".join(header + events) + "\n", encoding="utf-8")

    # Each still gets an equal share of the voice-over; subtle zoom keeps the frame alive.
    per = total / len(images)
    clips = []
    for i, image in enumerate(images):
        clip = ROOT / f"scene-{i+1:02d}.mp4"
        frames = max(1, math.ceil(per * 30))
        vf = (
          "scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920,"
          f"zoompan=z='min(zoom+0.00035,1.045)':d={frames}:"
          "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
          "setsar=1"
        )
        run(["ffmpeg","-y","-loop","1","-i",str(image),"-t",f"{per:.3f}","-vf",vf,
             "-r","30","-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(clip)])
        clips.append(clip)
    concat = ROOT / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")
    silent = ROOT / "teaser-visual.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    final = pathlib.Path("output/peta-sunyi-lembang-teaser-review.mp4")
    run(["ffmpeg","-y","-i",str(silent),"-i",str(audio),"-vf",f"ass={ass}",
         "-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast","-crf","21",
         "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(final)])
    print(f"TEASER_RENDERED={final}; duration_seconds={probe(final):.2f}; format=1080x1920; publish=false")

if __name__ == "__main__":
    main()
