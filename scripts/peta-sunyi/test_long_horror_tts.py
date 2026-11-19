#!/usr/bin/env python3
"""Create matched Indonesian TTS audition samples for Peta Sunyi."""
import asyncio
import json
import pathlib
import re
import edge_tts
from pydub import AudioSegment

OUT = pathlib.Path("output/tts-audition")
TMP = OUT / "segments"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
TEXT = (
    "Awalnya, tidak ada yang terasa aneh malam itu. Angin bergerak pelan di antara "
    "pepohonan, sementara kami mulai membereskan barang-barang di sekitar tenda. "
    "Tapi beberapa menit kemudian, terdengar sesuatu dari arah hutan. Bukan suara "
    "ranting patah. Bukan pula langkah orang yang sedang berjalan. Suaranya pelan, "
    "teratur, dan semakin dekat. Saat itu, tidak seorang pun dari kami berani menoleh."
)

async def synthesize(text, voice, rate, path):
    await edge_tts.Communicate(text, voice, rate=rate).save(str(path))

async def make_paced_sample(label, voice, rate):
    # Split only at existing punctuation; words and wording remain identical.
    phrases = re.findall(r"[^,;.!?]+[,;.!?]?", TEXT)
    combined = AudioSegment.empty()
    for index, phrase in enumerate(phrases):
        phrase = phrase.strip()
        if not phrase:
            continue
        part = TMP / f"{label}-{index:02d}.mp3"
        await synthesize(phrase, voice, rate, part)
        combined += AudioSegment.from_file(part)
        ending = phrase[-1:]
        pause_ms = 320 if ending in ".!?" else 150 if ending in ",;" else 0
        if pause_ms:
            combined += AudioSegment.silent(duration=pause_ms)
    destination = OUT / f"{label}.mp3"
    combined.export(destination, format="mp3", bitrate="192k")
    return destination

async def main():
    voices = await edge_tts.list_voices()
    male = [v for v in voices if v.get("Locale") == "id-ID" and v.get("Gender") == "Male"]
    male.sort(key=lambda v: (v.get("ShortName") != "id-ID-ArdiNeural", v.get("ShortName", "")))
    if not male:
        raise RuntimeError("Tidak ditemukan suara laki-laki id-ID dari daftar Edge TTS.")
    selected = male[:2]
    manifest = {"text": TEXT, "samples": [], "available_indonesian_male_voices": [v.get("ShortName") for v in male]}
    for index, voice in enumerate(selected):
        name = voice["ShortName"]
        if name == "id-ID-ArdiNeural":
            default_label, paced_label = "A_ardi_default", "B_ardi_paced"
        else:
            default_label, paced_label = f"C_{index+1}_alternative_default", f"D_{index+1}_alternative_paced"
        default_path = OUT / f"{default_label}.mp3"
        await synthesize(TEXT, name, "+0%", default_path)
        manifest["samples"].append({"file": default_path.name, "voice": name, "rate": "+0%", "delivery": "provider_default"})
        print(f"TTS_SAMPLE_OK={default_path}; voice={name}; delivery=default")
        paced_path = await make_paced_sample(paced_label, name, "-3%")
        manifest["samples"].append({"file": paced_path.name, "voice": name, "rate": "-3%", "delivery": "punctuation_pauses_150_320ms"})
        print(f"TTS_SAMPLE_OK={paced_path}; voice={name}; delivery=paced")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TTS_AUDITION_OK={len(manifest['samples'])} samples; male_voices_tested={len(selected)}")

if __name__ == "__main__":
    asyncio.run(main())
