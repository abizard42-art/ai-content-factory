#!/usr/bin/env python3
"""Peta Sunyi long-form horror renderer: 16:9, multi-speaker TTS, subtitles, pencil stills."""
import json, os, pathlib, re, subprocess, textwrap, html, math, time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from animated_overlays import create_overlay

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

def tts(text, audio, vtt, voice, rate="+0%", pitch="+0Hz", volume="+0%"):
    delays = [2,4,8,15]
    for attempt in range(len(delays)+1):
        try:
            subprocess.run(["edge-tts","--voice",voice,"--rate",str(rate),"--pitch",str(pitch),"--volume",str(volume),
                            "--text",text,"--write-media",str(audio),"--write-subtitles",str(vtt)],check=True,timeout=150)
            if audio.stat().st_size and vtt.stat().st_size:
                return
            raise RuntimeError("TTS menghasilkan file kosong")
        except Exception:
            audio.unlink(missing_ok=True); vtt.unlink(missing_ok=True)
            if attempt == len(delays):
                raise
            time.sleep(delays[attempt])


def split_delivery_phrases(text, split_commas=False):
    """Split only at natural punctuation boundaries; preserve every source word."""
    pattern = r".+?(?:[.!?]+[\"')\]]*|[,;]+)|.+$" if split_commas else r".+?[.!?]+[\"')\]]*|.+$"
    return [part.strip() for part in re.findall(pattern, text, flags=re.S) if part.strip()]

