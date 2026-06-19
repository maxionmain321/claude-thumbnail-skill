# -*- coding: utf-8 -*-
"""
face_autocrop.py — detect the face and crop a consistent head+shoulders portrait,
so "big face" framing is reliable every time (the geometry we kept fighting).

Primary: OpenCV Haar face detection. Fallback: alpha-bbox head heuristic (top of the
cut-out) if no face is found. Input should be an RGBA cut-out (rembg output); output is
a tight head+shoulders RGBA portrait ready for the HTML compositor.

    python face_autocrop.py <cutout.png> <portrait_out.png>
    # or: from face_autocrop import autocrop; autocrop(src, out)
"""
import sys
import numpy as np
from PIL import Image


def _detect_face(rgb):
    try:
        import cv2
    except Exception:
        return None
    arr = np.asarray(rgb)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    cc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cc.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                minSize=(int(rgb.width * 0.08), int(rgb.height * 0.08)))
    if len(faces) == 0:
        return None
    # largest detected face
    return max(faces, key=lambda f: f[2] * f[3])


def autocrop(src, out, above=0.78, below=1.65, side=0.98):
    """Frame a tight head+shoulders portrait, sized relative to the detected FACE height
    (so it works whether the selfie is close or far). above/below = xFaceHeight from the
    face-box top; side = xFaceHeight each side of the face center."""
    im = Image.open(src).convert("RGBA")
    abox = im.split()[-1].getbbox() or (0, 0, im.width, im.height)
    # detect on the cut-out composited over mid-gray (so alpha edges don't confuse Haar)
    bg = Image.new("RGB", im.size, (128, 128, 128))
    bg.paste(im, (0, 0), im)
    face = _detect_face(bg)

    if face is not None:
        fx, fy, fw, fh = [int(v) for v in face]
        cx = fx + fw / 2
        top = int(fy - above * fh)
        bottom = int(fy + below * fh)
        half = int(side * fh)
        left, right = int(cx - half), int(cx + half)
    else:  # fallback: head is the top of the alpha bbox
        x0, y0, x1, y1 = abox
        h = y1 - y0
        top, bottom = y0, y0 + int(h * 0.78)
        cx = (x0 + x1) / 2
        half = int((x1 - x0) * 0.42)
        left, right = int(cx - half), int(cx + half)

    # clamp to image AND to where there's actually content (alpha bbox)
    left = max(left, 0, abox[0] - 10)
    right = min(right, im.width, abox[2] + 10)
    top = max(top, 0, abox[1] - 10)
    bottom = min(bottom, im.height)

    portrait = im.crop((left, top, right, bottom))
    portrait.save(out)
    print(f"autocrop: face={'yes' if face is not None else 'fallback'} "
          f"crop=({left},{top},{right},{bottom}) -> {out} {portrait.size}")
    return out


if __name__ == "__main__":
    autocrop(sys.argv[1], sys.argv[2])
