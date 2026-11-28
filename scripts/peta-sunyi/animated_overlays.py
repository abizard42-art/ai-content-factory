#!/usr/bin/env python3
"""Animated scene atmosphere and progressive infographic overlays for Peta Sunyi."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 960, 540, 8
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def _font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

def _gif_frame(rgba, palette=None):
    rgb = rgba.convert("RGB")
    indexed = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT) if palette is None else rgb.quantize(palette=palette, dither=Image.Dither.NONE)
    alpha = rgba.getchannel("A")
    px, ap = indexed.load(), alpha.load()
    for y in range(H):
        for x in range(W):
            if ap[x, y] < 12:
                px[x, y] = 255
    colors = indexed.getpalette() or []
    indexed.putpalette(colors[:765] + [0, 0, 0])
    return indexed

def create_overlay(path, duration, motion="atmosphere", graphic=None, seed=17):
    frames = max(16, min(480, int(math.ceil(max(2.0, duration) * FPS))))
    rng = random.Random(seed)
    particles = [(rng.randrange(W), rng.randrange(H), rng.uniform(0, 6.28), rng.uniform(.5, 1.8)) for _ in range(34)]
    fogs = [(rng.randrange(-W, W), rng.randrange(210, 490), rng.randrange(90, 230), rng.randrange(24, 75), rng.uniform(.15,.45)) for _ in range(5)]
    rendered = []
    palette = None
    for i in range(frames):
        t = i / max(1, frames - 1)
        sec = i / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        hd = ImageDraw.Draw(haze, "RGBA")
        if motion in ("atmosphere", "fog", "rain", "flashlight"):
            for x0, y, rx, ry, speed in fogs:
                x = int((x0 + sec * speed * 42) % (W + rx * 2) - rx)
                hd.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(190, 205, 198, 18))
            haze = haze.filter(ImageFilter.GaussianBlur(34))
            im = Image.alpha_composite(im, haze)
        d = ImageDraw.Draw(im, "RGBA")
        if motion in ("atmosphere", "dust", "flashlight"):
            for j, (x0, y0, phase, speed) in enumerate(particles):
                x = int((x0 + sec * speed * 13) % W)
                y = int((y0 + math.sin(sec * .6 + phase) * 12) % H)
                r = 1 + (j % 3 == 0)
                d.ellipse((x-r, y-r, x+r, y+r), fill=(236, 226, 195, 85))
        if motion == "rain":
            for j in range(42):
                x = (j * 31 + int(sec * 85)) % W
                y = (j * 47 + int(sec * 210)) % H
                d.line((x, y, x-5, y+18), fill=(185, 205, 210, 72), width=1)
        if motion == "flashlight":
            x = int(W * (.12 + .76 * ((math.sin(sec * .55) + 1) / 2)))
            beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bd = ImageDraw.Draw(beam, "RGBA")
            bd.polygon([(x-8, 0), (x+8, 0), (x+145, H), (x-145, H)], fill=(255, 239, 190, 25))
            im = Image.alpha_composite(im, beam.filter(ImageFilter.GaussianBlur(28)))
        if motion == "foliage":
            for j in range(8):
                x = (j * 137 + int(math.sin(sec * .7 + j) * 18)) % W
                y = 60 + j * 53
                d.arc((x-45, y-20, x+45, y+22), 195, 345, fill=(128, 157, 113, 90), width=3)

        if graphic:
            kind = graphic.get("type", "fact")
            x0, y0, gw, gh = 90, 92, 780, 330
            panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            g = ImageDraw.Draw(panel, "RGBA")
            g.rounded_rectangle((x0, y0, x0+gw, y0+gh), radius=22, fill=(12, 27, 31, 218), outline=(219, 198, 151, 225), width=2)
            heading = str(graphic.get("heading", "CATATAN INVESTIGASI"))[:58]
            g.text((x0+28, y0+22), heading, font=_font(24, True), fill=(246, 235, 207, 255))
            g.line((x0+28, y0+66, x0+gw-28, y0+66), fill=(201, 180, 133, 190), width=2)
            items = graphic.get("items", [])
            if kind == "timeline":
                y = y0 + 205
                left, right = x0+65, x0+gw-65
                progress = max(.02, min(1.0, t))
                g.line((left, y, left + int((right-left)*progress), y), fill=(221, 191, 128, 245), width=5)
                for n, item in enumerate(items[:5]):
                    pos = left + int((right-left) * n / max(1, len(items[:5])-1))
                    reveal = min(1, max(0, (t - n*.14) / .18))
                    if reveal > 0:
                        g.ellipse((pos-9, y-9, pos+9, y+9), fill=(236, 211, 159, int(255*reveal)))
                        label = str(item.get("label", item) if isinstance(item, dict) else item)[:22]
                        g.text((pos, y+28), label, font=_font(15, True), fill=(245, 238, 220, int(245*reveal)), anchor="mm")
            elif kind == "map":
                cx, cy = x0+gw//2, y0+210
                pulse = 15 + int(7 * (1 + math.sin(sec*2)))
                for radius in (48, 95, 145):
                    g.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=(125, 176, 165, 125), width=2)
                g.ellipse((cx-pulse, cy-pulse, cx+pulse, cy+pulse), fill=(232, 105, 76, 240))
                g.text((cx, cy+65), str(graphic.get("pin_label", "TITIK LOKASI"))[:32], font=_font(18, True), fill=(255, 239, 213, 255), anchor="mm")
            elif kind == "evidence":
                cols = graphic.get("columns", ["TERCATAT", "BELUM TERVERIFIKASI"])
                for c, label in enumerate(cols[:2]):
                    cx = x0 + 28 + c*365
                    g.rounded_rectangle((cx, y0+92, cx+335, y0+gh-24), radius=12, fill=(37, 62, 61, 220), outline=(132, 155, 139, 190), width=1)
                    g.text((cx+16, y0+108), str(label)[:24], font=_font(17, True), fill=(235, 213, 166, 255))
                for n, item in enumerate(items[:4]):
                    col, row = n % 2, n // 2
                    cx, yy = x0 + 44 + col*365, y0 + 158 + row*62
                    reveal = max(0, min(1, (t - n*.12)/.2))
                    if reveal:
                        txt = str(item.get("text", item) if isinstance(item, dict) else item)[:34]
                        g.text((cx, yy), "• " + txt, font=_font(14), fill=(245, 241, 226, int(255*reveal)))
            else:
                for n, item in enumerate(items[:4]):
                    reveal = max(0, min(1, (t - n*.16)/.22))
                    if reveal:
                        txt = str(item.get("text", item) if isinstance(item, dict) else item)[:66]
                        yy = y0 + 102 + n*48
                        g.rounded_rectangle((x0+34, yy, x0+gw-34, yy+35), radius=8, fill=(42, 68, 66, int(225*reveal)))
                        g.text((x0+52, yy+7), txt, font=_font(16, True), fill=(249, 243, 226, int(255*reveal)))
            im = Image.alpha_composite(im, panel)
        indexed = _gif_frame(im, palette)
        if palette is None:
            palette = indexed
        rendered.append(indexed)
    rendered[0].save(path, save_all=True, append_images=rendered[1:], duration=int(1000/FPS), loop=0, transparency=255, disposal=2, optimize=True)
    print(f"ANIMATED_OVERLAY_OK={path}; frames={frames}; motion={motion}; graphic={graphic.get('type') if graphic else 'none'}")