def tts_with_delivery(text, audio, vtt, voice, rate, pitch, volume, delivery, dramatic_pause_after=None):
    """Render one scene with scene-level pacing and optional phrase-level dramatic holds."""
    if delivery == "natural":
        tts(text, audio, vtt, voice, rate=rate, pitch=pitch, volume=volume)
        return
    split_commas = delivery in ("suspense", "reflective")
    phrases = split_delivery_phrases(text, split_commas=split_commas)
    if not phrases:
        tts(text, audio, vtt, voice, rate=rate, pitch=pitch, volume=volume)
        return
    pause_map = {"paced": (0, 320), "suspense": (170, 460), "reflective": (220, 520), "urgent": (0, 170)}
    comma_pause, sentence_pause = pause_map.get(delivery, (0, 320))
    dramatic = set(dramatic_pause_after or [])
    work = OUT / "delivery_segments"
    work.mkdir(parents=True, exist_ok=True)
    concat_entries = []
    vtt_cues = []
    elapsed = 0.0
    pause_total = 0.0
    for index, phrase in enumerate(phrases):
        part_audio = work / f"{audio.stem}-{index:03d}.mp3"
        part_vtt = work / f"{audio.stem}-{index:03d}.vtt"
        tts(phrase, part_audio, part_vtt, voice, rate=rate, pitch=pitch, volume=volume)
        concat_entries.append(part_audio)
        part_duration = duration(part_audio)
        raw = part_vtt.read_text(encoding="utf-8-sig").splitlines()
        cue = None
        for line in raw:
            line = line.strip()
            if "-->" in line:
                if cue:
                    vtt_cues.append((elapsed + cue[0], elapsed + cue[1], cue[2]))
                times = line.split()
                cue = [timestamp_seconds(times[0]), timestamp_seconds(times[2]), []]
            elif cue and line and line != "WEBVTT" and not line.isdigit():
                cue[2].append(line)
        if cue:
            vtt_cues.append((elapsed + cue[0], elapsed + cue[1], cue[2]))
        elapsed += part_duration
        ending = phrase.rstrip()[-1:]
        pause = sentence_pause if ending in ".!?" else comma_pause if ending in ",;" else 0
        if phrase in dramatic:
            pause = max(pause, 850)
        if pause:
            silence = work / f"{audio.stem}-{index:03d}-silence.mp3"
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                            "-t", f"{pause / 1000:.3f}", "-q:a", "7", str(silence)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            concat_entries.append(silence)
            elapsed += pause / 1000.0
            pause_total += pause / 1000.0
    concat_file = work / f"{audio.stem}-concat.txt"
    concat_file.write_text("".join("file '" + str(path.resolve()) + "'\n" for path in concat_entries), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(audio)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    vtt_lines = ["WEBVTT", ""]
    for start, end, cue_words in vtt_cues:
        vtt_lines += [f"{vtt_timestamp(start)} --> {vtt_timestamp(end)}",
                      *cue_words, ""]
    vtt.write_text("\n".join(vtt_lines), encoding="utf-8")
    print(f"TTS_DELIVERY={delivery}; phrases={len(phrases)}; inserted_pause_seconds={pause_total:.2f}")

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

def timestamp_seconds(value):
    parts = value.replace(",", ".").split(":")
    if len(parts) == 2:
        hours, minutes, seconds = 0, int(parts[0]), float(parts[1])
    else:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def seconds_ass(value):
    value = max(0.0, value)
    hours = int(value // 3600)
    minutes = int((value % 3600) // 60)
    seconds = value % 60
    whole = int(seconds)
    centiseconds = int(round((seconds - whole) * 100))
    if centiseconds >= 100:
        whole += 1
        centiseconds = 0
    return f"{hours}:{minutes:02d}:{whole:02d}.{centiseconds:02d}"

def vtt_timestamp(value):
    milliseconds = int(round(max(0.0, value) * 1000))
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"

def clean_caption_text(value):
    value = html.unescape(re.sub(r"<[^>]+>", "", value))
    return re.sub(r"\s+", " ", value).strip()

def word_tokens(value):
    return re.findall(r"\S+", clean_caption_text(value))

def normalized_words(value):
    return re.findall(r"[0-9a-zA-ZÀ-ÿ]+", value.lower())

def split_caption_words(words, max_words=6):
    return [words[i:i + max_words] for i in range(0, len(words), max_words)]

def subtitles(vtt, target, speaker, source_text, audio_duration):
    lines = pathlib.Path(vtt).read_text(encoding="utf-8-sig").splitlines()
    cues = []
    current = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if current:
                cues.append(current)
                current = None
            continue
        if "-->" in line:
            if current:
                cues.append(current)
            timing = line.split()
            current = {"start": timestamp_seconds(timing[0]), "end": timestamp_seconds(timing[2]), "text": []}
        elif current and line != "WEBVTT" and not line.isdigit():
            current["text"].append(line)
    if current:
        cues.append(current)

    vtt_text = " ".join(clean_caption_text(x) for cue in cues for x in cue["text"])
    source_tokens = normalized_words(source_text)
    vtt_tokens = normalized_words(vtt_text)
    use_source_fallback = not cues or vtt_tokens != source_tokens

    timed_chunks = []
    if not use_source_fallback:
        for cue in cues:
            words = word_tokens(" ".join(cue["text"]))
            if not words:
                continue
            chunks = split_caption_words(words, 6)
            total_words = len(words)
            span = max(0.01, cue["end"] - cue["start"])
            elapsed_words = 0
            for chunk in chunks:
                chunk_start = cue["start"] + span * elapsed_words / total_words
                elapsed_words += len(chunk)
                chunk_end = cue["start"] + span * elapsed_words / total_words
                timed_chunks.append((chunk_start, chunk_end, chunk))
    else:
        # Safety fallback: subtitle the complete approved script rather than silently
        # trusting an incomplete ASR/TTS VTT transcript.
        words = word_tokens(source_text)
        chunks = split_caption_words(words, 6)
        total_words = max(1, len(words))
        cursor = 0
        for chunk in chunks:
            chunk_start = audio_duration * cursor / total_words
            cursor += len(chunk)
            chunk_end = audio_duration * cursor / total_words
            timed_chunks.append((chunk_start, chunk_end, chunk))
        print(f"SUBTITLE_SOURCE_FALLBACK=true; vtt_words={len(vtt_tokens)}; script_words={len(source_tokens)}")

    head = [
      "[Script Info]", "Title: Peta Sunyi Long Form", "ScriptType: v4.00+",
      "WrapStyle: 2", "ScaledBorderAndShadow: yes", "PlayResX: 1920",
      "PlayResY: 1080", "", "[V4+ Styles]",
      "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
      "Style: Default,DejaVu Sans,44,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,0,0,1,3,1,2,180,180,85,1", "", "[Events]",
      "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    events = []
    tag = re.sub(r"[^A-Z0-9 _-]", "", speaker.upper())[:22]
    for start_time, end_time, words in timed_chunks:
        if not words:
            continue
        # Keep each subtitle card to <= 6 words, arranged over at most two lines.
        if len(words) > 3:
            caption = " ".join(words[:3]) + r"\N" + " ".join(words[3:])
        else:
            caption = " ".join(words)
        caption = caption.replace("{", "(").replace("}", ")")
        text = r"{\an8\fs30\b1\c&H00D6D6D6&}" + tag + r"\N{\rDefault}" + caption
        events.append(
            f"Dialogue: 0,{seconds_ass(start_time)},{seconds_ass(end_time)},Default,,0,0,0,,{text}"
        )
    pathlib.Path(target).write_text("\n".join(head + events) + "\n", encoding="utf-8")
    if not events:
        raise RuntimeError(f"Tidak ada cue subtitle: {vtt}")
    print(f"SUBTITLE_CUES={len(events)}; max_words=6; source_fallback={str(use_source_fallback).lower()}")
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
        delivery = scene.get("delivery", "natural")
        delivery_rates = {"natural": "+0%", "paced": "-3%", "suspense": "-5%", "reflective": "-4%", "urgent": "+0%"}
        rate = scene.get("tts_rate", delivery_rates.get(delivery, "+0%"))
        tts_with_delivery(
            scene["text"], audio, vtt, voice,
            rate=rate,
            pitch=scene.get("tts_pitch", "+0Hz"),
            volume=scene.get("tts_volume", "+0%"),
            delivery=delivery,
            dramatic_pause_after=scene.get("dramatic_pause_after", []),
        )
        length=duration(audio)+0.45
        print(f"TTS_DIRECTION={speaker}; delivery={delivery}; rate={rate}; pitch={scene.get('tts_pitch', '+0Hz')}")
        src=ASSETS/f"peta-sunyi-{scene['shot']}.jpg"
        if not src.exists(): raise FileNotFoundError(f"Aset visual tidak ditemukan: {src}")
        if style=="rough_pencil":
            styled=OUT/f"long-{i:02d}-pencil.jpg"; pencil(src,styled); src=styled
        ass=subtitles(vtt,OUT/f"long-{i:02d}.ass",speaker,scene["text"],duration(audio))
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
        overlay=OUT/f"long-{i:02d}-motion.gif"
        create_overlay(overlay, length, motion=scene.get("motion_profile", "atmosphere"),
                       graphic=scene.get("graphic"), seed=i * 97)
        cmd=["ffmpeg","-y","-loop","1","-i",str(src),"-i",str(audio)]
        audio_filters=["[1:a]volume=1.0[voice]"]
        mix_labels=["[voice]"]
        input_index=2
        for field,volume in (("ambience_asset",0.18),("music_asset",0.10)):
            asset_name=scene.get(field)
            if asset_name:
                layer=ASSETS/"audio"/asset_name
                if not layer.exists():
                    raise FileNotFoundError(f"Audio layer tidak ditemukan: {layer}")
                cmd += ["-stream_loop","-1","-i",str(layer)]
                label=f"layer{input_index}"
                audio_filters.append(f"[{input_index}:a]volume={volume}[{label}]")
                mix_labels.append(f"[{label}]")
                input_index+=1
        sfx_name=scene.get("sfx_asset")
        if sfx_name:
            layer=ASSETS/"audio"/sfx_name
            if not layer.exists():
                raise FileNotFoundError(f"SFX tidak ditemukan: {layer}")
            cmd += ["-i",str(layer)]
            label=f"layer{input_index}"
            delay=int(scene.get("sfx_delay_ms",900))
            audio_filters.append(f"[{input_index}:a]volume=0.30,adelay={delay}|{delay}[{label}]")
            mix_labels.append(f"[{label}]")
        overlay_index=input_index
        cmd += ["-ignore_loop","1","-i",str(overlay)]
        complex_filters=[]
        if len(mix_labels)>1:
            complex_filters.append("".join(mix_labels)+f"amix=inputs={len(mix_labels)}:duration=first:dropout_transition=2:normalize=0[aout]")
        complex_filters.append(f"[0:v]{vf}[basev]")
        complex_filters.append(f"[{overlay_index}:v]scale={W}:{H}:flags=bicubic[ov]")
        complex_filters.append("[basev][ov]overlay=0:0:format=auto:shortest=1[vout]")
        cmd += ["-filter_complex",";".join(complex_filters),"-map","[vout]"]
        if len(mix_labels)>1:
            cmd += ["-map","[aout]"]
        else:
            cmd += ["-map","1:a:0"]
        cmd += ["-t",f"{length:.3f}","-r",str(FPS),"-c:v","libx264",
                "-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
                "-c:a","aac","-b:a","192k","-shortest",str(clip)]
        run(cmd)
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
