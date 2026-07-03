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

Usage:
    python build_html.py <spec.json> <output.html>
"""

import argparse
import base64
import colorsys
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
    "rack_focus",
    "dolly_up",
    "tilt_reveal",
    "none",
}

BACKGROUND_STYLES = {"starfield", "aurora", "grid", "none"}


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def kinetic_spans(text):
    """Wrap text into word spans of per-character spans for kinetic reveals.

    Words stay unbreakable (.kword); each character is an animatable .klt
    with a global character index in --ci. The JS animator staggers on --ci.
    """
    words = text.split(" ")
    ci = 0
    out = []
    for w in words:
        chars = []
        for ch in w:
            chars.append(f'<span class="klt" style="--ci:{ci}">{esc(ch)}</span>')
            ci += 1
        out.append(f'<span class="kword">{"".join(chars)}</span>')
        ci += 1  # count the space so cross-word rhythm stays even
    return "".join(out), ci


def word_spans(text):
    """Wrap text into word-level spans (.kword) for word-stagger reveals."""
    words = text.split(" ")
    out = []
    for i, w in enumerate(words):
        out.append(f'<span class="kword" style="--wi:{i}">{esc(w)}</span>')
    return "".join(out), len(words)


def sheen_div(scene):
    """Light-sweep overlay, on by default for logo_reveal, opt-in elsewhere."""
    want = scene.get("sheen", scene["template"] == "logo_reveal")
    return '<div class="scene-sheen" aria-hidden="true"></div>' if want else ""


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _canvas_is_dark(hex_color):
    r, g, b = _hex_to_rgb(hex_color)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) < 128


def _luma(hex_color):
    r, g, b = _hex_to_rgb(hex_color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _mix_toward(hex_color, target_rgb, t):
    r, g, b = _hex_to_rgb(hex_color)
    tr, tg, tb = target_rgb
    return "#{:02x}{:02x}{:02x}".format(
        round(r + (tr - r) * t), round(g + (tg - g) * t), round(b + (tb - b) * t))


def _text_safe_accent(accent, canvas):
    """Brand accents are picked for buttons and links, not for hero glyphs.
    A mid-luma accent (herdr blue ~147) used as TEXT on a dark canvas reads
    dim on a phone. Blend it toward white until it carries ~205 luma (or
    toward black to ~60 on light canvases); hue survives, brightness ships."""
    la = _luma(accent)
    if _canvas_is_dark(canvas):
        if la >= 175:
            return accent
        t = (205 - la) / max(1.0, 255 - la)
        return _mix_toward(accent, (255, 255, 255), min(0.85, t))
    if la <= 90:
        return accent
    t = (la - 60) / max(1.0, la)
    return _mix_toward(accent, (0, 0, 0), min(0.85, t))


def _content_muted(ink_muted, ink, canvas):
    """Muted ink that CARRIES CONTENT (pane activity lines, terminal detail)
    must stay readable: on dark canvases lift it 45% toward full ink when it
    sits below ~175 luma. Decorative muted (corner tags, tickers) keeps the
    quiet original token."""
    lm = _luma(ink_muted)
    if _canvas_is_dark(canvas) and lm < 175:
        return _mix_toward(ink_muted, _hex_to_rgb(ink), 0.6)
    if not _canvas_is_dark(canvas) and lm > 110:
        return _mix_toward(ink_muted, _hex_to_rgb(ink), 0.6)
    return ink_muted


def _hue_shift(hex_color, deg, light=None, sat=None):
    r, g, b = (c / 255 for c in _hex_to_rgb(hex_color))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + deg / 360.0) % 1.0
    if light is not None:
        l = light
    if sat is not None:
        s = sat
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(int(r2 * 255), int(g2 * 255), int(b2 * 255))


def background_html(spec):
    """Emit the configured background layer: starfield (default), aurora, grid, none."""
    design = spec["design"]
    bg = design.get("background") or {}
    style = bg.get("style", "starfield")
    if style not in BACKGROUND_STYLES:
        raise SystemExit(f"Unknown background style: {style!r}. Valid: {sorted(BACKGROUND_STYLES)}")
    intensity = float(bg.get("intensity", 1.0))
    if style == "none":
        return ""
    if style == "starfield":
        return '<canvas id="bgParticles" class="bg-particles" aria-hidden="true"></canvas>'
    if style == "grid":
        return (
            f'<div class="bg-grid" aria-hidden="true" style="--grid-opacity:{0.13 * intensity:.3f}">'
            f'<div class="plane"></div></div>'
        )
    # aurora: three accent-derived blobs drifting behind the scenes.
    # Hue spread stays tight (+/-24deg) so the field reads as the BRAND color
    # breathing, not a rainbow; dark opacity is low so near-black stays black.
    accent = design["tokens"]["accent"]
    dark = _canvas_is_dark(design["tokens"]["canvas"])
    c1 = _hue_shift(accent, 0, light=0.50 if dark else 0.62)
    c2 = _hue_shift(accent, 24, light=0.42 if dark else 0.66)
    c3 = _hue_shift(accent, -18, light=0.38 if dark else 0.70)
    opacity = (0.15 if dark else 0.11) * intensity
    blend = "screen" if dark else "normal"
    blobs = "".join(
        f'<div class="blob b{i}" style="background: radial-gradient(circle at 35% 35%, {c} 0%, transparent 62%);"></div>'
        for i, c in ((1, c1), (2, c2), (3, c3))
    )
    return (
        f'<div class="bg-aurora" aria-hidden="true" '
        f'style="--aurora-opacity:{opacity:.3f};--aurora-blend:{blend}">{blobs}</div>'
    )


def sparkline_geometry(values):
    """Normalize a value series into SVG path data in a 100x56 viewBox."""
    vals = [float(v) for v in values]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    x0, x1 = 6.0, 94.0
    y0, y1 = 50.0, 8.0  # SVG y is inverted: y0 = chart floor
    pts = []
    n = len(vals)
    for i, v in enumerate(vals):
        x = x0 + (x1 - x0) * (i / (n - 1))
        y = y0 + (y1 - y0) * ((v - lo) / span)
        pts.append((round(x, 2), round(y, 2)))
    line_d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    area_d = line_d + f" L{pts[-1][0]} 54 L{pts[0][0]} 54 Z"
    return line_d, area_d, pts[-1]


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
    # overlay blend is invisible over near-black; screen lifts it
    sheen_blend = "screen" if _canvas_is_dark(canvas) else "overlay"
    pane_bg = "rgba(255,255,255,0.06)" if _canvas_is_dark(canvas) else "rgba(0,0,0,0.035)"
    accent_ink = _text_safe_accent(accent, canvas)
    muted_content = _content_muted(ink_muted, ink, canvas)

    return f"""
{fonts_css}

:root {{
  --canvas: {canvas};
  --ink: {ink};
  --ink-muted: {ink_muted};
  --muted-content: {muted_content};
  --accent: {accent};
  --accent-ink: {accent_ink};
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
  gap: 0;
  padding: 0;
}}

/* Full-bleed: the old floating-card matte cost ~26% of pixels to a dark
   border and read dim in the feed. X's tile provides the frame. */
