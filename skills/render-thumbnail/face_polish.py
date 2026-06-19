# -*- coding: utf-8 -*-
"""
face_polish.py — turn a rough background-removed face PNG into the polished
"highly edited" thumbnail cut-out the big channels use.

This is NOT AI generation (that would change the face). It's deterministic
compositing polish: clean the alpha, despill the fringe, punch color/contrast,
add a white outline stroke + soft shadow. Keeps the real face.

    polish(src_png) -> RGBA cut-out (tight bbox), ready to composite.
    add_outline(cutout, width, color) -> RGBA with stroke + shadow baked, padded.

CLI (quick preview on a dark card):
    python face_polish.py <face.png> [out.png]
"""
import sys
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops


def polish(src, brightness=1.06, contrast=1.12, color=1.22, sharpness=1.5):
    im = Image.open(src).convert("RGBA")
    bbox = im.split()[-1].getbbox()
    if bbox:
        im = im.crop(bbox)
    r, g, b, a = im.split()
    # de-jag the matte: harden, median-filter the staircase edges, erode the
    # chroma fringe, then a soft feather so the cut-out edge reads clean not pixelated
    a = a.point(lambda v: 0 if v < 70 else 255)
    a = a.filter(ImageFilter.MedianFilter(5))   # kills jagged hair staircase
    a = a.filter(ImageFilter.MinFilter(3))       # erode fringe
    a = a.filter(ImageFilter.GaussianBlur(1.4))  # soft anti-aliased edge
    rgb = Image.merge("RGB", (r, g, b))
    # clarity: unsharp mask adds perceived detail to soft webcam frames
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=3, percent=110, threshold=2))
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Color(rgb).enhance(color)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    out = Image.merge("RGBA", (*rgb.split(), a))
    bbox2 = out.split()[-1].getbbox()
    return out.crop(bbox2) if bbox2 else out


def cinematic(im):
    """Pro-grade face look: soft-skin retouch + highlight bloom + teal-orange grade.
    Approximates the lit/retouched faces on top thumbnails (no AI model needed)."""
    import numpy as np
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b))
    # soft skin: blend a slight blur back, then restore micro-detail so it isn't plastic
    smooth = rgb.filter(ImageFilter.GaussianBlur(2.4))
    rgb = Image.blend(rgb, smooth, 0.34)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=95, threshold=3))
    arr = np.asarray(rgb).astype(float)
    lum = arr.mean(2)
    # bloom: glow the highlights
    mask = np.clip((lum - 178) / 77, 0, 1)[..., None]
    bloom = Image.fromarray((arr * mask).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(12))
    arr = arr + np.asarray(bloom).astype(float) * 0.5
    # teal-orange grade: warm highlights, cool shadows
    hl = np.clip((lum - 120) / 135, 0, 1)
    arr[..., 0] += 14 * hl
    arr[..., 2] -= 9 * hl
    arr[..., 2] += 8 * (1 - hl)
    rgb = Image.fromarray(arr.clip(0, 255).astype("uint8"))
    rgb = ImageEnhance.Contrast(rgb).enhance(1.1)
    rgb = ImageEnhance.Color(rgb).enhance(1.12)
    return Image.merge("RGBA", (*rgb.split(), a))


def add_outline(cutout, width=10, color=(255, 255, 255),
                shadow=True, shadow_radius=22, shadow_opacity=150, shadow_off=(0, 10)):
    """Return a padded RGBA with white stroke + drop shadow behind the cut-out."""
    pad = width + shadow_radius + max(abs(shadow_off[0]), abs(shadow_off[1])) + 8
    W, H = cutout.size
    canvas = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    a = cutout.split()[-1]

    # drop shadow
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sil = Image.new("RGBA", (W, H), (0, 0, 0, shadow_opacity))
        sh.paste(sil, (pad + shadow_off[0], pad + shadow_off[1]), a)
        sh = sh.filter(ImageFilter.GaussianBlur(shadow_radius))
        canvas = Image.alpha_composite(canvas, sh)

    # soft outer glow (a blurred white halo beyond the stroke = "designed" pop)
    glow_dil = a
    for _ in range(width + 14):
        glow_dil = glow_dil.filter(ImageFilter.MaxFilter(3))
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    glow.paste(Image.new("RGBA", (W, H), color + (200,)), (pad, pad), glow_dil)
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    canvas = Image.alpha_composite(canvas, glow)

    # white outline: dilate alpha, fill with color, slight feather so it isn't jagged
    dil = a
    for _ in range(width):
        dil = dil.filter(ImageFilter.MaxFilter(3))
    dil = dil.filter(ImageFilter.GaussianBlur(1.0))
    stroke = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    fill = Image.new("RGBA", (W, H), color + (255,))
    stroke.paste(fill, (pad, pad), dil)
    canvas = Image.alpha_composite(canvas, stroke)

    # the face on top
    top = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    top.paste(cutout, (pad, pad), cutout)
    canvas = Image.alpha_composite(canvas, top)
    bbox = canvas.split()[-1].getbbox()
    return canvas.crop(bbox) if bbox else canvas


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "face_polish_preview.png"
    cut = polish(src)
    cut = add_outline(cut, width=10)
    card = Image.new("RGBA", (cut.width + 120, cut.height + 120), (16, 20, 34, 255))
    card.alpha_composite(cut, (60, 60))
    card.convert("RGB").save(out)
    print("wrote", out, cut.size)
