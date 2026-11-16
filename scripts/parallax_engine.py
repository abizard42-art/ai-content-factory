#!/usr/bin/env python3
"""Create a restrained 2.5D parallax pass from a single scene still.

This is a depth-illusion pass, not object/character animation. Three broad,
feathered image planes drift at different speeds to add subtle camera depth.
"""
import argparse
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--duration", type=float, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

os.makedirs(args.out, exist_ok=True)
W, H = 720, 1280
fps = 12
frames = max(1, int(math.ceil(args.duration * fps)))

with Image.open(args.input) as source:
    image = ImageOps.fit(source.convert("RGB"), (W, H), method=Image.Resampling.LANCZOS)

# Broad approximate depth zones: distant upper scene, middle scene, foreground.
# Feathered boundaries avoid obvious horizontal seams. Movement stays deliberately
# tiny because a single still cannot provide the hidden pixels behind moving objects.
zones = [
    (0, int(H * 0.43), 1.4, 0.20, 0.0),
    (int(H * 0.28), int(H * 0.78), 3.0, 0.15, 1.7),
    (int(H * 0.64), H, 5.0, 0.11, 3.1),
]
pad = 10
padded = ImageOps.expand(image, border=(pad, 0, pad, 0), fill=None)
for frame in range(frames):
    seconds = frame / fps
    result = image.copy()
    for top, bottom, amplitude, speed, phase in zones:
        dx = int(round(math.sin(seconds * speed + phase) * amplitude))
        # Crop from padded source so edges never wrap around.
        shifted = padded.crop((pad + dx, 0, pad + dx + W, H))
        mask = Image.new("L", (W, H), 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle((0, top, W, bottom), fill=190)
        mask = mask.filter(ImageFilter.GaussianBlur(34))
        result.paste(shifted, (0, 0), mask)
    result.save(os.path.join(args.out, f"{frame:05d}.png"), optimize=True)

print(f"Parallax: 3 feathered depth planes; frames: {frames}; source: {args.input}")
