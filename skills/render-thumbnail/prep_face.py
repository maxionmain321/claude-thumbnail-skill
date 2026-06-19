# -*- coding: utf-8 -*-
"""
prep_face.py — full face asset pipeline for the HTML compositor.

  raw rembg cut-out  ->  autocrop (head+shoulders)  ->  polish (clean alpha + grade)
  ->  cinematic (pro look)  ->  add_outline (bake white stroke + glow + shadow)
  ->  ready-to-place transparent PNG.

The HTML engine just positions this finished PNG. All the face quality lives here.

    python prep_face.py <rembg_cutout.png> <out.png> [outline_width]
"""
import os
import sys
from face_autocrop import autocrop
from face_polish import polish, cinematic, add_outline


def prep_face(src, out, outline_width=12, outline_color=(255, 255, 255)):
    tmp = out + ".crop.png"
    autocrop(src, tmp)
    cut = polish(tmp)            # harden alpha + base grade (returns tight RGBA)
    cut = cinematic(cut)         # soft-skin + bloom + teal-orange grade
    cut = add_outline(cut, width=outline_width, color=outline_color)
    cut.save(out)
    try:
        os.remove(tmp)
    except OSError:
        pass
    print(f"prep_face -> {out} {cut.size}")
    return out


if __name__ == "__main__":
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    prep_face(sys.argv[1], sys.argv[2], outline_width=w)