.stage {{
  position: relative;
  width: 100vmin;
  aspect-ratio: 1 / 1;
  background: var(--canvas);
  overflow: hidden;
  border-radius: 0;
  container-type: inline-size;
  container-name: stage;
  contain: layout paint;
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

/* Dark ink on a light canvas anti-aliases thinner than bright ink on a dark
   canvas at the same nominal size (sRGB gamma asymmetry), so downsampled
   readability sampling under-measures true glyph darkness/coverage on light
   aesthetics. A hairline stroke in the same color fattens the rendered glyph
   without changing its visible hue. Harmless on dark canvases too (stroke
   color always matches fill color). */
.t-headline, .s-name, .q-quote, .c-primary, .c-accent, .terminal-body,
.sp-value, .flash-word, .bn-numeral, .dg-label, .mb-line, .line, .fix-primary {{
  -webkit-text-stroke: 3.6px currentColor;
}}

/* ---------------- camera move keyframes ---------------- */
@keyframes camPushIn {{
  from {{ transform: scale(1.000); }}
  to   {{ transform: scale(1.22); }}
}}
@keyframes camPullBack {{
  0%   {{ transform: scale(1.26); }}
  35%  {{ transform: scale(1.09); }}
  72%  {{ transform: scale(1.02); }}
  100% {{ transform: scale(0.99); }}
}}
@keyframes camKenBurns {{
  from {{ transform: scale(1.06) translate(1.0%, 0.8%); }}
  to   {{ transform: scale(1.20) translate(-1.2%, -0.9%); }}
}}
@keyframes camCrashZoom {{
  0%   {{ transform: scale(1.00); }}
  10%  {{ transform: scale(1.20); }}
  18%  {{ transform: scale(1.24); }}
  100% {{ transform: scale(1.34); }}
}}
@keyframes camOrbit {{
  from {{ transform: perspective(1100px) rotateY(-15deg) scale(1.08); }}
  to   {{ transform: perspective(1100px) rotateY(15deg)  scale(1.08); }}
}}
@keyframes camParallaxDrift {{
  from {{ transform: translate(1.6%, 0.4%) scale(1.07); }}
  to   {{ transform: translate(-1.6%, -0.6%) scale(1.07); }}
}}
@keyframes camBreathe {{
  0%, 100% {{ transform: scale(1.000); }}
  50%      {{ transform: scale(1.008); }}
}}

@keyframes camRackFocus {{
  0%   {{ filter: blur(6px);   transform: scale(1.14); }}
  14%  {{ filter: blur(0px);   transform: scale(1.04); }}
  15%  {{ filter: none;        transform: scale(1.038); }}
  100% {{ filter: none;        transform: scale(1.13); }}
}}
@keyframes camDollyUp {{
  from {{ transform: translateY(3.4%)  scale(1.04); }}
  to   {{ transform: translateY(-2.0%) scale(1.14); }}
}}
@keyframes camTiltReveal {{
  0%   {{ transform: perspective(1200px) rotateX(11deg) translateY(3.0%) scale(1.10); }}
  30%  {{ transform: perspective(1200px) rotateX(2deg)  translateY(0.7%) scale(1.03); }}
  55%  {{ transform: perspective(1200px) rotateX(0deg)  translateY(0%)   scale(1.02); }}
  100% {{ transform: perspective(1200px) rotateX(-1.5deg) translateY(-1.2%) scale(1.08); }}
}}

/* Linear timing everywhere: easing shape lives in the keyframes (piecewise),
   so the camera keeps perceptible velocity through the WHOLE scene instead of
   parking after the first second (decelerating curves read as freeze-frames
   in a feed). */
.scene[data-cam="push_in"]        {{ animation: camPushIn        var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="pull_back"]      {{ animation: camPullBack      var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="ken_burns"]      {{ animation: camKenBurns      var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="crash_zoom"]     {{ animation: camCrashZoom     var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="orbit"]          {{ animation: camOrbit         var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="parallax_drift"] {{ animation: camParallaxDrift var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="static_breathe"] {{ animation: camBreathe       var(--scene-dur, 3s) ease-in-out forwards; }}
.scene[data-cam="rack_focus"]     {{ animation: camRackFocus     var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="dolly_up"]       {{ animation: camDollyUp       var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="tilt_reveal"]    {{ animation: camTiltReveal    var(--scene-dur, 3s) linear forwards; }}
.scene[data-cam="none"]           {{ animation: none; }}
/* Cameras are SCRUBBED by the timeline driver: CSS animations otherwise start
   at page load and finish before late scenes ever become visible (every
   camera past scene 1 shipped as a parked end-pose until this). */
.scene[data-cam] {{ animation-play-state: paused; }}

/* ---------------- kinetic per-character type ---------------- */
.kword {{ display: inline-block; white-space: nowrap; }}
.kword + .kword {{ margin-left: 0.26em; }}
.klt {{
  display: inline-block;
  opacity: 0;
}}

/* ---------------- light sweep (sheen) ---------------- */
.scene-sheen {{
  position: absolute;
  top: -55%;
  left: 0;
  width: 34%;
  height: 210%;
  background: linear-gradient(100deg,
    rgba(255,255,255,0) 0%,
    rgba(255,255,255,0.14) 45%,
    rgba(255,255,255,0.22) 50%,
    rgba(255,255,255,0.14) 55%,
    rgba(255,255,255,0) 100%);
  transform: translateX(-260%) skewX(-16deg);
  mix-blend-mode: {sheen_blend};
  pointer-events: none;
  opacity: 0;
  z-index: 6;
}}

/* ---------------- held subject wordmark ---------------- */
.held-subject {{
  position: absolute;
  left: 4.2%;
  bottom: 3.8%;
  z-index: 30;
  font-family: var(--mono);
  font-size: 1.85cqw;
  letter-spacing: 0.30em;
  transition: opacity 0.35s ease-out;
  text-transform: uppercase;
  color: var(--ink-muted);
  opacity: 0;
  pointer-events: none;
}}
.held-subject::before {{
  content: "";
  display: inline-block;
  width: 0.9cqw;
  height: 0.9cqw;
  border-radius: 50%;
  background: var(--accent);
  margin-right: 1.0cqw;
  vertical-align: 6%;
}}

/* ---------------- aurora background ---------------- */
.bg-aurora {{
  position: absolute;
  inset: -12%;
  z-index: 1;
  pointer-events: none;
}}
.bg-aurora .blob {{
  position: absolute;
  width: 68%;
  height: 68%;
  border-radius: 50%;
  opacity: var(--aurora-opacity, 0.20);
  mix-blend-mode: var(--aurora-blend, screen);
}}
.bg-aurora .blob.b1 {{ top: -14%; left: -10%; animation: auroraDrift1 26s ease-in-out infinite alternate; }}
.bg-aurora .blob.b2 {{ right: -16%; top: 22%;  animation: auroraDrift2 31s ease-in-out infinite alternate; }}
.bg-aurora .blob.b3 {{ left: 14%; bottom: -20%; animation: auroraDrift3 23s ease-in-out infinite alternate; }}
@keyframes auroraDrift1 {{ from {{ transform: translate(0,0) scale(1); }}     to {{ transform: translate(9%, 7%) scale(1.14); }} }}
@keyframes auroraDrift2 {{ from {{ transform: translate(0,0) scale(1.10); }} to {{ transform: translate(-8%, -5%) scale(0.94); }} }}
@keyframes auroraDrift3 {{ from {{ transform: translate(0,0) scale(0.96); }} to {{ transform: translate(6%, -9%) scale(1.12); }} }}

/* ---------------- perspective grid background ---------------- */
.bg-grid {{
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
  opacity: var(--grid-opacity, 0.13);
}}
.bg-grid .plane {{
  position: absolute;
  left: -50%;
  bottom: -62%;
  width: 200%;
  height: 130%;
  transform: perspective(900px) rotateX(62deg);
  transform-origin: 50% 100%;
  -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,0.9) 30%, transparent 86%);
  mask-image: linear-gradient(to top, rgba(0,0,0,0.9) 30%, transparent 86%);
  overflow: hidden;
}}
.bg-grid .plane::before {{
  content: "";
  position: absolute;
  left: 0; right: 0;
  top: -64px; bottom: -64px;
  background-image:
    repeating-linear-gradient(0deg,  var(--hairline) 0 1px, transparent 1px 64px),
    repeating-linear-gradient(90deg, var(--hairline) 0 1px, transparent 1px 64px);
  animation: gridScroll 9s linear infinite;
  will-change: transform;
}}
@keyframes gridScroll {{
  from {{ transform: translateY(0); }}
  to   {{ transform: translateY(64px); }}
}}

/* ---------------- particle background canvas ---------------- */
.bg-particles {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  opacity: 0.85;
}}

.bv-defs {{ position: absolute; width: 0; height: 0; pointer-events: none; }}

/* ---------------- cut kick (compositor-only cut accent) ---------------- */
.stage.chrom-cut .stage-inner {{
  animation: cutKick 0.16s ease-out;
}}
@keyframes cutKick {{
  0%   {{ transform: scale(1.000); }}
  40%  {{ transform: scale(1.006); }}
  100% {{ transform: scale(1.000); }}
}}

/* ---------------- emphasize flash ---------------- */
.emphasize-flash {{
  position: absolute;
  inset: 0;
  background: var(--accent);
  opacity: 0;
  pointer-events: none;
  z-index: 45;
  mix-blend-mode: screen;
}}
.emphasize-flash.fire {{
  animation: bvEmpFlash 0.32s ease-out forwards;
}}
@keyframes bvEmpFlash {{
  0%   {{ opacity: 0;   }}
  18%  {{ opacity: 0.42; }}
  100% {{ opacity: 0;   }}
}}

/* ---------------- texture overlay (always on) ---------------- */
.texture {{
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 50;
}}
.texture-grain {{
  position: absolute;
  inset: -2%;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.95' numOctaves='2' seed='9'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.7 0'/></filter><rect width='220' height='220' filter='url(%23n)'/></svg>");
  background-size: 220px 220px;
  opacity: {grain_strength};
  animation: grainShift 0.52s steps(13) infinite;
}}
@keyframes grainShift {{
  0%   {{ transform: translate(0, 0); }}
  8%   {{ transform: translate(-1.5%, 1%); }}
  16%  {{ transform: translate(1%, -1.2%); }}
  24%  {{ transform: translate(-0.8%, -1.5%); }}
  32%  {{ transform: translate(1.5%, 0.8%); }}
  40%  {{ transform: translate(-0.4%, 1.4%); }}
  48%  {{ transform: translate(1.2%, -0.6%); }}
  56%  {{ transform: translate(-1.3%, -0.9%); }}
  64%  {{ transform: translate(0.7%, 1.3%); }}
  72%  {{ transform: translate(-1.1%, 0.3%); }}
  80%  {{ transform: translate(0.9%, -1.4%); }}
  88%  {{ transform: translate(-0.6%, -0.4%); }}
  100% {{ transform: translate(0, 0); }}
}}
.texture-vignette {{
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 35%, rgba(255,210,160,{halation_strength}) 0%, transparent 60%),
    radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,{vignette_strength}) 100%);
}}
.texture-halation {{
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 35%, rgba(255,210,160,{halation_strength}) 0%, transparent 60%);
}}

/* ---------------- lighting arc (warm-to-cool crossfade, compositor-only) ---------------- */
.lighting-arc {{ position: absolute; inset: 0; pointer-events: none; z-index: 40; }}
.la-warm, .la-cool {{ position: absolute; inset: 0; }}
.la-warm {{
  background: linear-gradient(135deg, rgba(255,214,170,0.10) 0%, rgba(255,214,170,0.0) 55%);
  opacity: {lighting_strength};
  animation: laWarmFade var(--total-dur, 25s) ease-in-out forwards;
}}
.la-cool {{
  background: linear-gradient(315deg, rgba(140,180,255,0.10) 0%, rgba(140,180,255,0.0) 55%);
  opacity: 0;
  animation: laCoolFade var(--total-dur, 25s) ease-in-out forwards;
}}
@keyframes laWarmFade {{ from {{ opacity: {lighting_strength}; }} to {{ opacity: 0; }} }}
@keyframes laCoolFade {{ from {{ opacity: 0; }} to {{ opacity: {lighting_strength}; }} }}

/* ---------------- shared atoms ---------------- */
.eyebrow-small {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 3.1cqw;
  color: var(--ink-muted);
  margin-top: 2.4cqw;
  letter-spacing: 0;
  text-transform: none;
}}

.uc-eyebrow {{
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 2.7cqw;
  letter-spacing: 0.34em;
  color: var(--accent-ink);
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
  font-size: 11cqw;
  line-height: 1.1;
  color: var(--ink);
  letter-spacing: var(--tracking);
}}
.s-descriptor {{
  font-family: var(--italic);
  font-style: {italic_descriptors};
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.6cqw;
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
.line.accent {{ color: var(--accent-ink); }}

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
.mb-line.accent {{ color: var(--accent-ink); font-weight: 700; font-variation-settings: "wght" 700; }}

/* ---- quote ---- */
.q-quote {{
  font-family: var(--italic);
  font-style: italic;
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 8.2cqw;
  line-height: 1.15;
  color: var(--ink);
  letter-spacing: var(--tracking);
}}
.q-attribution {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.8cqw;
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
  font-size: 12cqw;
  line-height: 1;
  letter-spacing: var(--tracking);
  color: var(--ink);
}}
.c-accent {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 12cqw;
  line-height: 1;
  letter-spacing: var(--tracking);
  color: var(--accent-ink);
  margin-top: 1.8cqw;
}}
.c-subtitle {{
  font-family: var(--italic);
  font-style: italic;
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.9cqw;
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
  font-size: 2.6cqw;
  letter-spacing: 0.34em;
  color: var(--accent-ink);
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
  font-weight: 700;
  font-size: 6.5px;
  fill: var(--ink);
  text-anchor: middle;
  dominant-baseline: middle;
  letter-spacing: 0;
  opacity: 0;
}}
.dg-label.on-filled {{ fill: var(--canvas); }}

.dg-grid {{
  color: var(--ink-muted);
  opacity: 0;
  animation: dgGridFade 0.9s ease-out 0.1s forwards, dgGridDrift 14s linear infinite;
}}
@keyframes dgGridFade {{ to {{ opacity: 0.18; }} }}
@keyframes dgGridDrift {{
  from {{ transform: translate(0,0); }}
  to   {{ transform: translate(-6px, -6px); }}
}}

.dg-node.accent {{
  filter: drop-shadow(0 0 1.4px var(--accent)) drop-shadow(0 0 2.8px var(--accent));
  transform-origin: center;
  transform-box: fill-box;
  animation: dgPulse 1.6s ease-in-out 0.6s infinite;
}}
.dg-edge.accent {{
  filter: drop-shadow(0 0 0.8px var(--accent));
}}
@keyframes dgPulse {{
  0%, 100% {{ transform: scale(1.00); }}
  50%      {{ transform: scale(1.05); }}
}}

.dg-particle {{
  fill: var(--ink-muted);
  opacity: 0;
}}
.dg-particle.accent {{
  fill: var(--accent);
  filter: drop-shadow(0 0 1.4px var(--accent)) drop-shadow(0 0 2.4px var(--accent));
}}

/* ---- flash ---- */
.scene[data-tpl="flash"] {{ background: var(--accent); }}
.flash-word {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 14cqw;
  line-height: 1;
  letter-spacing: var(--tracking);
  color: var(--canvas);
}}
.flash-caption {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.7cqw;
  max-width: 74%;
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
  color: var(--accent-ink);
  font-variant-numeric: tabular-nums;
  text-align: center;
}}
.bn-caption {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 3.6cqw;
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
  font-size: 2.7cqw;
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
  width: 94%;
  height: 64%;
  padding: 2.5cqw 2cqw 3cqw 2cqw;
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
  font-size: 1.9cqw;
  color: var(--ink-muted);
  margin-left: 1cqw;
  letter-spacing: 0;
  text-transform: none;
}}
.terminal-body {{
  flex: 1;
  font-family: var(--mono);
  font-size: 5.6cqw;
  line-height: 1.6;
  color: var(--ink);
  text-align: left;
  letter-spacing: 0;
  text-transform: none;
}}
.terminal-line {{ display: block; opacity: 0; white-space: pre; }}
.terminal-line.accent {{ color: var(--accent-ink); }}
.terminal-line .prompt {{ color: var(--accent-ink); margin-right: 0.6cqw; }}
.terminal-cursor {{
  display: inline-block;
  width: 0.55em;
  height: 1.0em;
  background: var(--ink);
  vertical-align: -0.12em;
  margin-left: 0.2em;
  animation: blink 1.06s ease-in-out infinite;
}}
@keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.12; }} }}

