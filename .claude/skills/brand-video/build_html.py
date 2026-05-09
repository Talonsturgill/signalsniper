#!/usr/bin/env python3
"""
brand-video HTML builder.

Reads a brand-video spec and emits a single self-contained HTML file
with fonts base64-embedded, layout driven by the spec's design tokens,
and an animated timeline of variable-duration scenes.

Usage:
    python build_html.py <spec.json> <output.html>
"""

import argparse
import base64
import json
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).parent
FONTS_DIR = SKILL_DIR / "fonts"

VIEWPORT = 1080

# ---- font registry ----
FONT_FILES = {
    "Inter":              ("Inter.ttf",              True),   # (filename, variable?)
    "JetBrainsMono":      ("JetBrainsMono.ttf",      True),
    "IBMPlexSerif":       ("IBMPlexSerif-Regular.ttf", False),
    "IBMPlexSerif-Bold":  ("IBMPlexSerif-Bold.ttf",   False),
    "EBGaramond":         ("EBGaramond.ttf",         True),
    "SpaceGrotesk":       ("SpaceGrotesk.ttf",       True),
    "BricolageGrotesque": ("BricolageGrotesque.ttf", True),
    "Fraunces":           ("Fraunces.ttf",           True),
}

# ---- motion presets ----
MOTION_PRESETS = {
    "fade":  {"in_s": 0.40, "out_s": 0.27, "y_px": 14, "stagger_s": 0.27, "scale_from": 1.00},
    "cut":   {"in_s": 0.05, "out_s": 0.05, "y_px":  0, "stagger_s": 0.10, "scale_from": 1.00},
    "scale": {"in_s": 0.45, "out_s": 0.27, "y_px":  0, "stagger_s": 0.30, "scale_from": 0.92},
}


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def load_font_b64(name):
    if name not in FONT_FILES:
        raise SystemExit(f"Unknown font key: {name!r}. Known: {', '.join(FONT_FILES)}")
    fname, _variable = FONT_FILES[name]
    path = FONTS_DIR / fname
    if not path.exists():
        raise SystemExit(f"Font file missing: {path}")
    return base64.b64encode(path.read_bytes()).decode("ascii")


def font_face_block(font_keys):
    """font_keys is an iterable of font registry names. Emits one @font-face per."""
    lines = []
    seen = set()
    for key in font_keys:
        if key in seen:
            continue
        seen.add(key)
        b64 = load_font_b64(key)
        lines.append(
            f"@font-face {{\n"
            f"  font-family: '{key}';\n"
            f"  src: url(data:font/ttf;base64,{b64}) format('truetype');\n"
            f"  font-weight: 100 900;\n"
            f"  font-display: block;\n"
            f"}}"
        )
    return "\n".join(lines)


def resolve_fonts(spec):
    """Return (display, body, italic, mono) font keys."""
    fonts = spec["design"].get("fonts", {})
    display = fonts.get("display") or "IBMPlexSerif"
    body = fonts.get("body") or display
    italic = fonts.get("italic") or body
    # mono is fixed for mono_block scenes
    mono = "JetBrainsMono"
    return display, body, italic, mono


