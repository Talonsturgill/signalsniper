#!/usr/bin/env python3
"""
brand-video HTML builder.

Reads a brand-video spec and emits a single self-contained HTML file
with fonts base64-embedded, layout driven by the spec's design tokens,
and an animated timeline of variable-duration scenes.

Adds (per PLAYBOOK.md):
- Texture overlay (SVG turbulence grain + vignette + halation)
- Per-scene camera moves (push_in, pull_back, ken_burns, crash_zoom,
  orbit, parallax_drift, static_breathe)
- Lighting arc (full-stage gradient that shifts hue across the runtime)
- New scene templates: diagram, flash, big_number, terminal, split
- Audio palette pass-through to synth_audio.py via the bv-meta tag
- Optional held-subject persistent corner wordmark

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

FONT_FILES = {
    "Inter":              ("Inter.ttf",                True),
    "JetBrainsMono":      ("JetBrainsMono.ttf",        True),
    "IBMPlexSerif":       ("IBMPlexSerif-Regular.ttf", False),
    "IBMPlexSerif-Bold":  ("IBMPlexSerif-Bold.ttf",    False),
    "EBGaramond":         ("EBGaramond.ttf",           True),
    "SpaceGrotesk":       ("SpaceGrotesk.ttf",         True),
    "BricolageGrotesque": ("BricolageGrotesque.ttf",   True),
    "Fraunces":           ("Fraunces.ttf",             True),
}

MOTION_PRESETS = {
    "fade":  {"in_s": 0.40, "out_s": 0.27, "y_px": 14, "stagger_s": 0.27, "scale_from": 1.00},
    "cut":   {"in_s": 0.05, "out_s": 0.05, "y_px":  0, "stagger_s": 0.10, "scale_from": 1.00},
    "scale": {"in_s": 0.45, "out_s": 0.27, "y_px":  0, "stagger_s": 0.30, "scale_from": 0.92},
}

CAMERA_MOVES = {
    "push_in",
    "pull_back",
    "ken_burns",
    "crash_zoom",
    "orbit",
    "parallax_drift",
    "static_breathe",
    "none",
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
    fonts = spec["design"].get("fonts", {})
    display = fonts.get("display") or "IBMPlexSerif"
    body = fonts.get("body") or display
    italic = fonts.get("italic") or body
    mono = "JetBrainsMono"
    return display, body, italic, mono


def build_css(spec):
    d = spec["design"]
    t = d["tokens"]
    typo = d.get("typography", {})
    motion = d.get("motion", {})
    layout = d.get("layout", {})
    texture = d.get("texture", {})

    display, body, italic, mono = resolve_fonts(spec)
    all_fonts = {display, body, italic, mono}
    fonts_css = font_face_block(all_fonts)

    register = motion.get("register", "fade")
    preset = MOTION_PRESETS.get(register, MOTION_PRESETS["fade"])

    display_weight = typo.get("display_weight", 700)
    body_weight = typo.get("body_weight", 400)
    letter_spacing = typo.get("letter_spacing_em", -0.02)
    case = typo.get("case", "preserve")
    text_transform = "uppercase" if case == "upper" else ("lowercase" if case == "lower" else "none")
    italic_descriptors = "italic" if typo.get("italic_descriptors", True) else "normal"

    padding_pct = layout.get("padding_pct", 8)
    rule_thickness = layout.get("rule_thickness_px", 2)
    stage_radius = layout.get("stage_radius_px", 12)

    grain_strength = texture.get("grain", 0.06)
    vignette_strength = texture.get("vignette", 0.20)
    halation_strength = texture.get("halation", 0.0)
    lighting_strength = texture.get("lighting_arc", 0.30)

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

.stage-inner {{
  position: absolute;
  inset: 0;
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
  transform-origin: center center;
  will-change: transform, opacity;
}}

.scene > * {{
  font-variation-settings: "wght" var(--display-weight);
  text-transform: {text_transform};
}}

/* ---------------- camera move keyframes ---------------- */
@keyframes camPushIn {{
  from {{ transform: scale(1.000); }}
  to   {{ transform: scale(1.10); }}
}}
@keyframes camPullBack {{
  from {{ transform: scale(1.08); }}
  to   {{ transform: scale(1.00); }}
}}
@keyframes camKenBurns {{
  from {{ transform: scale(1.04) translate(0.2%, 0.2%); }}
  to   {{ transform: scale(1.12) translate(-0.6%, -0.4%); }}
}}
@keyframes camCrashZoom {{
  0%   {{ transform: scale(1.00); }}
  18%  {{ transform: scale(1.85); }}
  100% {{ transform: scale(1.85); }}
}}
@keyframes camOrbit {{
  from {{ transform: perspective(1400px) rotateY(-7deg) scale(1.02); }}
  to   {{ transform: perspective(1400px) rotateY(7deg)  scale(1.02); }}
}}
@keyframes camParallaxDrift {{
  from {{ transform: translate(0.6%, 0) scale(1.04); }}
  to   {{ transform: translate(-0.6%, -0.2%) scale(1.04); }}
}}
@keyframes camBreathe {{
  0%, 100% {{ transform: scale(1.000); }}
  50%      {{ transform: scale(1.008); }}
}}

.scene[data-cam="push_in"]        {{ animation: camPushIn        var(--scene-dur, 3s) ease-out forwards; }}
.scene[data-cam="pull_back"]      {{ animation: camPullBack      var(--scene-dur, 3s) ease-out forwards; }}
.scene[data-cam="ken_burns"]      {{ animation: camKenBurns      var(--scene-dur, 3s) ease-in-out forwards; }}
.scene[data-cam="crash_zoom"]     {{ animation: camCrashZoom     var(--scene-dur, 3s) ease-out forwards; }}
.scene[data-cam="orbit"]          {{ animation: camOrbit         var(--scene-dur, 3s) ease-in-out forwards; }}
.scene[data-cam="parallax_drift"] {{ animation: camParallaxDrift var(--scene-dur, 3s) ease-in-out forwards; }}
.scene[data-cam="static_breathe"] {{ animation: camBreathe       var(--scene-dur, 3s) ease-in-out forwards; }}
.scene[data-cam="none"]           {{ animation: none; }}

/* ---------------- texture overlay (always on) ---------------- */
.texture {{
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 50;
  mix-blend-mode: overlay;
}}
.texture-grain {{
  position: absolute;
  inset: -2%;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.95' numOctaves='2' seed='9'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.7 0'/></filter><rect width='220' height='220' filter='url(%23n)'/></svg>");
  background-size: 220px 220px;
  opacity: {grain_strength};
  animation: grainShift 1.6s steps(6) infinite;
}}
@keyframes grainShift {{
  0%   {{ transform: translate(0, 0); }}
  16%  {{ transform: translate(-1.5%, 1%); }}
  33%  {{ transform: translate(1%, -1%); }}
  50%  {{ transform: translate(-1%, -1.5%); }}
  66%  {{ transform: translate(1.5%, 1%); }}
  83%  {{ transform: translate(-0.5%, 1.5%); }}
  100% {{ transform: translate(0, 0); }}
}}
.texture-vignette {{
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,{vignette_strength}) 100%);
  mix-blend-mode: multiply;
}}
.texture-halation {{
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 35%, rgba(255,210,160,{halation_strength}) 0%, transparent 60%);
  mix-blend-mode: screen;
}}

/* ---------------- lighting arc (full-stage hue drift) ---------------- */
.lighting-arc {{
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 40;
  mix-blend-mode: overlay;
  opacity: {lighting_strength};
  background: linear-gradient(135deg,
    rgba(255, 220, 180, 0.0) 0%,
    rgba(255, 220, 180, 0.4) 50%,
    rgba(140, 180, 255, 0.4) 100%);
  animation: lightingArcShift var(--total-dur, 25s) ease-in-out forwards;
}}
@keyframes lightingArcShift {{
  0%   {{ filter: hue-rotate(-12deg); }}
  50%  {{ filter: hue-rotate(0deg); }}
  100% {{ filter: hue-rotate(20deg); }}
}}

/* ---------------- shared atoms ---------------- */
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

/* ---- title ---- */
.t-headline {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 11cqw;
  line-height: 1.02;
  letter-spacing: var(--tracking);
  color: var(--ink);
}}

/* ---- stack ---- */
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

/* ---- two_line / three_line ---- */
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

/* ---- fix ---- */
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

/* ---- mono_block ---- */
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

/* ---- quote ---- */
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

/* ---- close ---- */
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

/* ---- diagram ---- */
.scene[data-tpl="diagram"] {{ padding: 4%; justify-content: flex-start; }}
.diagram-eyebrow {{
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 2.2cqw;
  letter-spacing: 0.34em;
  color: var(--accent);
  text-transform: uppercase;
  margin-top: 2cqw;
  margin-bottom: 3cqw;
}}
.diagram-svg {{
  width: 90%;
  height: 78%;
  display: block;
  overflow: visible;
}}
.dg-edge {{
  stroke: var(--ink-muted);
  stroke-width: 0.35;
  fill: none;
  stroke-dasharray: 200;
  stroke-dashoffset: 200;
}}
.dg-edge.dashed {{ stroke-dasharray: 1.6 1.6; stroke-dashoffset: 0; opacity: 0; }}
.dg-edge.accent {{ stroke: var(--accent); stroke-width: 0.55; }}
.dg-node {{
  fill: var(--canvas);
  stroke: var(--ink);
  stroke-width: 0.4;
  opacity: 0;
}}
.dg-node.accent {{ stroke: var(--accent); stroke-width: 0.7; }}
.dg-node.filled {{ fill: var(--ink); }}
.dg-node.filled.accent {{ fill: var(--accent); stroke: var(--accent); }}
.dg-label {{
  font-family: var(--body);
  font-weight: 500;
  font-size: 2.3px;
  fill: var(--ink);
  text-anchor: middle;
  dominant-baseline: middle;
  letter-spacing: 0;
  opacity: 0;
}}
.dg-label.on-filled {{ fill: var(--canvas); }}

/* ---- flash ---- */
.scene[data-tpl="flash"] {{ background: var(--accent); }}
.flash-word {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 18cqw;
  line-height: 1;
  letter-spacing: var(--tracking);
  color: var(--canvas);
}}
.flash-caption {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.6cqw;
  color: var(--canvas);
  margin-top: 3cqw;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  opacity: 0.78;
}}

/* ---- big_number ---- */
.bn-numeral {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 28cqw;
  line-height: 0.92;
  letter-spacing: -0.04em;
  color: var(--accent);
}}
.bn-caption {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 3.2cqw;
  color: var(--ink);
  margin-top: 2.6cqw;
  letter-spacing: 0.04em;
  text-transform: none;
}}
.bn-sub {{
  font-family: var(--italic);
  font-style: italic;
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.2cqw;
  color: var(--ink-muted);
  margin-top: 1cqw;
  text-transform: none;
}}

/* ---- terminal ---- */
.scene[data-tpl="terminal"] {{ padding: 6%; }}
.terminal-frame {{
  background: var(--canvas);
  border: 1px solid var(--hairline);
  border-radius: 4px;
  width: 88%;
  height: 78%;
  padding: 2.5cqw 3cqw 3cqw 3cqw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 1cqw 3cqw rgba(0,0,0,0.18);
}}
.terminal-bar {{
  display: flex;
  gap: 0.7cqw;
  margin-bottom: 2.2cqw;
  align-items: center;
}}
.terminal-dot {{ width: 1.1cqw; height: 1.1cqw; border-radius: 50%; opacity: 0.55; background: var(--ink-muted); }}
.terminal-title {{
  font-family: var(--mono);
  font-size: 1.6cqw;
  color: var(--ink-muted);
  margin-left: 1cqw;
  letter-spacing: 0;
  text-transform: none;
}}
.terminal-body {{
  flex: 1;
  font-family: var(--mono);
  font-size: 2.4cqw;
  line-height: 1.55;
  color: var(--ink);
  text-align: left;
  letter-spacing: 0;
  text-transform: none;
}}
.terminal-line {{ display: block; opacity: 0; }}
.terminal-line.accent {{ color: var(--accent); }}
.terminal-line .prompt {{ color: var(--accent); margin-right: 0.6cqw; }}
.terminal-cursor {{
  display: inline-block;
  width: 0.55em;
  height: 1.0em;
  background: var(--ink);
  vertical-align: -0.12em;
  margin-left: 0.2em;
  animation: blink 1s steps(2) infinite;
}}
@keyframes blink {{ 50% {{ opacity: 0; }} }}

/* ---- split ---- */
.scene[data-tpl="split"] {{ padding: 0; flex-direction: row; }}
.split-pane {{
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6%;
  text-align: center;
  opacity: 0;
}}
.split-pane.left  {{ border-right: 1px solid var(--hairline); }}
.split-pane.right {{ background: var(--accent); color: var(--canvas); }}
.split-pane .label {{
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 1.9cqw;
  letter-spacing: 0.34em;
  text-transform: uppercase;
  margin-bottom: 2.4cqw;
  opacity: 0.7;
}}
.split-pane .value {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 7.5cqw;
  line-height: 1.05;
  letter-spacing: var(--tracking);
}}

/* ---- held subject (persistent corner wordmark, optional) ---- */
.held-subject {{
  position: absolute;
  bottom: 4%;
  left: 4%;
  z-index: 30;
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 1.5cqw;
  color: var(--ink-muted);
  letter-spacing: 0.32em;
  text-transform: uppercase;
  opacity: 0;
  pointer-events: none;
}}
.held-subject .accent-dot {{
  display: inline-block;
  width: 0.6em;
  height: 0.6em;
  background: var(--accent);
  border-radius: 50%;
  margin-right: 0.7em;
  vertical-align: 0.05em;
}}

/* ---- controls ---- */
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
    cam = scene.get("camera", "static_breathe")
    if cam not in CAMERA_MOVES:
        raise SystemExit(f"Unknown camera move: {cam!r}. Valid: {sorted(CAMERA_MOVES)}")
    dur = float(scene.get("duration_s", 3.0))
    extra_attrs = f' data-cam="{cam}" style="--scene-dur: {dur}s;"'

    if tpl == "title":
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="title"{extra_attrs}>
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
<section class="scene" data-idx="{idx}" data-tpl="stack"{extra_attrs}>
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
<section class="scene" data-idx="{idx}" data-tpl="{tpl}"{extra_attrs}>
  {lines_html}
</section>"""

    if tpl == "fix":
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="fix"{extra_attrs}>
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
<section class="scene" data-idx="{idx}" data-tpl="mono_block"{extra_attrs}>
  {lines_html}