/* ---- split ---- */
.scene[data-tpl="split"] {{ padding: 0; flex-direction: row; align-items: stretch; justify-content: stretch; }}
.split-pane {{
  flex: 1 1 50%;
  min-height: 100%;
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
  font-size: 2.2cqw;
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

/* ---- logo_reveal ---- */
.lr-wrap {{ position: relative; display: inline-block; overflow: hidden; padding: 0.1em 0.14em; }}
.lr-word {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 16cqw;
  line-height: 1.0;
  letter-spacing: var(--tracking);
  color: var(--ink);
}}
.lr-rule {{
  height: calc(var(--rule) + 1px);
  background: var(--accent);
  width: 0;
  margin: 2.8cqw auto 0;
}}
.lr-tagline {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.6cqw;
  color: var(--ink-muted);
  margin-top: 2.6cqw;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  opacity: 0;
}}

/* ---- sparkline ---- */
.scene[data-tpl="sparkline"] {{ padding: 7%; }}
.sp-eyebrow {{
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 2.2cqw;
  letter-spacing: 0.34em;
  color: var(--ink-muted);
  text-transform: uppercase;
  margin-bottom: 2.4cqw;
  opacity: 0;
}}
.sp-svg {{ width: 88%; height: 46%; overflow: visible; display: block; }}
.sp-area {{ opacity: 0; }}
.sp-path {{
  fill: none;
  stroke: var(--accent);
  stroke-width: 1.1;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 0 1.6px var(--accent));
}}
.sp-dot {{
  fill: var(--accent);
  filter: drop-shadow(0 0 2.2px var(--accent)) drop-shadow(0 0 4.4px var(--accent));
  opacity: 0;
}}
.sp-value {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 12cqw;
  line-height: 1;
  letter-spacing: -0.03em;
  color: var(--ink);
  margin-top: 2.2cqw;
  opacity: 0;
}}
.sp-caption {{
  font-family: var(--body);
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 2.8cqw;
  color: var(--ink-muted);
  margin-top: 1.4cqw;
  opacity: 0;
  text-transform: none;
}}