def build_css(spec):
    d = spec["design"]
    t = d["tokens"]
    typo = d.get("typography", {})
    motion = d.get("motion", {})
    layout = d.get("layout", {})

    display, body, italic, mono = resolve_fonts(spec)
    all_fonts = {display, body, italic, mono}
    fonts_css = font_face_block(all_fonts)

    register = motion.get("register", "fade")
    preset = MOTION_PRESETS.get(register, MOTION_PRESETS["fade"])
    in_s = motion.get("scene_in_s", preset["in_s"])
    out_s = motion.get("scene_out_s", preset["out_s"])

    display_weight = typo.get("display_weight", 700)
    body_weight = typo.get("body_weight", 400)
    letter_spacing = typo.get("letter_spacing_em", -0.02)
    case = typo.get("case", "preserve")
    text_transform = "uppercase" if case == "upper" else ("lowercase" if case == "lower" else "none")
    italic_descriptors = "italic" if typo.get("italic_descriptors", True) else "normal"

    padding_pct = layout.get("padding_pct", 8)
    rule_thickness = layout.get("rule_thickness_px", 2)
    stage_radius = layout.get("stage_radius_px", 12)

    canvas = t["canvas"]
    ink = t["ink"]
    ink_muted = t["ink_muted"]
    accent = t["accent"]
    hairline = t["hairline"]

    return f"""
{fonts_css}

:root {{
  --canvas: {canvas};
  --ink: {ink};
  --ink-muted: {ink_muted};
  --accent: {accent};
  --hairline: {hairline};
  --display: '{display}', serif;
  --body: '{body}', serif;
  --italic: '{italic}', serif;
  --mono: '{mono}', monospace;
  --display-weight: {display_weight};
  --body-weight: {body_weight};
  --tracking: {letter_spacing}em;
  --pad: {padding_pct}%;
  --rule: {rule_thickness}px;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  background: #0d0d0e;
  color: var(--ink);
  font-family: var(--body);
  height: 100%;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}

body {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px;
}}

.stage {{
  position: relative;
  width: min(86vmin, calc(100vh - 100px));
  aspect-ratio: 1 / 1;
  background: var(--canvas);
  overflow: hidden;
  border-radius: {stage_radius}px;
  box-shadow: 0 30px 80px -30px rgba(0,0,0,0.5),
              0 0 0 1px rgba(255,255,255,0.04);
  container-type: inline-size;
  container-name: stage;
}}

.scene {{
  position: absolute;
  inset: 0;
  opacity: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--pad);
}}

.scene > * {{
  font-variation-settings: "wght" var(--display-weight);
  text-transform: {text_transform};
}}

/* ---- shared atoms ---- */
.eyebrow-small {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.6cqw;
  color: var(--ink-muted);
  margin-top: 2.4cqw;
  letter-spacing: 0;
  text-transform: none;
}}

.uc-eyebrow {{
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 2.4cqw;
  letter-spacing: 0.34em;
  color: var(--accent);
  text-transform: uppercase;
}}

.divider-rule {{
  height: var(--rule);
  background: var(--hairline);
  margin: 1.6cqw auto 4.5cqw;
  width: 0;
}}

/* ---- scene: title ---- */
.t-headline {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 11cqw;
  line-height: 1.02;
  letter-spacing: var(--tracking);
  color: var(--ink);
}}

/* ---- scene: stack ---- */
.s-item {{ margin: 1.1cqw 0; }}
.s-name {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 5.7cqw;
  line-height: 1.1;
  color: var(--ink);
  letter-spacing: var(--tracking);
}}
.s-descriptor {{
  font-family: var(--italic);
  font-style: {italic_descriptors};
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.2cqw;
  color: var(--ink-muted);
  margin-top: 0.4cqw;
  text-transform: none;
}}

/* ---- scene: two_line / three_line ---- */
.line {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  line-height: 1.05;
  letter-spacing: var(--tracking);
  color: var(--ink);
  margin: 0.6cqw 0;
}}
.line.size-2 {{ font-size: 8.6cqw; }}
.line.size-3 {{ font-size: 6.4cqw; }}
.line.accent {{ color: var(--accent); }}

/* ---- scene: fix ---- */
.f-primary {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 13cqw;
  line-height: 1;
  letter-spacing: var(--tracking);
  color: var(--ink);
}}
.f-secondary {{
  font-family: var(--italic);
  font-style: italic;
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 5.6cqw;
  color: var(--ink-muted);
  margin-top: 3.6cqw;
  letter-spacing: 0;
  text-transform: none;
}}

/* ---- scene: mono_block ---- */
.mb-line {{
  font-family: var(--mono);
  font-weight: 500;
  font-variation-settings: "wght" 500;
  font-size: 4.2cqw;
  line-height: 1.45;
  color: var(--ink);
  letter-spacing: 0;
  text-transform: none;
}}
.mb-line.accent {{ color: var(--accent); font-weight: 700; font-variation-settings: "wght" 700; }}

/* ---- scene: quote ---- */
.q-quote {{
  font-family: var(--italic);
  font-style: italic;
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 6.5cqw;
  line-height: 1.15;
  color: var(--ink);
  letter-spacing: var(--tracking);
}}
.q-attribution {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.4cqw;
  color: var(--ink-muted);
  margin-top: 3cqw;
  letter-spacing: 0.04em;
  text-transform: none;
}}

/* ---- scene: close ---- */
.c-primary {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 9.2cqw;
  line-height: 1;
  letter-spacing: var(--tracking);
  color: var(--ink);
}}
.c-accent {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 9.2cqw;
  line-height: 1;
  letter-spacing: var(--tracking);
  color: var(--accent);
  margin-top: 1.8cqw;
}}
.c-subtitle {{
  font-family: var(--italic);
  font-style: italic;
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.4cqw;
  color: var(--ink-muted);
  margin-top: 4.4cqw;
  letter-spacing: 0.02em;
  text-transform: none;
}}

/* ---- controls (only visible in browser, not the recorded MP4) ---- */
.controls {{
  display: flex;
  align-items: center;
  gap: 12px;
  width: min(86vmin, calc(100vh - 100px));
  color: rgba(255,255,255,0.55);
  font-family: var(--body);
  font-size: 11px;
}}
.controls button {{
  background: transparent;
  border: 1px solid rgba(255,255,255,0.18);
  color: rgba(255,255,255,0.85);
  font: inherit;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}}
.controls button:hover {{ border-color: var(--accent); color: var(--accent); }}
.progress {{
  flex: 1;
  height: 2px;
  background: rgba(255,255,255,0.12);
  border-radius: 1px;
  overflow: hidden;
}}
.progress-fill {{
  height: 100%;
  width: 0%;
  background: var(--accent);
}}
.clock {{ font-variant-numeric: tabular-nums; color: rgba(255,255,255,0.85); }}
"""