</section>"""

    if tpl == "quote":
        attr_html = (
            f"""<div class="q-attribution">{esc(scene['attribution'])}</div>"""
            if scene.get("attribution")
            else ""
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="quote"{extra_attrs}>
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
<section class="scene" data-idx="{idx}" data-tpl="close"{extra_attrs}>
  <div class="c-primary">{esc(scene['primary'])}</div>
  <div class="c-accent">{esc(scene['accent'])}</div>
  {sub}
</section>"""

    if tpl == "diagram":
        nodes = scene["nodes"]
        edges = scene.get("edges", [])
        eyebrow = scene.get("eyebrow", "")

        node_w = 22.0
        node_h = 9.0

        def node_el(n):
            x = float(n["x"])
            y = float(n["y"])
            shape = n.get("shape", "rect")
            classes = "dg-node"
            if n.get("accent"): classes += " accent"
            if n.get("filled"): classes += " filled"
            label_classes = "dg-label"
            if n.get("filled"): label_classes += " on-filled"
            if shape == "circle":
                r = node_h / 2.0
                el = f'<circle class="{classes}" cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" />'
            else:
                rx = x - node_w / 2.0
                ry = y - node_h / 2.0
                el = (
                    f'<rect class="{classes}" x="{rx:.2f}" y="{ry:.2f}" '
                    f'width="{node_w:.2f}" height="{node_h:.2f}" rx="0.6" />'
                )
            label = (
                f'<text class="{label_classes}" x="{x:.2f}" y="{y:.2f}">{esc(n["label"])}</text>'
            )
            return el + label

        def edge_path(e):
            a = nodes[e["from"]]
            b = nodes[e["to"]]
            ax, ay = float(a["x"]), float(a["y"])
            bx, by = float(b["x"]), float(b["y"])
            classes = "dg-edge"
            if e.get("style") == "dashed": classes += " dashed"
            if e.get("accent"): classes += " accent"
            return f'<path class="{classes}" d="M{ax:.2f} {ay:.2f} L{bx:.2f} {by:.2f}" />'

        edges_svg = "".join(edge_path(e) for e in edges)
        nodes_svg = "".join(node_el(n) for n in nodes)
        eyebrow_div = (
            f'<div class="diagram-eyebrow">{esc(eyebrow)}</div>' if eyebrow else ""
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="diagram"{extra_attrs}>
  {eyebrow_div}
  <svg class="diagram-svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
    <g class="dg-edges">{edges_svg}</g>
    <g class="dg-nodes">{nodes_svg}</g>
  </svg>
</section>"""

    if tpl == "flash":
        caption_html = (
            f"""<div class="flash-caption">{esc(scene['caption'])}</div>"""
            if scene.get("caption")
            else ""
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="flash"{extra_attrs}>
  <div class="flash-word">{esc(scene['word'])}</div>
  {caption_html}
</section>"""

    if tpl == "big_number":
        sub_html = (
            f"""<div class="bn-sub">{esc(scene['sub'])}</div>"""
            if scene.get("sub")
            else ""
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="big_number"{extra_attrs}>
  <div class="bn-numeral">{esc(scene['numeral'])}</div>
  <div class="bn-caption">{esc(scene['caption'])}</div>
  {sub_html}
</section>"""

    if tpl == "terminal":
        title = scene.get("title", "")
        lines = scene["lines"]
        accent_idx = scene.get("accent_idx", -1)

        def render_line(i, line):
            text = line["text"] if isinstance(line, dict) else line
            show_prompt = line.get("prompt", True) if isinstance(line, dict) else True
            classes = "terminal-line" + (" accent" if i == accent_idx else "")
            prompt_html = '<span class="prompt">$</span>' if show_prompt else ""
            cursor_html = '<span class="terminal-cursor"></span>' if i == len(lines) - 1 else ""
            return f'<span class="{classes}">{prompt_html}{esc(text)}{cursor_html}</span>'

        lines_html = "".join(render_line(i, line) for i, line in enumerate(lines))
        title_html = f'<div class="terminal-title">{esc(title)}</div>' if title else ""
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="terminal"{extra_attrs}>
  <div class="terminal-frame">
    <div class="terminal-bar">
      <div class="terminal-dot"></div>
      <div class="terminal-dot"></div>
      <div class="terminal-dot"></div>
      {title_html}
    </div>
    <div class="terminal-body">{lines_html}</div>
  </div>
</section>"""

    if tpl == "split":
        left = scene["left"]
        right = scene["right"]
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="split"{extra_attrs}>
  <div class="split-pane left">
    <div class="label">{esc(left['label'])}</div>
    <div class="value">{esc(left['value'])}</div>
  </div>
  <div class="split-pane right">
    <div class="label">{esc(right['label'])}</div>
    <div class="value">{esc(right['value'])}</div>
  </div>
</section>"""

    raise SystemExit(f"Unknown scene template: {tpl!r}")


def build_timeline(spec):
    cursor = 0.0
    timeline = []
    emphases = []
    for i, sc in enumerate(spec["scenes"]):
        dur = float(sc.get("duration_s", 3.0))
        timeline.append({
            "idx": i,
            "tpl": sc["template"],
            "start": round(cursor, 3),
            "end": round(cursor + dur, 3),
            "dur": round(dur, 3),
            "emphasize": bool(sc.get("emphasize", False)),
        })
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

  const tpl = el.dataset.tpl;
  if (tpl === "diagram") { animateDiagram(el, sceneT, dur); return; }
  if (tpl === "flash") { animateFlash(el, sceneT, dur); return; }
  if (tpl === "big_number") { animateBigNumber(el, sceneT, dur); return; }
  if (tpl === "terminal") { animateTerminal(el, sceneT, dur); return; }
  if (tpl === "split") { animateSplit(el, sceneT, dur); return; }

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

function animateDiagram(el, t, dur) {
  const eyebrow = el.querySelector(".diagram-eyebrow");
  const svg = el.querySelector(".diagram-svg");
  const groups = el.querySelectorAll(".dg-edges, .dg-nodes");
  const nodes = el.querySelectorAll(".dg-node");
  const labels = el.querySelectorAll(".dg-label");
  const edges = el.querySelectorAll(".dg-edge");

  // containers must be visible; their children are individually animated
  if (svg) svg.style.opacity = 1;
  for (let g = 0; g < groups.length; g++) groups[g].style.opacity = 1;

  if (eyebrow) {
    const e = easeOut(Math.min(1, t / 0.30));
    eyebrow.style.opacity = e.toFixed(3);
    eyebrow.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
  }

  const nodeStart = eyebrow ? 0.30 : 0.05;
  const nodeStep = 0.18;
  for (let i = 0; i < nodes.length; i++) {
    const local = t - nodeStart - i * nodeStep;
    if (local < 0) {
      nodes[i].style.opacity = 0;
      if (labels[i]) labels[i].style.opacity = 0;
      continue;
    }
    const e = easeOut(Math.min(1, local / 0.35));
    nodes[i].style.opacity = e.toFixed(3);
    if (labels[i]) labels[i].style.opacity = e.toFixed(3);
  }

  const edgeStart = nodeStart + nodes.length * nodeStep + 0.10;
  const edgeStep = 0.18;
  for (let i = 0; i < edges.length; i++) {
    const local = t - edgeStart - i * edgeStep;
    const dashed = edges[i].classList.contains("dashed");
    if (local < 0) {
      edges[i].style.opacity = dashed ? 0 : 1;
      if (!dashed) edges[i].style.strokeDashoffset = 200;
      continue;
    }
    if (dashed) {
      edges[i].style.opacity = easeOut(Math.min(1, local / 0.45)).toFixed(3);
    } else {
      const e = easeOut(Math.min(1, local / 0.55));
      edges[i].style.strokeDashoffset = (200 * (1 - e)).toFixed(2);
      edges[i].style.opacity = 1;
    }
  }
}

function animateFlash(el, t, dur) {
  const word = el.querySelector(".flash-word");
  const cap = el.querySelector(".flash-caption");
  if (word) {
    const e = easeOut(Math.min(1, t / 0.20));
    word.style.opacity = e.toFixed(3);
    word.style.transform = `scale(${(0.86 + 0.14 * e).toFixed(3)})`;
  }
  if (cap) {
    const local = t - 0.35;
    if (local < 0) { cap.style.opacity = 0; cap.style.transform = "translateY(6px)"; }
    else {
      const e = easeOut(Math.min(1, local / 0.40));
      cap.style.opacity = e.toFixed(3);
      cap.style.transform = `translateY(${(6 * (1 - e)).toFixed(2)}px)`;
    }
  }
}

function animateBigNumber(el, t, dur) {
  const numeral = el.querySelector(".bn-numeral");
  const cap = el.querySelector(".bn-caption");
  const sub = el.querySelector(".bn-sub");
  if (numeral) {
    const e = easeOut(Math.min(1, t / 0.40));
    numeral.style.opacity = e.toFixed(3);
    numeral.style.transform = `scale(${(0.92 + 0.08 * e).toFixed(3)})`;
  }
  if (cap) {
    const local = t - 0.25;
    if (local < 0) { cap.style.opacity = 0; cap.style.transform = "translateY(8px)"; }
    else {
      const e = easeOut(Math.min(1, local / 0.45));
      cap.style.opacity = e.toFixed(3);
      cap.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
    }
  }
  if (sub) {
    const local = t - 0.55;
    if (local < 0) { sub.style.opacity = 0; sub.style.transform = "translateY(8px)"; }
    else {
      const e = easeOut(Math.min(1, local / 0.45));
      sub.style.opacity = e.toFixed(3);
      sub.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
    }
  }
}

function animateTerminal(el, t, dur) {
  const frame = el.querySelector(".terminal-frame");
  const bar = el.querySelector(".terminal-bar");
  const body = el.querySelector(".terminal-body");
  const dots = el.querySelectorAll(".terminal-dot");
  const title = el.querySelector(".terminal-title");
  const lines = el.querySelectorAll(".terminal-line");

  // frame fades in fast at scene start
  if (frame) {
    const e = easeOut(Math.min(1, t / 0.18));
    frame.style.opacity = e.toFixed(3);
    frame.style.transform = `scale(${(0.985 + 0.015 * e).toFixed(3)})`;
  }
  if (bar) bar.style.opacity = 1;
  if (body) body.style.opacity = 1;
  for (let d = 0; d < dots.length; d++) dots[d].style.opacity = 0.55;
  if (title) title.style.opacity = 0.7;

  const startT = 0.20;
  const stepT = 0.55;
  for (let i = 0; i < lines.length; i++) {
    const local = t - startT - i * stepT;
    if (local < 0) { lines[i].style.opacity = 0; continue; }
    const e = easeOut(Math.min(1, local / 0.18));
    lines[i].style.opacity = e.toFixed(3);
  }
}

function animateSplit(el, t, dur) {
  const panes = el.querySelectorAll(".split-pane");
  for (let i = 0; i < panes.length; i++) {
    const local = t - i * 0.35;
    if (local < 0) {
      panes[i].style.opacity = 0;
      panes[i].style.transform = i === 0 ? "translateX(-3%)" : "translateX(3%)";
      continue;
    }
    const e = easeOut(Math.min(1, local / 0.50));
    panes[i].style.opacity = e.toFixed(3);
    panes[i].style.transform = `translateX(${((i === 0 ? -3 : 3) * (1 - e)).toFixed(2)}%)`;
  }
}

function hideScene(i) {
  const el = sceneEls[i];
  el.style.opacity = 0;
  walkReset(el);
}
function walkReset(node) {
  for (let k = 0; k < node.children.length; k++) {
    const c = node.children[k];
    c.style.opacity = 0;
    c.style.transform = "";
    if (c.classList.contains("divider-rule")) c.style.width = "0";
    if (c.children && c.children.length) walkReset(c);
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

  const held = $(".held-subject");
  if (held) {
    if (clamped < 1.6) held.style.opacity = 0;
    else held.style.opacity = Math.min(0.65, (clamped - 1.6) / 0.6).toFixed(3);
  }

  $("#pf").style.width = `${(clamped / DURATION_S * 100).toFixed(2)}%`;
  const sec = Math.floor(clamped);
  const mm = String(Math.floor(sec / 60)).padStart(2, "0");
  const ss = String(sec % 60).padStart(2, "0");
  $("#clock").textContent = `${mm}:${ss}`;

  if (t < DURATION_S) raf = requestAnimationFrame(tick);
}

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
function trackNode(node, when, dur) {
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
    trackNode(o, t0, totalDur);
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
  trackNode(src, t0, 1.5);
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
  trackNode(o, t0, 1.7); trackNode(mod, t0, 1.7);
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
  for (let i = 0; i < sceneEls.length; i++) hideScene(i);
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

    audio_palette = spec["design"].get("audio_palette", "ambient")
    held_subject_text = spec["design"].get("held_subject")
    framework = spec["design"].get("framework", None)

    bv_meta = json.dumps({
        "total_s": total_s,
        "timeline": timeline,
        "emphases": emphases,
        "audio_palette": audio_palette,
        "framework": framework,
    })

    held_html = ""
    if held_subject_text:
        held_html = (
            f'<div class="held-subject"><span class="accent-dot"></span>'
            f'{esc(held_subject_text)}</div>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<meta name="bv-timeline" content='{esc(bv_meta)}' />
<title>{esc(title_text)}</title>
<style>{css}
.stage {{ --total-dur: {total_s}s; }}
</style>
</head>
<body>
<div class="stage" id="stage">
  <div class="stage-inner">
{scenes_html}
    {held_html}
  </div>
  <div class="lighting-arc"></div>
  <div class="texture">
    <div class="texture-grain"></div>
    <div class="texture-vignette"></div>
    <div class="texture-halation"></div>
  </div>
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