/* ---- word_cascade ---- */
.wc-word {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  line-height: 1.04;
  letter-spacing: var(--tracking);
  color: var(--ink);
  margin: 0.5cqw 0;
  opacity: 0;
}}
.wc-word.size-l {{ font-size: 9.6cqw; }}
.wc-word.size-m {{ font-size: 7.4cqw; }}
.wc-word.accent {{ color: var(--accent-ink); }}

/* ---- wire_dispatch ---- */
.scene[data-tpl="wire_dispatch"] {{
  align-items: flex-start;
  justify-content: center;
  text-align: left;
  padding: 9%;
}}
.wd-tickerbar {{
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1.4cqw;
  border-top: var(--rule) solid var(--ink);
  border-bottom: 1px solid var(--hairline);
  padding: 1.4cqw 0;
  opacity: 0;
}}
.wd-square {{
  width: 1.3cqw; height: 1.3cqw;
  background: var(--accent);
  animation: blink 1.1s steps(2) infinite;
}}
.wd-ticker {{
  font-family: var(--mono);
  font-size: 1.9cqw;
  letter-spacing: 0.22em;
  color: var(--ink-muted);
  text-transform: uppercase;
  white-space: nowrap;
}}
.wd-dateline {{
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 2.1cqw;
  letter-spacing: 0.34em;
  color: var(--accent-ink);
  text-transform: uppercase;
  margin-top: 6cqw;
  opacity: 0;
}}
.wd-headline {{
  font-family: var(--display);
  font-weight: var(--display-weight);
  font-variation-settings: "wght" var(--display-weight);
  font-size: 8.4cqw;
  line-height: 1.04;
  letter-spacing: var(--tracking);
  color: var(--ink);
  margin-top: 2.2cqw;
  max-width: 92%;
}}
.wd-headline .kword {{ opacity: 0; will-change: transform, opacity; }}
.wd-lede {{
  font-family: var(--italic);
  font-style: {italic_descriptors};
  font-weight: var(--body-weight);
  font-variation-settings: "wght" var(--body-weight);
  font-size: 3.0cqw;
  line-height: 1.5;
  color: var(--ink-muted);
  margin-top: 3.4cqw;
  max-width: 78%;
  opacity: 0;
  text-transform: none;
}}


