# -*- coding: utf-8 -*-
"""
render_html.py — HTML/CSS + Playwright thumbnail compositor.

Config-driven layered renderer (see thumbnail-framework.md for the schema + modes).
Local image/font paths are inlined as base64 data URIs so the file:// page can load them.

    python render_html.py <config.json> [config2.json ...]

Outputs <output>.png (1280x720) + <output>.m120.png (the 120px mobile gate).
"""
import base64
import json
import os
import sys
from playwright.sync_api import sync_playwright
from PIL import Image

SKILL = os.path.dirname(os.path.abspath(__file__))


def data_uri(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp", "svg": "image/svg+xml", "ttf": "font/ttf"}.get(ext, "application/octet-stream")
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def inline_images(cfg):
    """Replace any local file path in the config with a data URI."""
    def fix(v):
        if isinstance(v, str) and os.path.exists(v) and v.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")):
            return data_uri(v)
        return v
    if cfg.get("bg", {}).get("type") == "image":
        cfg["bg"]["value"] = fix(cfg["bg"]["value"])
    for e in cfg.get("elements", []):
        if e.get("src"):
            e["src"] = fix(e["src"])
    if cfg.get("face", {}).get("src"):
        cfg["face"]["src"] = fix(cfg["face"]["src"])
    return cfg


def font_css():
    css = []
    for fam, fn in [("Anton", "Anton-Regular.ttf"), ("Montserrat", "Montserrat-ExtraBold.ttf")]:
        p = os.path.join(SKILL, "assets", fn)
        if os.path.exists(p):
            css.append(f"@font-face{{font-family:'{fam}';src:url('{data_uri(p)}') format('truetype');font-weight:normal;}}")
    return "\n".join(css)


def render(cfg_path):
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    out = cfg["output"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cfg = inline_images(cfg)
    fcss = font_css()
    W, H = cfg.get("width", 1280), cfg.get("height", 720)
    tpl = "file:///" + os.path.join(SKILL, "html_template.html").replace("\\", "/")

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        pg.goto(tpl)
        pg.evaluate("([cfg, fcss]) => window.render(cfg, fcss)", [cfg, fcss])
        pg.wait_for_function("window.__rendered === true", timeout=5000)
        pg.wait_for_timeout(400)  # let fonts + images paint
        pg.locator("#stage").screenshot(path=out)
        b.close()

    im = Image.open(out).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H))
        im.save(out)
    im.resize((228, 128)).save(out.rsplit(".", 1)[0] + ".m120.png")
    print("wrote", out)


if __name__ == "__main__":
    for c in sys.argv[1:]:
        render(c)
