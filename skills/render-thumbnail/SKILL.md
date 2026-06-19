---
name: render-thumbnail
description: Produce a high-converting YouTube thumbnail (1280x720) via a FRAMEWORK (not a template) — concept brief → big cinematic face + real proof + non-flat background → HTML/CSS + Playwright render. rembg cut-outs, cinematic face grade, and optional AI backgrounds. Use when the user says "render thumbnail", "make the thumbnail", "thumbnail PNG", or has picked a thumbnail concept to render. Start at thumbnail-framework.md. Also reusable for X-post cards and video frames.
---

# render-thumbnail

Turns a thumbnail **concept** into an actual **1280x720 PNG**.

**START HERE: `thumbnail-framework.md`.** It is a *framework, not a template* — a decision
process (concept brief → canon → variable → background mode → gates) that produces VARIED
thumbnails sharing one brand DNA. Lock the concept on paper BEFORE rendering; every spiral
comes from rendering first.

**Engine: `render_html.py` + `html_template.html`** (HTML/CSS + Playwright, zero cost for
the composite). Layered config: background (gradient / real-artifact / AI scene / color
zones) + big cinematic face + highlight/gradient/plain/card/pill text + vignette.

Supporting tools:
- `prep_face.py` — raw rembg cut-out → autocrop (big head+shoulders) → cinematic grade →
  baked white outline. The face quality lives here; run it once per chosen photo.
- `face_autocrop.py` — OpenCV face-detect → reliable big-face crop (the geometry fix).
- `face_polish.py` — `polish` / `cinematic` / `add_outline` (reused by `prep_face`).
- `gen_background.py` — optional AI themed scenes for Background-mode C (backgrounds ONLY,
  never the face). Needs `OPENAI_API_KEY`. ~$0.016–0.06/image; surfaces cost.

## Workflow

1. **Read `thumbnail-framework.md`** and fill the 4-line concept brief (hook / emotion / proof / title). Do NOT render before this is locked.
2. **Prep the face:** rembg cut-out → `python prep_face.py cut.png faces/<v>.png 14`.
3. **Pick a background MODE** (A artifact · B logos · C AI scene · D color-split · E gradient). For C: `python gen_background.py "<scene>" bg.png low`.
4. **Author `<video>.json`** (schema in the framework doc) and render:
   ```
   python render_html.py <video>.json
   ```
   (pass multiple JSON files to batch).
5. **Run the gates** (framework §5): `<out>.m120.png` 120px test · spot-check vs thumbnails you admire · thumbnail+title complement · brand-consistent-but-distinct-from-last-3.
6. **Give the full path** — auto-open is unreliable across platforms; print the path, don't claim "opened".

## Reuse beyond YouTube

The HTML engine is a generic layered canvas — change `width`/`height` for **X-post cards**
(1200×675) or **video frames** (1920×1080). One input, many outputs.

## Deps

`playwright` (chromium) + `Pillow` + `rembg` + `opencv-python`, plus `openai` only if you use
AI backgrounds (Mode C). Install:
```
pip install playwright pillow rembg opencv-python openai && playwright install chromium
```
