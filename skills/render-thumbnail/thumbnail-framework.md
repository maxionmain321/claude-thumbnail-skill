# Thumbnail Framework (follow this each time — do NOT template)

The goal is a **repeatable decision process** that produces *varied* thumbnails sharing one
brand DNA — not a fixed layout you re-skin. Lock the concept on paper BEFORE you touch
pixels. Most thumbnail spirals come from rendering before the concept is locked.

Two first principles the whole framework rests on: (1) the face is always *big*, (2) the
background is never one flat tone — a base tone plus "other stuff" with depth.

---

## STEP 1 — Concept brief (4 lines, before any rendering)

- **Hook** — the one curiosity gap that earns the click.
- **Emotion** — win / shock / fear / greed / intrigue. Drives the face AND the accent color.
- **Proof** — the ONE real artifact that makes it believable (dashboard, tweet, number, logo).
- **Title** — the complementary line. Opens a *different* loop than the thumbnail. NEVER repeats it.

If you can read the (thumbnail + title) and there's no unanswered question left, the concept
failed. Redo the brief.

## STEP 1.5 — Generate + pick the text/title combo (before any pixels)

The thumbnail-text × title pairing is the click. Lock it BEFORE rendering:
1. Generate 3–5 candidate combos (each = on-image thumbnail text + the paired title that
   opens a *different* loop).
2. Score each on: curiosity gap, complementarity (thumb vs title), specificity, scroll-stop,
   clarity at a glance.
3. Keep iterating until one is clearly the best — don't proceed to rendering on a merely-good
   combo. A rubric is a guide; your gut is the gate.

## STEP 1.6 — Gather REAL assets first

Before generating anything, list what real assets exist for this video — they beat anything
synthetic and they ARE the "proof":
- dashboards / screenshots (the actual numbers)
- tool/app logos (drop them in `assets/logos/` you create)
- real tweet / inbox / app screenshots
- specific photos you want in-frame

Only fall back to AI generation (Mode C) when no real asset fits the hook. Reference local
images as `{type:"image"}` elements (see schema).

## STEP 2 — Canon (always true; the spine that keeps it on-brand)

- **Face huge** — ~50–65% of frame, head near the top edge, eye contact, expression = the emotion.
- **One real proof element.** Real > fabricated.
- **Brutal contrast**; must pass the 120px mobile test (read in <1s).
- **Depth** — subject separated from bg (baked white outline + glow + shadow); background never flat.
- **Thumbnail + title complement**, never repeat. **≤4 words** of big text.

## STEP 3 — Variable (choose fresh per video — this is what prevents a template)

- Face: which photo/expression, which side (L/R).
- **Accent color** from the emotion: win→yellow, problem/danger→red, fix/money→green, neutral/tech→cyan.
- **Background MODE** (pick ONE, never "flat") — see below.
- Proof form: full-bleed scene · framed card · floating element · highlight number.
- Text treatment: highlight boxes · gradient · plain · none.

## STEP 4 — Background model (the #2 upgrade; pick ONE mode)

- **A. Artifact scene** — a real screenshot/dashboard enlarged + darkened as the *environment*
  (`bg.type:image`, darken ~0.5, blur ~3, scrim toward the text side).
- **B. Element cluster** — floating relevant logos/icons (an `assets/logos/` folder you add)
  with depth blur, via `elements:[…]`.
- **C. Themed image** — an AI scene from `gen_background.py` (cash room, server room, inbox).
  Backgrounds ONLY; the face is always the real cut-out. (~$0.016/img on `low`.)
- **D. Color-block split** — two `elements:[{type:rect}]` zones for before/after or contrast hooks.
- **E. Clean spotlight** — rich radial gradient + vignette (used when the proof is a card).

Rotate modes across consecutive uploads so the channel page looks varied, not factory-made.

