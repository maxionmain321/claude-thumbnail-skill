# -*- coding: utf-8 -*-
"""
gen_background.py — AI themed-scene backgrounds via OpenAI gpt-image-1.

BACKGROUNDS ONLY. The face is always the real cut-out (never AI-generated). Use for
Background-model Mode C (themed scene: cash room, server room, inbox, etc.).

    python gen_background.py "money raining in a dark office, green tones" out.png [quality]
    # quality: low (~$0.01) | medium (~$0.06, default) | high

Builds a thumbnail-friendly prompt (no text, no people, room for a subject), generates
1536x1024, crops to 1280x720. Prints estimated cost.
"""
import base64
import os
import sys

COST = {"low": 0.016, "medium": 0.063, "high": 0.25}  # ~1536x1024 per OpenAI pricing


def load_key():
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    raise RuntimeError("Set OPENAI_API_KEY in your environment to use AI backgrounds (Mode C).")


def build_prompt(scene, subject_side="right", tones="cinematic"):
    return (
        f"Professional YouTube thumbnail BACKGROUND. Scene: {scene}. "
        f"Dramatic studio lighting, strong depth of field, blurred bokeh, high contrast, "
        f"{tones} color grade, glossy and premium. Leave the {subject_side} side emptier "
        f"so a person can be composited there. ABSOLUTELY NO text, NO words, NO letters, "
        f"NO people, NO faces, NO logos. Clean cinematic backdrop only."
    )


def generate(scene, out, quality="medium", subject_side="right", tones="cinematic"):
    from openai import OpenAI
    client = OpenAI(api_key=load_key())
    prompt = build_prompt(scene, subject_side, tones)
    print(f"[gen_bg] generating ({quality}) ~${COST.get(quality, 0.06):.3f} ... ")
    r = client.images.generate(model="gpt-image-1", prompt=prompt,
                               size="1536x1024", quality=quality, n=1)
    raw = base64.b64decode(r.data[0].b64_json)
    tmp = out + ".raw.png"
    with open(tmp, "wb") as f:
        f.write(raw)
    from PIL import Image
    im = Image.open(tmp).convert("RGB")
    # crop 1536x1024 -> 1280x720 (cover)
    scale = max(1280 / im.width, 720 / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)))
    left = (im.width - 1280) // 2
    top = (im.height - 720) // 2
    im.crop((left, top, left + 1280, top + 720)).save(out)
    os.remove(tmp)
    print(f"[gen_bg] wrote {out}  (est ${COST.get(quality, 0.06):.3f})")
    return out


if __name__ == "__main__":
    scene = sys.argv[1]
    out = sys.argv[2]
    q = sys.argv[3] if len(sys.argv) > 3 else "medium"
    generate(scene, out, q)