def render_scene(idx, scene):
    tpl = scene["template"]
    if tpl == "title":
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="title">
  <div class="t-headline">{esc(scene['headline'])}</div>
  <div class="eyebrow-small">{esc(scene['eyebrow'])}</div>
</section>"""

    if tpl == "stack":
        items_html = "".join(
            f"""<div class="s-item"><div class="s-name">{esc(it['name'])}</div>"""
            f"""<div class="s-descriptor">{esc(it['descriptor'])}</div></div>"""
            for it in scene["items"]
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="stack">
  <div class="uc-eyebrow">{esc(scene['eyebrow'])}</div>
  <div class="divider-rule"></div>
  {items_html}
</section>"""

    if tpl in ("two_line", "three_line"):
        size_class = "size-2" if tpl == "two_line" else "size-3"
        accent_idx = scene.get("accent_idx", -1)
        lines_html = "".join(
            f"""<div class="line {size_class}{' accent' if i == accent_idx else ''}">{esc(line)}</div>"""
            for i, line in enumerate(scene["lines"])
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="{tpl}">
  {lines_html}
</section>"""

    if tpl == "fix":
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="fix">
  <div class="f-primary">{esc(scene['primary'])}</div>
  <div class="f-secondary">{esc(scene['secondary'])}</div>
</section>"""

    if tpl == "mono_block":
        accent_idx = scene.get("accent_idx", -1)
        lines_html = "".join(
            f"""<div class="mb-line{' accent' if i == accent_idx else ''}">{esc(line)}</div>"""
            for i, line in enumerate(scene["lines"])
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="mono_block">
  {lines_html}
</section>"""

    if tpl == "quote":
        attr_html = (
            f"""<div class="q-attribution">{esc(scene['attribution'])}</div>"""
            if scene.get("attribution")
            else ""
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="quote">
  <div class="q-quote">{esc(scene['quote'])}</div>
  {attr_html}
</section>"""

    if tpl == "close":
        sub = (
            f"""<div class="c-subtitle">{esc(scene['subtitle'])}</div>"""
            if scene.get("subtitle")
            else ""
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="close">
  <div class="c-primary">{esc(scene['primary'])}</div>
  <div class="c-accent">{esc(scene['accent'])}</div>
  {sub}
</section>"""

    raise SystemExit(f"Unknown scene template: {tpl!r}")


def build_timeline(spec):
    cursor = 0.0
    timeline = []
    emphases = []
    for i, sc in enumerate(spec["scenes"]):
        dur = float(sc.get("duration_s", 3.0))
        timeline.append({"idx": i, "tpl": sc["template"], "start": round(cursor, 3), "end": round(cursor + dur, 3), "dur": round(dur, 3)})
        if sc.get("emphasize"):
            emphases.append(round(cursor, 3))
        cursor += dur
    return timeline, round(cursor, 3), emphases


def build_js(spec, timeline, total_s, emphases):
    motion = spec["design"].get("motion", {})
    register = motion.get("register", "fade")
    preset = MOTION_PRESETS.get(register, MOTION_PRESETS["fade"])
    in_s = motion.get("scene_in_s", preset["in_s"])
    out_s = motion.get("scene_out_s", preset["out_s"])
    y_px = preset["y_px"]
    stagger_s = motion.get("stagger_s", preset["stagger_s"])
    scale_from = preset["scale_from"]

    tl_json = json.dumps(timeline)
    return r"""
const TL = """ + tl_json + r""";
const DURATION_S = """ + str(total_s) + r""";
const FADE_IN_S = """ + f"{in_s}" + r""";
const FADE_OUT_S = """ + f"{out_s}" + r""";
const STAGGER_S = """ + f"{stagger_s}" + r""";
const Y_PX = """ + f"{y_px}" + r""";
const SCALE_FROM = """ + f"{scale_from}" + r""";
const EMPHASES = """ + json.dumps(emphases) + r""";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const sceneEls = $$(".scene");

let startedAt = 0;
let raf = null;

function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

function applySceneAnimations(idx, sceneT, dur) {
  const el = sceneEls[idx];
  let op = 1;
  if (sceneT < FADE_IN_S) op = sceneT / FADE_IN_S;
  else if (sceneT > dur - FADE_OUT_S) op = Math.max(0, (dur - sceneT) / FADE_OUT_S);
  el.style.opacity = op.toFixed(3);

  const children = el.children;
  for (let i = 0; i < children.length; i++) {
    const c = children[i];
    const d = i * STAGGER_S;
    const local = sceneT - d;
    if (local < 0) {
      c.style.opacity = 0;
      c.style.transform = (Y_PX > 0)
        ? `translateY(${Y_PX}px)`
        : (SCALE_FROM < 1 ? `scale(${SCALE_FROM})` : "");
      continue;
    }
    const t = Math.min(1, local / Math.max(FADE_IN_S, 0.001));
    const eased = easeOut(t);
    c.style.opacity = eased.toFixed(3);
    if (Y_PX > 0) {
      c.style.transform = `translateY(${(Y_PX * (1 - eased)).toFixed(2)}px)`;
    } else if (SCALE_FROM < 1) {
      const s = SCALE_FROM + (1 - SCALE_FROM) * eased;
      c.style.transform = `scale(${s.toFixed(3)})`;
    } else {
      c.style.transform = "";
    }
    if (c.classList.contains("divider-rule")) {
      c.style.width = `${(12 * eased).toFixed(2)}vmin`;
    }
  }
}

function resetScenes() {
  sceneEls.forEach((el) => {
    el.style.opacity = 0;
    Array.from(el.children).forEach(c => {
      c.style.opacity = 0;
      c.style.transform = "";
    });
  });
}

function hideScene(i) {
  const el = sceneEls[i];
  el.style.opacity = 0;
  const children = el.children;
  for (let k = 0; k < children.length; k++) {
    children[k].style.opacity = 0;
    children[k].style.transform = "";
    if (children[k].classList.contains("divider-rule")) {
      children[k].style.width = "0";
    }
  }
}

function tick() {
  const t = (performance.now() - startedAt) / 1000;
  const clamped = Math.min(t, DURATION_S);
  for (let i = 0; i < TL.length; i++) {
    const sc = TL[i];
    if (clamped < sc.start || clamped >= sc.end) {
      hideScene(i);
    } else {
      applySceneAnimations(i, clamped - sc.start, sc.end - sc.start);
    }
  }

  $("#pf").style.width = `${(clamped / DURATION_S * 100).toFixed(2)}%`;
  const sec = Math.floor(clamped);
  const mm = String(Math.floor(sec / 60)).padStart(2, "0");
  const ss = String(sec % 60).padStart(2, "0");
  $("#clock").textContent = `${mm}:${ss}`;

  if (t < DURATION_S) raf = requestAnimationFrame(tick);
}

// audio engine (browser-side; mp4 path uses synth_audio.py instead)
let audioCtx = null;
let masterGain = null;
let liveNodes = [];
let soundEnabled = true;
function initAudio() {
  if (audioCtx) return;
  const Ctx = window.AudioContext || window.webkitAudioContext;
  if (!Ctx) return;
  audioCtx = new Ctx();
  masterGain = audioCtx.createGain();
  masterGain.gain.value = 0.6;
  const lp = audioCtx.createBiquadFilter();
  lp.type = "lowpass"; lp.frequency.value = 13000;
  masterGain.connect(lp).connect(audioCtx.destination);
}
function track(node, when, dur) {
  node.start(when); node.stop(when + dur + 0.1); liveNodes.push(node);
}
function stopAll() { liveNodes.forEach(n => { try { n.stop(); } catch (e) {} }); liveNodes = []; }
function playPad(t0, totalDur) {
  [261.63, 329.63, 392.00, 493.88, 587.33].forEach((f, i) => {
    const o = audioCtx.createOscillator();
    o.type = "sine"; o.frequency.value = f * (1 + (i - 2) * 0.0008);
    const g = audioCtx.createGain();
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(0.025, t0 + 2.5);
    g.gain.setValueAtTime(0.025, t0 + totalDur - 2.5);
    g.gain.linearRampToValueAtTime(0.0001, t0 + totalDur);
    o.connect(g).connect(masterGain);
    track(o, t0, totalDur);
  });
}
function playSwell(t0) {
  const len = Math.floor(audioCtx.sampleRate * 1.4);
  const buf = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < len; i++) data[i] = (Math.random() * 2 - 1) * 0.4;
  const src = audioCtx.createBufferSource(); src.buffer = buf;
  const bp = audioCtx.createBiquadFilter(); bp.type = "bandpass";
  bp.frequency.value = 2200; bp.Q.value = 0.7;
  const g = audioCtx.createGain();
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.exponentialRampToValueAtTime(0.18, t0 + 1.2);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.4);
  src.connect(bp).connect(g).connect(masterGain);
  track(src, t0, 1.5);
}
function playMallet(t0, freq, vol) {
  const o = audioCtx.createOscillator();
  const mod = audioCtx.createOscillator();
  const modGain = audioCtx.createGain();
  o.type = "sine"; mod.type = "sine";
  o.frequency.value = freq; mod.frequency.value = freq * 3.2;
  modGain.gain.value = freq * 1.4;
  mod.connect(modGain).connect(o.frequency);
  const g = audioCtx.createGain();
  g.gain.setValueAtTime(0, t0);
  g.gain.linearRampToValueAtTime(vol, t0 + 0.005);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.6);
  o.connect(g).connect(masterGain);
  track(o, t0, 1.7); track(mod, t0, 1.7);
}
function scheduleScore(t0) {
  playPad(t0, DURATION_S);
  TL.slice(1).forEach(s => playSwell(t0 + s.start - 0.6));
  EMPHASES.forEach(e => {
    playMallet(t0 + e + 0.0, 523.25, 0.22);
    playMallet(t0 + e + 0.05, 659.25, 0.16);
  });
}