**Background editing WITH REASONING (don't default — decide).** The background is never
decoration; it must *cue the topic and carry the emotion* (money video → cash scene;
deliverability → spam folder; tools → logo cluster). Before rendering, state in one line
*why* this background reinforces the hook. Then treat it as **editable**: for Mode C, refine
the `gen_background.py` prompt and regenerate until the scene actually says the topic; for
Mode A, re-crop the real screenshot; adjust `darken`/`blur`/`scrim` so the subject + text
stay readable on top. If you can't say why the background fits, it's wrong — change it.

## STEP 5 — Gates (before ship)

1. **120px test** — the `.m120.png`; text + face read instantly.
2. **Swipe spot-check** — open it next to a folder of thumbnails you admire; what's weaker? Fix that.
3. **T+T complement** — thumbnail + title leave an open question.
4. **Brand-consistent but distinct** — recognizably your channel, different from the last 3.

---

## The pipeline (tools)

```
# 1. cut the face out (rembg)
python -c "from rembg import remove,new_session;import io;from PIL import Image;\
open('cut.png','wb').write(remove(open('photo.jpg','rb').read(),session=new_session('u2net'),alpha_matting=True))"
# 2. face -> ready-to-place portrait (autocrop + cinematic grade + baked outline)
python prep_face.py cut.png faces/v1_face.png 14
# 3. (optional) AI themed background — Mode C  (needs OPENAI_API_KEY)
python gen_background.py "stacks of cash in a dark office, blue/red light" bg.png low
# 4. author <video>.json (schema below) and render
python render_html.py <video>.json     # -> <output>.png + <output>.m120.png
```

### Config schema (`render_html.py` / `html_template.html`)

```jsonc
{
  "output": "...png", "width": 1280, "height": 720,
  "bg": { "type": "gradient|image|color", "value": "<css gradient | image path | color>",
          "darken": 0.5, "blur": 3, "scrim": "<css gradient overlay>" },
  "elements": [ // Mode B/D: logos, artifacts, color zones
     {"type":"image","src":"...","x":0,"y":0,"w":200,"h":200,"opacity":1,"blur":0,"rotate":0,"blend":"normal","radius":0,"shadow":true},
     {"type":"rect","x":0,"y":0,"w":640,"h":720,"color":"#E11D2A","opacity":0.9} ],
  "face": { "src": "faces/x.png", "side": "right|left", "h": 820, "dx": -10, "dy": 0 },
  "texts": [
     {"kind":"highlight","lines":["12,000","DEAD LEADS"],"x":44,"y":34,"size":94,"lineh":106,"gap":10,
      "box":"#E11D2A","color":"#fff","font":"arialblack",
      "subtitle":{"t":"YOU'RE STILL PAYING","size":46,"color":"#fff","gap":16,"stroke":1,"strokeColor":"#06101f"}},
     {"kind":"gradient","lines":["90+ CUSTOMERS"],"x":44,"y":40,"size":120,"gradient":["#FFF3A6","#FFC400"],"stroke":3,"strokeColor":"#000"},
     {"kind":"plain","lines":["..."],"x":44,"y":40,"size":80,"color":"#fff","stroke":8,"strokeColor":"#000"},
     {"kind":"card","lines":[{"t":"WHOLE PLAYBOOK","color":"#E11D2A","size":74}],"x":40,"y":402,"w":560,"fill":"#fff","radius":28,"pad":30,"font":"arialblack"},
     {"kind":"pill","t":"FIXED IT LIVE","x":44,"y":520,"fill":"#10B981","color":"#04261a","size":50,"font":"arialblack"} ],
  "vignette": true
}
```
Fonts: `anton` · `montserrat` · `arialblack`. Card text auto-fits inside the box. Local image
paths are auto-inlined as data URIs.

## Worked example modes

- **WIN** — Mode E gradient · yellow highlight + white card · excited face.
- **PROBLEM** — Mode C AI scene · red highlight + dark pill · displeased face.
- **FIX** — Mode A real dashboard environment · red→green two-color highlight · shocked face.

Keep each video's `<video>.json` config next to its output so you can tweak and re-render.

## Reuse beyond YouTube

The HTML engine is a generic layered canvas — change `width`/`height` for **X-post cards**
(1200×675) or **video frames** (1920×1080). One input, many outputs.
