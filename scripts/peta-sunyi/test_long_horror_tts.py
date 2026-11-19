#!/usr/bin/env python3
"""Create matched Indonesian TTS audition samples for Peta Sunyi."""
import asyncio
import json
import pathlib
import re
import edge_tts

OUT = pathlib.Path("output/tts-audition")
OUT.mkdir(parents=True, exist_ok=True)
TEXT = (
    "Awalnya, tidak ada yang terasa aneh malam itu. Angin bergerak pelan di antara "
    "pepohonan, sementara kami mulai membereskan barang-barang di sekitar tenda. "
    "Tapi beberapa menit kemudian, terdengar sesuatu dari arah hutan. Bukan suara "
    "ranting patah. Bukan pula langkah orang yang sedang berjalan. Suaranya pelan, "
    "teratur, dan semakin dekat. Saat itu, tidak seorang pun dari kami berani menoleh."
)

async def main():
    voices = await edge_tts.list_voices()
    male = [v for v in voices if v.get("Locale") == "id-ID" and v.get("Gender") == "Male"]
    male.sort(key=lambda v: (v.get("ShortName") != "id-ID-ArdiNeural", v.get("ShortName", "")))
    if not male:
        raise RuntimeError("Tidak ditemukan suara laki-laki id-ID dari daftar Edge TTS.")
    selected = male[:2]
    manifest = {"text": TEXT, "samples": [], "available_indonesian_male_voices": [v.get("ShortName") for v in male]}
    variants = []
    for index, voice in enumerate(selected):
        name = voice["ShortName"]
        label = "A_ardi_default" if name == "id-ID-ArdiNeural" else f"C_{index+1}_alternative_default"
        variants.append((label, name, "+0%"))
        label_slow = "B_ardi_paced" if name == "id-ID-ArdiNeural" else f"D_{index+1}_alternative_paced"
        variants.append((label_slow, name, "-5%"))
    for label, voice, rate in variants:
        path = OUT / f"{label}.mp3"
        communicate = edge_tts.Communicate(TEXT, voice, rate=rate)
        await communicate.save(str(path))
        manifest["samples"].append({"file": path.name, "voice": voice, "rate": rate, "text_identical": True})
        print(f"TTS_SAMPLE_OK={path}; voice={voice}; rate={rate}")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TTS_AUDITION_OK={len(variants)} samples; voices={len(selected)}")

if __name__ == "__main__":
    asyncio.run(main())