async function play() {
  cancelAnimationFrame(raf);
  resetScenes();
  stopAll();
  if (soundEnabled) {
    initAudio();
    if (audioCtx) {
      try { await audioCtx.resume(); } catch (e) {}
      if (audioCtx.state === "running") {
        scheduleScore(audioCtx.currentTime + 0.15);
      }
    }
  }
  startedAt = performance.now() + 150;
  setTimeout(() => { raf = requestAnimationFrame(tick); }, 150);
}

document.getElementById("play").addEventListener("click", play);
document.getElementById("mute").addEventListener("click", () => {
  soundEnabled = !soundEnabled;
  document.getElementById("mute").textContent = "sound: " + (soundEnabled ? "on" : "off");
  if (!soundEnabled) stopAll();
});
play();
"""


def build_html(spec):
    timeline, total_s, emphases = build_timeline(spec)
    css = build_css(spec)
    scenes_html = "\n".join(render_scene(i, sc) for i, sc in enumerate(spec["scenes"]))
    js = build_js(spec, timeline, total_s, emphases)
    title_text = spec.get("topic") or spec["scenes"][0].get("headline") or "video"

    # Encode the timeline + emphases for record_mp4.py to read.
    bv_meta = json.dumps({"total_s": total_s, "timeline": timeline, "emphases": emphases})

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<meta name="bv-timeline" content='{esc(bv_meta)}' />
<title>{esc(title_text)}</title>
<style>{css}</style>
</head>
<body>
<div class="stage" id="stage">
{scenes_html}
</div>
<div class="controls">
  <button id="play">replay</button>
  <button id="mute">sound: on</button>
  <div class="progress"><div class="progress-fill" id="pf"></div></div>
  <span class="clock" id="clock">00:00</span>
</div>
<script>{js}</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", help="Path to spec JSON")
    parser.add_argument("output", help="Path to write HTML")
    args = parser.parse_args()
    spec = json.loads(Path(args.spec).read_text())
    html = build_html(spec)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"Wrote {out} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