/* ---- panes (live multi-agent session illustration) ---- */
.scene[data-tpl="panes"] {{ padding: 6%; }}
.panes-eyebrow {{
  font-family: var(--body);
  font-weight: 600;
  font-variation-settings: "wght" 600;
  font-size: 2.7cqw;
  letter-spacing: 0.34em;
  color: var(--muted-content);
  text-transform: uppercase;
  margin-bottom: 2.2cqw;
  opacity: 0;
}}
.panes-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-auto-rows: 1fr;
  gap: 2.0cqw;
  width: 92%;
  min-height: 58%;
}}
.panes-grid.n2 {{ grid-template-columns: 1fr; width: 74%; }}
.pane {{
  background: {pane_bg};
  border: 1px solid var(--hairline);
  border-radius: 6px;
  padding: 3.0cqw 3.0cqw;
  text-align: left;
  opacity: 0;
  position: relative;
  overflow: hidden;
}}
.pane-head {{
  display: flex;
  align-items: center;
  gap: 1cqw;
  margin-bottom: 1.3cqw;
}}
.pane-dot {{
  width: 1.15cqw; height: 1.15cqw;
  border-radius: 50%;
  background: var(--state-color, var(--ink-muted));
  animation: panePulse 1.5s ease-in-out infinite;
}}
@keyframes panePulse {{
  0%, 100% {{ opacity: 1;    transform: scale(1); }}
  50%      {{ opacity: 0.45; transform: scale(1.45); }}
}}
.pane-name {{
  font-family: var(--mono);
  font-size: 2.7cqw;
  color: var(--ink);
  letter-spacing: 0.04em;
  text-transform: none;
  white-space: nowrap;
  flex-shrink: 0;
}}
.pane-badge {{
  margin-left: auto;
  font-family: var(--mono);
  font-size: 2.1cqw;
  white-space: nowrap;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--state-color, var(--ink-muted));
}}
.pane-line {{
  font-family: var(--mono);
  font-size: 2.7cqw;
  line-height: 1.6;
  color: var(--muted-content);
  display: block;
  opacity: 0;
  white-space: pre;
  text-transform: none;
}}
.pane.flipped {{
  border-color: var(--state-color);
  animation: paneShake 0.28s ease-out;
}}
@keyframes paneShake {{
  0% {{ transform: translateX(0); }}
  30% {{ transform: translateX(-0.5%); }}
  60% {{ transform: translateX(0.4%); }}
  100% {{ transform: translateX(0); }}
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
    cam_dur = dur + 1.2 if idx == 0 else dur  # scene 0 cold-opens 1.2s in
    extra_attrs = f' data-cam="{cam}" style="--scene-dur: {cam_dur}s;"'

    if tpl == "title":
        head_html, _ = kinetic_spans(scene["headline"])
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="title"{extra_attrs}>
  <div class="t-headline" data-kinetic="1">{head_html}</div>
  <div class="eyebrow-small">{esc(scene['eyebrow'])}</div>
  {sheen_div(scene)}
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

        node_w = 30.0
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

        particles_svg = ""
        for i, e in enumerate(edges):
            if e.get("style") == "dashed":
                continue
            cls = "dg-particle"
            if e.get("accent"):
                cls += " accent"
            # 2 staggered particles per edge so the flow reads as a stream not a single dot
            for k in range(2):
                particles_svg += (
                    f'<circle class="{cls}" data-edge="{i}" data-phase="{k*0.5:.2f}" '
                    f'r="1.4" cx="0" cy="0" />'
                )

        return f"""
<section class="scene" data-idx="{idx}" data-tpl="diagram"{extra_attrs}>
  {eyebrow_div}
  <svg class="diagram-svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
    <defs>
      <filter id="dgGlow{idx}" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="0.9" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <pattern id="dgGrid{idx}" x="0" y="0" width="6" height="6" patternUnits="userSpaceOnUse">
        <path d="M 6 0 L 0 0 0 6" fill="none" stroke="currentColor" stroke-width="0.12" />
      </pattern>
    </defs>
    <rect class="dg-grid" x="0" y="0" width="100" height="100" fill="url(#dgGrid{idx})" />
    <g class="dg-edges">{edges_svg}</g>
    <g class="dg-nodes">{nodes_svg}</g>
    <g class="dg-particles">{particles_svg}</g>
  </svg>
</section>"""

    if tpl == "flash":
        caption_html = (
            f"""<div class="flash-caption">{esc(scene['caption'])}</div>"""
            if scene.get("caption")
            else ""
        )
        word_html, _ = kinetic_spans(scene["word"])
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="flash"{extra_attrs}>
  <div class="flash-word" data-kinetic="1">{word_html}</div>
  {caption_html}
</section>"""

    if tpl == "big_number":
        sub_html = (
            f"""<div class="bn-sub">{esc(scene['sub'])}</div>"""
            if scene.get("sub")
            else ""
        )
        # Leading integer counts up on reveal; suffix (k, MB, /day) stays fixed.
        import re as _re
        m = _re.match(r"^(\d[\d,]*)(.*)$", scene["numeral"])
        count_attrs = ""
        if m and len(m.group(1).replace(",", "")) <= 6:
            count_attrs = (
                f' data-count="{m.group(1).replace(",", "")}"'
                f' data-suffix="{esc(m.group(2))}"'
                f' data-grouped="{1 if "," in m.group(1) else 0}"'
            )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="big_number"{extra_attrs}>
  <div class="bn-numeral"{count_attrs}>{esc(scene['numeral'])}</div>
  <div class="bn-caption">{esc(scene['caption'])}</div>
  {sub_html}
</section>"""

    if tpl == "terminal":
        title = scene.get("title", "")
        lines = scene["lines"]
        accent_idx = scene.get("accent_idx", -1)
        # REPL-accurate prompt: Claude Code sessions prompt with ">", a shell
        # with "$". Spec sets prompt_char to match the tool being shown.
        prompt_char = scene.get("prompt_char", "$")

        def render_line(i, line):
            text = line["text"] if isinstance(line, dict) else line
            show_prompt = line.get("prompt", True) if isinstance(line, dict) else True
            line_accent = i == accent_idx or (isinstance(line, dict) and line.get("accent"))
            classes = "terminal-line" + (" accent" if line_accent else "")
            prompt_html = f'<span class="prompt">{esc(prompt_char)}</span>' if show_prompt else ""
            cursor_html = '<span class="terminal-cursor"></span>' if i == len(lines) - 1 else ""
            # Prompt lines type on character by character; output lines fade in whole.
            typed = ' data-typed="1"' if show_prompt else ""
            return (
                f'<span class="{classes}">{prompt_html}'
                f'<span class="ttext"{typed} data-full="{esc(text)}">{esc(text)}</span>'
                f'{cursor_html}</span>'
            )

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

    if tpl == "logo_reveal":
        word_html, _ = kinetic_spans(scene["word"])
        tagline_html = (
            f"""<div class="lr-tagline">{esc(scene['tagline'])}</div>"""
            if scene.get("tagline")
            else ""
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="logo_reveal"{extra_attrs}>
  <div class="lr-wrap">
    <div class="lr-word" data-kinetic="1">{word_html}</div>
    {sheen_div(scene)}
  </div>
  <div class="lr-rule"></div>
  {tagline_html}
</section>"""

    if tpl == "sparkline":
        line_d, area_d, (ex, ey) = sparkline_geometry(scene["values"])
        eyebrow_html = (
            f"""<div class="sp-eyebrow">{esc(scene['eyebrow'])}</div>"""
            if scene.get("eyebrow")
            else ""
        )
        caption_html = f"""<div class="sp-caption">{esc(scene['caption'])}</div>"""
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="sparkline"{extra_attrs}>
  {eyebrow_html}
  <svg class="sp-svg" viewBox="0 0 100 56" preserveAspectRatio="none">
    <defs>
      <linearGradient id="spFill{idx}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.28"/>
        <stop offset="100%" stop-color="var(--accent)" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <path class="sp-area" d="{area_d}" fill="url(#spFill{idx})"/>
    <path class="sp-path" d="{line_d}" pathLength="1000"
          stroke-dasharray="1000" stroke-dashoffset="1000"/>
    <circle class="sp-dot" cx="{ex}" cy="{ey}" r="1.7"/>
  </svg>
  <div class="sp-value">{esc(scene['value_label'])}</div>
  {caption_html}
</section>"""

    if tpl == "word_cascade":
        words = scene["words"]
        accent_idx = scene.get("accent_idx", -1)
        maxlen = max(len(w) for w in words)
        size_class = "size-m" if (maxlen > 10 or len(words) > 4) else "size-l"
        words_html = "".join(
            f"""<div class="wc-word {size_class}{' accent' if i == accent_idx else ''}">{esc(w)}</div>"""
            for i, w in enumerate(words)
        )
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="word_cascade"{extra_attrs}>
  {words_html}
</section>"""

    if tpl == "wire_dispatch":
        head_html, _ = word_spans(scene["headline"])
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="wire_dispatch"{extra_attrs}>
  <div class="wd-tickerbar">
    <div class="wd-square"></div>
    <div class="wd-ticker" data-typed="1" data-full="{esc(scene['ticker'])}">{esc(scene['ticker'])}</div>
  </div>
  <div class="wd-dateline">{esc(scene['dateline'])}</div>
  <div class="wd-headline" data-wordstagger="1">{head_html}</div>
  <div class="wd-lede">{esc(scene['lede'])}</div>
</section>"""


    if tpl == "panes":
        panes = scene["panes"]
        state_colors = {
            "working": "#3fb950", "blocked": "#f0524f",
            "done": "#58a6ff", "idle": "#8b8b86",
        }
        eyebrow_html = (
            f"""<div class="panes-eyebrow">{esc(scene['eyebrow'])}</div>"""
            if scene.get("eyebrow") else ""
        )
        grid_class = "panes-grid n2" if len(panes) == 2 else "panes-grid"

        def pane_el(i, pn):
            state = pn.get("state", "working")
            flip_to = pn.get("flip_to", "")
            flip_at = float(pn.get("flip_at", 0.7))
            lines_html = "".join(
                f"""<span class="pane-line" data-typed="1" data-full="{esc(ln)}">{esc(ln)}</span>"""
                for ln in pn.get("lines", [])
            )
            flip_attrs = (
                f' data-flip-to="{esc(flip_to)}" data-flip-color="{state_colors.get(flip_to, "#8b8b86")}"'
                f' data-flip-at="{flip_at}"'
            ) if flip_to else ""
            return (
                f'<div class="pane" data-state="{esc(state)}"{flip_attrs} '
                f'style="--state-color: {state_colors.get(state, "#8b8b86")};">'
                f'<div class="pane-head"><div class="pane-dot"></div>'
                f'<div class="pane-name">{esc(pn["name"])}</div>'
                f'<div class="pane-badge" data-badge="{esc(state)}">{esc(state)}</div></div>'
                f'{lines_html}</div>'
            )

        panes_html = "".join(pane_el(i, pn) for i, pn in enumerate(panes))
        return f"""
<section class="scene" data-idx="{idx}" data-tpl="panes"{extra_attrs}>
  {eyebrow_html}
  <div class="{grid_class}">{panes_html}</div>
  {sheen_div(scene)}
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

    tracking_em = spec["design"].get("typography", {}).get("letter_spacing_em", -0.02)

    tl_json = json.dumps(timeline)
    return r"""
const TL = """ + tl_json + r""";
const DURATION_S = """ + str(total_s) + r""";
const FADE_IN_S = """ + f"{in_s}" + r""";
const FADE_OUT_S = """ + f"{out_s}" + r""";
const STAGGER_S = """ + f"{stagger_s}" + r""";
const Y_PX = """ + f"{y_px}" + r""";
const SCALE_FROM = """ + f"{scale_from}" + r""";
const TRACKING_EM = """ + f"{tracking_em}" + r""";
const COLD_OPEN_S = 1.2;
const EMPHASES = """ + json.dumps(emphases) + r""";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const sceneEls = $$(".scene");

let startedAt = 0;
let raf = null;

function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
function easeOutExpo(t) { return t >= 1 ? 1 : 1 - Math.pow(2, -10 * t); }
function easeOutBack(t) {
  const c1 = 1.20, c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}
function easeInOutCubic(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
function clamp01(t) { return Math.max(0, Math.min(1, t)); }

// Per-character kinetic reveal: blur-in, rise with overshoot settle.
function animChars(container, t, opts) {
  const stagger = (opts && opts.stagger) || 0.026;
  const dur = (opts && opts.dur) || 0.46;
  const delay = (opts && opts.delay) || 0.06;
  const chars = container.querySelectorAll(".klt");
  let allLanded = chars.length > 0;
  for (let i = 0; i < chars.length; i++) {
    const ci = parseFloat(chars[i].style.getPropertyValue("--ci")) || i;
    const local = t - delay - ci * stagger;
    if (local < 0) {
      chars[i].style.opacity = 0;
      chars[i].style.transform = "translateY(0.42em)";
      chars[i].style.filter = "blur(7px)";
      allLanded = false;
      continue;
    }
    const k = clamp01(local / dur);
    const eo = easeOutExpo(k);
    const eb = easeOutBack(k);
    chars[i].style.opacity = clamp01(eo * 1.15).toFixed(3);
    chars[i].style.transform = `translateY(${(0.42 * (1 - eb)).toFixed(3)}em)`;
    chars[i].style.filter = k >= 1 ? "none" : `blur(${(7 * (1 - eo)).toFixed(2)}px)`;
    if (k < 1) allLanded = false;
  }
  return allLanded;
}

// Character-count typing for elements with data-typed + data-full.
function typeText(el, t, start, cps) {
  const full = el.getAttribute("data-full") || "";
  const local = t - start;
  if (local < 0) { el.textContent = ""; return false; }
  const nchars = Math.min(full.length, Math.floor(local * (cps || 40)));
  const want = full.slice(0, nchars);
  if (el.textContent !== want) el.textContent = want;
  return nchars >= full.length;
}

// Light sweep across the scene between 52% and 82% of its runtime.
function animateSheen(el, t, dur) {
  const sheen = el.querySelector(".scene-sheen");
  if (!sheen) return;
  const k = (t / dur - 0.52) / 0.30;
  if (k < 0 || k > 1) { sheen.style.opacity = 0; return; }
  const e = easeInOutCubic(clamp01(k));
  sheen.style.opacity = (Math.sin(clamp01(k) * Math.PI) * 0.55).toFixed(3);
  sheen.style.transform = `translateX(${(-260 + 620 * e).toFixed(1)}%) skewX(-16deg)`;
}

function applySceneAnimations(idx, sceneT, dur) {
  const el = sceneEls[idx];
  // Scene 0 is the poster: it opens already 1.2s into its beat with no fade-in,
  // so frame 0 is a landed title card under muted autoplay (X thumbnail duty).
  if (idx === 0) { sceneT += COLD_OPEN_S; dur += COLD_OPEN_S; }
  // Scrub the paused camera animation to the exact scene time.
  el.style.animationDelay = `${(-sceneT).toFixed(3)}s`;
  // Entrance decelerates, exit accelerates (Material/Carbon asymmetric easing).
  let op = 1;
  if (sceneT < FADE_IN_S) op = idx === 0 ? 1 : easeOut(clamp01(sceneT / FADE_IN_S));
  else if (sceneT > dur - FADE_OUT_S) op = easeOut(clamp01((dur - sceneT) / FADE_OUT_S));
  el.style.opacity = op.toFixed(3);

  const tpl = el.dataset.tpl;
  if (tpl === "diagram") { animateDiagram(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "flash") { animateFlash(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "big_number") { animateBigNumber(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "terminal") { animateTerminal(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "split") { animateSplit(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "logo_reveal") { animateLogoReveal(el, sceneT, dur); return; }
  if (tpl === "sparkline") { animateSparkline(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "word_cascade") { animateWordCascade(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "wire_dispatch") { animateWireDispatch(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }
  if (tpl === "panes") { animatePanes(el, sceneT, dur); animateSheen(el, sceneT, dur); return; }

  const children = el.children;
  let staggerSlot = 0;
  for (let i = 0; i < children.length; i++) {
    const c = children[i];
    if (c.classList.contains("scene-sheen")) continue;
    if (c.dataset && c.dataset.kinetic) {
      // per-character container: chars animate; container itself stays visible
      c.style.opacity = 1;
      c.style.transform = "";
      animChars(c, sceneT - staggerSlot * STAGGER_S, {});
      staggerSlot++;
      continue;
    }
    const d = staggerSlot * STAGGER_S;
    staggerSlot++;
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
    const settled = easeOutBack(t);
    c.style.opacity = eased.toFixed(3);
    if (Y_PX > 0) {
      c.style.transform = `translateY(${(Y_PX * (1 - settled)).toFixed(2)}px)`;
    } else if (SCALE_FROM < 1) {
      const s = SCALE_FROM + (1 - SCALE_FROM) * settled;
      c.style.transform = `scale(${s.toFixed(3)})`;
    } else {
      c.style.transform = "";
    }
    if (c.classList.contains("divider-rule")) {
      c.style.width = `${(12 * eased).toFixed(2)}vmin`;
    }
  }
  animateSheen(el, sceneT, dur);
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

  // Phase 4: sub-shots inside the diagram (build / focus on accent edge / overview)
  if (svg && dur >= 3.5) {
    const tn = t / dur;
    let scale = 1.0, ty = 0;
    if (tn < 0.30) {
      // build-up: hold a wide framing
      scale = 1.0; ty = 0;
    } else if (tn < 0.65) {
      // focus phase: zoom toward router/core (y ~ 42 to 66 in viewBox -> push center down)
      const k = (tn - 0.30) / 0.35;
      const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      scale = 1.0 + 0.18 * e;
      ty   = -3.0 * e;
    } else {
      // overview phase: settle back wide
      const k = (tn - 0.65) / 0.35;
      const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      scale = 1.18 - 0.18 * e;
      ty   = -3.0 + 3.0 * e;
    }
    svg.style.transformOrigin = "50% 50%";
    svg.style.transform = `translateY(${ty.toFixed(2)}%) scale(${scale.toFixed(3)})`;
  }

  if (eyebrow) {
    const e = easeOut(Math.min(1, t / 0.30));
    eyebrow.style.opacity = e.toFixed(3);
    eyebrow.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
  }

  const nodeStart = eyebrow ? 0.18 : 0.04;
  const nodeStep = 0.10;
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

  const edgeStart = nodeStart + nodes.length * nodeStep + 0.06;
  const edgeStep = 0.10;
  const edgeEndOffsets = [];
  for (let i = 0; i < edges.length; i++) {
    const local = t - edgeStart - i * edgeStep;
    const dashed = edges[i].classList.contains("dashed");
    edgeEndOffsets[i] = edgeStart + i * edgeStep;
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

  // Particles: flow along each non-dashed edge after it draws on. Loop.
  const particles = el.querySelectorAll(".dg-particle");
  for (let p = 0; p < particles.length; p++) {
    const edgeIdx = parseInt(particles[p].getAttribute("data-edge"), 10);
    const phase = parseFloat(particles[p].getAttribute("data-phase") || "0");
    const edge = edges[edgeIdx];
    const startedAt = edgeEndOffsets[edgeIdx] + 0.35;
    const local = t - startedAt;
    if (!edge || local < 0) {
      particles[p].style.opacity = 0;
      continue;
    }
    const path = edge.getAttribute("d") || "";
    const m = path.match(/M\s*([\-\d.]+)\s+([\-\d.]+)\s*L\s*([\-\d.]+)\s+([\-\d.]+)/);
    if (!m) continue;
    const ax = parseFloat(m[1]), ay = parseFloat(m[2]);
    const bx = parseFloat(m[3]), by = parseFloat(m[4]);
    const period = 1.1;
    const tNorm = ((local + phase * period) % period) / period;
    const cx = ax + (bx - ax) * tNorm;
    const cy = ay + (by - ay) * tNorm;
    particles[p].setAttribute("cx", cx.toFixed(2));
    particles[p].setAttribute("cy", cy.toFixed(2));
    const fade = Math.min(1, Math.min(tNorm, 1 - tNorm) * 5);
    particles[p].style.opacity = (0.95 * fade).toFixed(3);
  }
}

function animateFlash(el, t, dur) {
  const word = el.querySelector(".flash-word");
  const cap = el.querySelector(".flash-caption");
  if (word) {
    word.style.opacity = 1;
    const e = easeOut(Math.min(1, t / 0.20));
    word.style.transform = `scale(${(0.90 + 0.10 * e).toFixed(3)})`;
    animChars(word, t, { stagger: 0.020, dur: 0.30, delay: 0.02 });
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
    // Reserve final width once so the count-up never reflows the layout.
    if (numeral.dataset.count && !numeral.dataset.wlock) {
      numeral.style.minWidth = numeral.offsetWidth + "px";
      numeral.dataset.wlock = "1";
    }
    const e = easeOut(Math.min(1, t / 0.40));
    numeral.style.opacity = e.toFixed(3);
    numeral.style.transform = `scale(${(0.92 + 0.08 * easeOutBack(Math.min(1, t / 0.40))).toFixed(3)})`;
    if (numeral.dataset.count) {
      const target = parseInt(numeral.dataset.count, 10);
      const k = easeOutExpo(clamp01((t - 0.05) / 0.90));
      let val = Math.round(target * k);
      if (k >= 1) val = target;
      const grouped = numeral.dataset.grouped === "1";
      const text = (grouped ? val.toLocaleString("en-US") : String(val)) + (numeral.dataset.suffix || "");
      if (numeral.textContent !== text) numeral.textContent = text;
    }
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

  // Prompt lines type on character-by-character; output lines fade in whole.
  const startT = 0.20;
  const stepT = 0.55;
  const cursor = el.querySelector(".terminal-cursor");
  for (let i = 0; i < lines.length; i++) {
    const local = t - startT - i * stepT;
    const ttext = lines[i].querySelector(".ttext");
    if (local < 0) {
      lines[i].style.opacity = 0;
      if (ttext && ttext.dataset.typed) ttext.textContent = "";
      continue;
    }
    const e = easeOut(Math.min(1, local / 0.18));
    lines[i].style.opacity = e.toFixed(3);
    if (ttext && ttext.dataset.typed) {
      typeText(ttext, t, startT + i * stepT + 0.05, 26);
    }
  }
  if (cursor) {
    const lastStart = startT + (lines.length - 1) * stepT;
    cursor.style.opacity = t >= lastStart ? "" : "0";
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
    panes[i].style.transform = `translateX(${((i === 0 ? -3 : 3) * (1 - easeOutBack(Math.min(1, local / 0.50)))).toFixed(2)}%)`;
  }
}

function animateLogoReveal(el, t, dur) {
  const wrap = el.querySelector(".lr-wrap");
  const word = el.querySelector(".lr-word");
  const rule = el.querySelector(".lr-rule");
  const tagline = el.querySelector(".lr-tagline");
  if (wrap) wrap.style.opacity = 1;
  let landAt = 1.0;
  if (word) {
    word.style.opacity = 1;
    const nChars = word.querySelectorAll(".klt").length;
    landAt = 0.10 + nChars * 0.030 + 0.46;
    animChars(word, t, { stagger: 0.030, dur: 0.46, delay: 0.10 });
    // Tracking settles as the word lands (Animista tracking-in).
    const k = easeOut(clamp01((t - 0.10) / (landAt - 0.10)));
    word.style.letterSpacing = `${(0.085 * (1 - k) + TRACKING_EM * k).toFixed(4)}em`;
  }
  if (rule) {
    const local = t - landAt + 0.22;
    const e = local < 0 ? 0 : easeOut(Math.min(1, local / 0.42));
    rule.style.opacity = 1;
    rule.style.width = `${(30 * e).toFixed(2)}cqw`;
  }
  if (tagline) {
    const local = t - landAt - 0.05;
    if (local < 0) { tagline.style.opacity = 0; tagline.style.transform = "translateY(8px)"; }
    else {
      const e = easeOut(Math.min(1, local / 0.45));
      tagline.style.opacity = e.toFixed(3);
      tagline.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
    }
  }
  animateSheen(el, t, dur);
}

function animateSparkline(el, t, dur) {
  const eyebrow = el.querySelector(".sp-eyebrow");
  const svg = el.querySelector(".sp-svg");
  const area = el.querySelector(".sp-area");
  const path = el.querySelector(".sp-path");
  const dot = el.querySelector(".sp-dot");
  const value = el.querySelector(".sp-value");
  const caption = el.querySelector(".sp-caption");
  if (svg) svg.style.opacity = 1;
  if (eyebrow) {
    const e = easeOut(clamp01(t / 0.32));
    eyebrow.style.opacity = e.toFixed(3);
    eyebrow.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
  }
  const drawStart = 0.10, drawDur = 1.1;
  const k = easeInOutCubic(clamp01((t - drawStart) / drawDur));
  if (path) {
    path.style.opacity = 1;
    path.style.strokeDashoffset = (1000 * (1 - k)).toFixed(1);
  }
  if (area) area.style.opacity = (0.9 * k).toFixed(3);
  if (dot) {
    const pop = easeOutBack(clamp01((k - 0.94) / 0.06));
    dot.style.opacity = k > 0.94 ? "1" : "0";
    dot.style.transformOrigin = "center";
    dot.style.transformBox = "fill-box";
    dot.style.transform = `scale(${(0.4 + 0.6 * pop).toFixed(3)})`;
  }
  const landAt = drawStart + drawDur;
  if (value) {
    // the number climbs WITH the curve: constant on-screen motion, and the
    // stat lands exactly when the line reaches its endpoint
    if (!value.dataset.vTarget) {
      const m = (value.textContent || "").match(/^([\d.]+)(.*)$/);
      value.dataset.vTarget = m ? m[1] : "";
      value.dataset.vSuffix = m ? m[2] : "";
      value.dataset.vDec = m && m[1].includes(".") ? String(m[1].split(".")[1].length) : "0";
    }
    if (t < drawStart) { value.style.opacity = 0; value.style.transform = "scale(0.94)"; }
    else {
      value.style.opacity = easeOut(clamp01((t - drawStart) / 0.35)).toFixed(3);
      const target = parseFloat(value.dataset.vTarget || "0");
      if (target > 0) {
        const shown = (target * k).toFixed(parseInt(value.dataset.vDec, 10));
        const text = shown + (value.dataset.vSuffix || "");
        if (value.textContent !== text) value.textContent = text;
      }
      const eb = easeOutBack(clamp01((t - landAt + 0.1) / 0.4));
      value.style.transform = `scale(${(0.94 + 0.06 * (t > landAt - 0.1 ? eb : 0)).toFixed(3)})`;
    }
  }
  if (caption) {
    const local = t - landAt - 0.10;
    if (local < 0) { caption.style.opacity = 0; caption.style.transform = "translateY(8px)"; }
    else {
      const e = easeOut(Math.min(1, local / 0.45));
      caption.style.opacity = e.toFixed(3);
      caption.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
    }
  }
}

function animateWordCascade(el, t, dur) {
  const words = el.querySelectorAll(".wc-word");
  const step = 0.42;
  let latest = -1;
  for (let i = 0; i < words.length; i++) {
    if (t - 0.12 - i * step >= 0) latest = i;
  }
  for (let i = 0; i < words.length; i++) {
    const local = t - 0.12 - i * step;
    if (local < 0) {
      words[i].style.opacity = 0;
      words[i].style.transform = "scale(1.45)";
      words[i].style.filter = "blur(8px)";
      continue;
    }
    const k = clamp01(local / 0.38);
    const eo = easeOutExpo(k);
    const dimmed = i < latest;
    words[i].style.opacity = (dimmed ? 0.55 : eo).toFixed(3);
    words[i].style.transform = `scale(${(1.45 - 0.45 * eo).toFixed(3)})`;
    words[i].style.filter = k >= 1 ? "none" : `blur(${(8 * (1 - eo)).toFixed(2)}px)`;
  }
}

function animateWireDispatch(el, t, dur) {
  const bar = el.querySelector(".wd-tickerbar");
  const ticker = el.querySelector(".wd-ticker");
  const dateline = el.querySelector(".wd-dateline");
  const headline = el.querySelector(".wd-headline");
  const lede = el.querySelector(".wd-lede");
  if (bar) {
    const e = easeOut(clamp01(t / 0.35));
    bar.style.opacity = e.toFixed(3);
    bar.style.transform = `translateY(${(-10 * (1 - e)).toFixed(2)}px)`;
  }
  if (ticker) typeText(ticker, t, 0.25, 30);
  if (dateline) {
    const local = t - 0.85;
    if (local < 0) { dateline.style.opacity = 0; }
    else { dateline.style.opacity = easeOut(Math.min(1, local / 0.35)).toFixed(3); }
  }
  let headLand = 1.6;
  if (headline) {
    headline.style.opacity = 1;
    const words = headline.querySelectorAll(".kword");
    headLand = 1.10 + words.length * 0.085 + 0.42;
    for (let i = 0; i < words.length; i++) {
      const local = t - 1.10 - i * 0.085;
      if (local < 0) {
        words[i].style.opacity = 0;
        words[i].style.transform = "translateY(0.55em)";
        continue;
      }
      const k = clamp01(local / 0.42);
      words[i].style.opacity = easeOut(k).toFixed(3);
      words[i].style.transform = `translateY(${(0.55 * (1 - easeOutBack(k))).toFixed(3)}em)`;
    }
  }
  if (lede) {
    const local = t - headLand;
    if (local < 0) { lede.style.opacity = 0; lede.style.transform = "translateY(10px)"; }
    else {
      const e = easeOut(Math.min(1, local / 0.5));
      lede.style.opacity = e.toFixed(3);
      lede.style.transform = `translateY(${(10 * (1 - e)).toFixed(2)}px)`;
    }
  }
}

function animatePanes(el, t, dur) {
  const eyebrow = el.querySelector(".panes-eyebrow");
  const grid = el.querySelector(".panes-grid");
  if (grid) grid.style.opacity = 1;
  if (eyebrow) {
    const e = easeOut(clamp01(t / 0.30));
    eyebrow.style.opacity = e.toFixed(3);
    eyebrow.style.transform = `translateY(${(8 * (1 - e)).toFixed(2)}px)`;
  }
  const panes = el.querySelectorAll(".pane");
  for (let i = 0; i < panes.length; i++) {
    const start = 0.18 + i * 0.22;
    const local = t - start;
    const pane = panes[i];
    if (local < 0) {
      pane.style.opacity = 0;
      pane.style.transform = "translateY(3%) scale(0.97)";
    } else {
      const k = clamp01(local / 0.42);
      pane.style.opacity = easeOut(k).toFixed(3);
      const eb = easeOutBack(k);
      pane.style.transform = `translateY(${(3 * (1 - eb)).toFixed(2)}%) scale(${(0.97 + 0.03 * eb).toFixed(3)})`;
    }
    // typed activity lines inside each pane, staggered so something is
    // always typing somewhere in the grid
    const lines = pane.querySelectorAll(".pane-line");
    for (let j = 0; j < lines.length; j++) {
      const lineStart = start + 0.35 + j * 0.5 + i * 0.30;
      lines[j].style.opacity = t - lineStart < 0 ? 0 : 1;
      typeText(lines[j], t, lineStart, 17);
    }
    // the state flip: a pane changes status mid-scene (the product moment)
    const flipTo = pane.dataset.flipTo;
    if (flipTo) {
      const flipT = parseFloat(pane.dataset.flipAt || "0.7") * dur;
      const badge = pane.querySelector(".pane-badge");
      if (t >= flipT) {
        if (!pane.classList.contains("flipped")) pane.classList.add("flipped");
        pane.style.setProperty("--state-color", pane.dataset.flipColor);
        if (badge && badge.textContent !== flipTo) badge.textContent = flipTo;
      } else {
        pane.classList.remove("flipped");
        pane.style.removeProperty("--state-color");
        if (badge && badge.textContent !== badge.dataset.badge) badge.textContent = badge.dataset.badge;
      }
    }
  }
}

function hideScene(i) {
  const el = sceneEls[i];
  el.style.opacity = 0;
  el.style.animationDelay = "0s";
  walkReset(el);
}
function walkReset(node) {
  // Reset DIRECT children only. Every template animator fully re-derives its
  // deep element state from scene time each frame (including t<0), so deep
  // resets are redundant -- and recursing zeroed nested text wrappers
  // (.kword, .ttext, .prompt) that no animator restores, leaving their glyphs
  // permanently transparent in the capture.
  for (let k = 0; k < node.children.length; k++) {
    const c = node.children[k];
    c.style.opacity = 0;
    c.style.transform = "";
    c.style.filter = "";
    if (c.classList.contains("divider-rule")) c.style.width = "0";
    if (c.dataset && c.dataset.typed) c.textContent = "";
  }
}

// ---- Phase 4: chromatic aberration on scene boundaries + emphasize flash ----
const SCENE_BOUNDARIES = TL.slice(1).map(s => s.start);
let lastSceneIdx = -1;
const CUT_FILTER_MS = 180;
const stageEl = document.getElementById("stage");
const empFlashEl = document.querySelector(".emphasize-flash");
const heldEl = document.querySelector(".held-subject");

function fireChromCut() {
  if (!stageEl) return;
  stageEl.classList.add("chrom-cut");
  setTimeout(() => stageEl.classList.remove("chrom-cut"), CUT_FILTER_MS);
}
function fireEmphasizeFlash() {
  if (!empFlashEl) return;
  empFlashEl.classList.remove("fire");
  // force reflow so the animation re-runs
  void empFlashEl.offsetWidth;
  empFlashEl.classList.add("fire");
}

function tick() {
  const t = (performance.now() - startedAt) / 1000;
  const clamped = Math.min(t, DURATION_S);
  let activeIdx = -1;
  for (let i = 0; i < TL.length; i++) {
    const sc = TL[i];
    if (clamped < sc.start || clamped >= sc.end) {
      hideScene(i);
    } else {
      activeIdx = i;
      applySceneAnimations(i, clamped - sc.start, sc.end - sc.start);
    }
  }

  if (activeIdx !== -1 && activeIdx !== lastSceneIdx) {
    if (lastSceneIdx !== -1) {
      // scene boundary detected: flash chromatic aberration on the cut
      fireChromCut();
    }
    if (activeIdx >= 0 && TL[activeIdx] && TL[activeIdx].emphasize) {
      fireEmphasizeFlash();
    }
    lastSceneIdx = activeIdx;
  }

  // Held-subject wordmark: appears after the title beat, hides on accent-bg flash scenes.
  if (heldEl && TL.length > 1) {
    const activeTpl = activeIdx >= 0 ? TL[activeIdx].tpl : "";
    const show = clamped >= TL[0].end - 0.25 && activeTpl !== "flash";
    heldEl.style.opacity = show ? 0.62 : 0;
  }

  if (t < DURATION_S) raf = requestAnimationFrame(tick);
}

// ---- Phase 4: particle background canvas (parallax depth, accent-tinted) ----
function startParticleBackground() {
  const canvas = document.getElementById("bgParticles");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#ffffff";
  const inkMuted = getComputedStyle(document.documentElement).getPropertyValue("--ink-muted").trim() || "#888";

  function fit() {
    const r = canvas.getBoundingClientRect();
    canvas.width = Math.floor(r.width * dpr);
    canvas.height = Math.floor(r.height * dpr);
  }
  fit();
  window.addEventListener("resize", fit);

  const PARTICLE_COUNT = 220;
  const ACCENT_RATIO = 0.18;
  const particles = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const depth = Math.random();
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * (0.10 + depth * 0.40),
      vy: (Math.random() - 0.5) * (0.10 + depth * 0.40),
      r: (0.5 + depth * 1.8) * dpr,
      depth: depth,
      isAccent: Math.random() < ACCENT_RATIO,
      tw: Math.random() * Math.PI * 2,
    });
  }

  function pf() {
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.tw += 0.03 + p.depth * 0.04;
      if (p.x < -8) p.x = w + 8;
      if (p.x > w + 8) p.x = -8;
      if (p.y < -8) p.y = h + 8;
      if (p.y > h + 8) p.y = -8;
      const twinkle = 0.55 + 0.45 * (Math.sin(p.tw) * 0.5 + 0.5);
      const baseAlpha = (0.12 + p.depth * 0.55) * twinkle;
      ctx.beginPath();
      ctx.fillStyle = p.isAccent ? accent : inkMuted;
      ctx.globalAlpha = baseAlpha;
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
      if (p.isAccent && p.depth > 0.7) {
        ctx.globalAlpha = baseAlpha * 0.35;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * 3.2, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(pf);
  }
  requestAnimationFrame(pf);
}
startParticleBackground();

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
      // resume() never settles under a blocked autoplay policy; race a timeout
      // so the visual timeline can never hang on audio permission.
      try {
        await Promise.race([audioCtx.resume(), new Promise(r => setTimeout(r, 400))]);
      } catch (e) {}
      if (audioCtx.state === "running") {
        scheduleScore(audioCtx.currentTime + 0.15);
      }
    }
  }
  startedAt = performance.now() + 150;
  // absolute epoch-ms of animation t=0, so the recorder can trim exactly
  window.__bvT0abs = performance.timeOrigin + startedAt;
  setTimeout(() => { raf = requestAnimationFrame(tick); }, 150);
}

// Wait for fonts so the first paint isn't unstyled.
if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(() => requestAnimationFrame(() => requestAnimationFrame(play)));
} else {
  requestAnimationFrame(() => requestAnimationFrame(play));
}
"""

def build_html(spec):
    timeline, total_s, emphases = build_timeline(spec)
    css = build_css(spec)
    scenes_html = "\n".join(render_scene(i, sc) for i, sc in enumerate(spec["scenes"]))
    js = build_js(spec, timeline, total_s, emphases)

    bg_html = background_html(spec)
    held = spec["design"].get("held_subject")
    held_html = f'<div class="held-subject">{esc(held)}</div>' if held else ""

    title_text = spec.get("topic") or spec["scenes"][0].get("headline") or "video"

    audio_palette = spec["design"].get("audio_palette", "ambient")
    framework = spec["design"].get("framework", None)

    bv_meta = json.dumps({
        "total_s": total_s,
        "timeline": timeline,
        "emphases": emphases,
        "audio_palette": audio_palette,
        "framework": framework,
    })

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
  {bg_html}
  <div class="stage-inner">
{scenes_html}
  </div>
  {held_html}
  <div class="lighting-arc"><div class="la-warm"></div><div class="la-cool"></div></div>
  <div class="emphasize-flash" aria-hidden="true"></div>
  <div class="texture">
    <div class="texture-grain"></div>
    <div class="texture-vignette"></div>
  </div>
  <svg class="bv-defs" aria-hidden="true" width="0" height="0">
    <defs>
      <filter id="bvChromAb" x="-5%" y="-5%" width="110%" height="110%">
        <feColorMatrix in="SourceGraphic" result="r" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"/>
        <feColorMatrix in="SourceGraphic" result="g" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0"/>
        <feColorMatrix in="SourceGraphic" result="b" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0"/>
        <feOffset in="r" dx="3.5" dy="0" result="rOff"/>
        <feOffset in="b" dx="-3.5" dy="0" result="bOff"/>
        <feBlend in="rOff" in2="g" mode="screen" result="rg"/>
        <feBlend in="rg" in2="bOff" mode="screen"/>
      </filter>
    </defs>
  </svg>
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
