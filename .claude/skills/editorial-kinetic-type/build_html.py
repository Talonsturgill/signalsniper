#!/usr/bin/env python3
"""
editorial-kinetic-type HTML builder.

Reads a scene-spec.json and emits a single self-contained HTML file
that plays the 25-second editorial kinetic-typography video in any
modern browser. CSS animations drive the typography, Web Audio API
drives the soundtrack, no external assets.

Two variant axes (selected per build):

    motion_variant  ∈ {rise, lateral, drop, cascade, stack, split}
    audio_variant   ∈ {ambient, minimal, warm}

Defaults are rise + ambient (the original v1 behavior). Variants can
be supplied via CLI flags or inside the scene spec under the
"motion_variant" / "audio_variant" keys.

Usage:
    python build_html.py <spec.json> <output.html>
        [--theme theme.json]
        [--motion-variant rise|lateral|drop|cascade|stack|split]
        [--audio-variant  ambient|minimal|warm]
"""

import argparse
import json
from pathlib import Path


SCENE_DURATIONS_S = {
    "title": 3.0,
    "three_things": 3.0,
    "problem": 3.0,
    "specific_case": 3.0,
    "fix": 3.0,
    "mechanism": 3.0,
    "consequence": 3.0,
    "close": 4.0,
}
TOTAL_S = sum(SCENE_DURATIONS_S.values())  # 25.0

MOTION_VARIANTS = ("rise", "lateral", "drop", "cascade", "stack", "split")
AUDIO_VARIANTS = ("ambient", "minimal", "warm")


def scene_starts():
    starts = {}
    cursor = 0.0
    for name, dur in SCENE_DURATIONS_S.items():
        starts[name] = (cursor, cursor + dur)
        cursor += dur
    return starts


STARTS = scene_starts()


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def resolve_theme(spec, theme_arg):
    if theme_arg:
        return json.loads(Path(theme_arg).read_text())
    if isinstance(spec.get("theme"), dict):
        return spec["theme"]
    default_path = Path(__file__).parent / "default_theme.json"
    return json.loads(default_path.read_text())


# ===================================================================
# CSS
# ===================================================================

# Per-motion-variant alignment overrides. Type sizes never vary —
# only where the lines sit on the canvas does.
VARIANT_ALIGN_CSS = {
    "rise": "",  # default centered, no overrides
    "lateral": """
.scene[data-scene="title"]         { align-items: flex-start; text-align: left; padding-left: 11%; }
.scene[data-scene="three_things"]  { align-items: flex-start; text-align: left; padding-left: 11%; }
.scene[data-scene="mechanism"]     { align-items: flex-start; text-align: left; padding-left: 11%; }
.scene[data-scene="close"]         { align-items: flex-end;   text-align: right; padding-right: 11%; }
""",
    "drop": "",  # default centered
    "cascade": """
.scene { align-items: flex-start; text-align: left; padding-left: 11%; }
.tt-rule { margin-left: 0; margin-right: auto; }
""",
    "stack": """
.scene { justify-content: flex-end; padding-bottom: 22%; }
""",
    "split": "",  # default centered
}


def build_css(theme, motion_variant):
    base = f"""
:root {{
  --bg: {theme['background']};
  --ink: {theme['ink']};
  --accent: {theme['accent']};
  --muted: {theme['muted']};
  --rule: {theme['rule']};
  --serif: {theme['serif']};
  --sans: {theme['sans']};
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  background: #0d0d0e;
  color: var(--ink);
  font-family: var(--serif);
  height: 100%;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
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
  background: var(--bg);
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 30px 80px -30px rgba(0,0,0,0.5),
              0 0 0 1px rgba(255,255,255,0.04);
}}

.canvas {{
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
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
  padding: 8%;
}}
.scene.active {{ pointer-events: auto; }}

.headline {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 10.2cqw;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: var(--ink);
}}
.eyebrow-small {{
  font-family: var(--sans);
  font-weight: 400;
  font-size: 3cqw;
  color: var(--muted);
  margin-top: 2.4cqw;
}}
.tt-eyebrow {{
  font-family: var(--sans);
  font-weight: 600;
  font-size: 2.4cqw;
  letter-spacing: 0.36em;
  color: var(--accent);
  text-transform: uppercase;
}}
.tt-rule {{
  height: 2px;
  background: var(--rule);
  margin: 1.6cqw auto 5cqw;
  width: 0;
}}
.tt-item {{ margin: 1cqw 0; }}
.tt-name {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 5.9cqw;
  line-height: 1.1;
  color: var(--ink);
}}
.tt-descriptor {{
  font-family: var(--sans);
  font-style: italic;
  font-size: 2.05cqw;
  color: var(--muted);
  margin-top: 0.4cqw;
}}
.problem-line {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 8.9cqw;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: var(--ink);
  margin: 0.6cqw 0;
}}
.problem-line.accent {{ color: var(--accent); }}
.case-line {{
  font-family: var(--serif);
  font-weight: 400;
  font-size: 5.9cqw;
  line-height: 1.15;
  color: var(--ink);
  margin: 0.6cqw 0;
}}
.case-line.accent {{ color: var(--accent); font-weight: 700; }}
.fix-primary {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 13cqw;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--ink);
  display: inline-block;
}}
.fix-primary .ch {{ display: inline-block; white-space: pre; opacity: 0; }}
.fix-secondary {{
  font-family: var(--serif);
  font-style: italic;
  font-size: 5.9cqw;
  color: var(--muted);
  margin-top: 4cqw;
}}
.mech-line {{
  font-family: var(--serif);
  font-weight: 400;
  font-size: 5.2cqw;
  line-height: 1.1;
  color: var(--ink);
  margin: 0.6cqw 0;
}}
.mech-line.accent {{
  font-weight: 700;
  font-size: 6.7cqw;
  color: var(--accent);
}}
.cons-a {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 6.5cqw;
  line-height: 1.1;
  color: var(--ink);
}}
.cons-b {{
  font-family: var(--serif);
  font-weight: 400;
  font-size: 5.2cqw;
  line-height: 1.15;
  color: var(--ink);
  margin-top: 1.2cqw;
}}
.cons-c {{
  font-family: var(--serif);
  font-style: italic;
  font-size: 5.2cqw;
  line-height: 1.15;
  color: var(--muted);
  margin-top: 1.2cqw;
}}
.close-primary {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 9.3cqw;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--ink);
}}
.close-accent {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 9.3cqw;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--accent);
  margin-top: 2cqw;
}}
.close-subtitle {{
  font-family: var(--sans);
  font-style: italic;
  font-size: 2.4cqw;
  color: var(--muted);
  margin-top: 4.6cqw;
}}

.controls {{
  display: flex;
  align-items: center;
  gap: 12px;
  width: min(86vmin, calc(100vh - 100px));
  color: rgba(255,255,255,0.55);
  font-family: var(--sans);
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

.stage {{ container-type: inline-size; container-name: stage; }}
@container stage (min-width: 0px) {{
  .headline {{ font-size: 10.2cqw; }}
}}
"""
    return base + VARIANT_ALIGN_CSS[motion_variant]


# ===================================================================
# Scene HTML
# ===================================================================

def build_scene_html(spec):
    s = spec["scenes"]
    parts = []

    parts.append(f"""
<section class="scene" data-scene="title">
  <div class="headline">{esc(s['title']['headline'])}</div>
  <div class="eyebrow-small">{esc(s['title']['eyebrow'])}</div>
</section>""")

    items_html = "".join(
        f"""<div class="tt-item">
        <div class="tt-name">{esc(item['name'])}</div>
        <div class="tt-descriptor">{esc(item['descriptor'])}</div>
      </div>"""
        for item in s["three_things"]["items"]
    )
    parts.append(f"""
<section class="scene" data-scene="three_things">
  <div class="tt-eyebrow">{esc(s['three_things']['eyebrow'])}</div>
  <div class="tt-rule"></div>
  {items_html}
</section>""")

    p = s["problem"]
    accent_a = " accent" if p.get("accent_line") == "a" else ""
    accent_b = " accent" if p.get("accent_line") == "b" else ""
    parts.append(f"""
<section class="scene" data-scene="problem">
  <div class="problem-line{accent_a}">{esc(p['line_a'])}</div>
  <div class="problem-line{accent_b}">{esc(p['line_b'])}</div>
</section>""")

    sc = s["specific_case"]
    accent = sc.get("accent_line", "b")
    parts.append(f"""
<section class="scene" data-scene="specific_case">
  <div class="case-line{' accent' if accent == 'a' else ''}">{esc(sc['line_a'])}</div>
  <div class="case-line{' accent' if accent == 'b' else ''}">{esc(sc['line_b'])}</div>
  <div class="case-line{' accent' if accent == 'c' else ''}">{esc(sc['line_c'])}</div>
</section>""")

    fx = s["fix"]
    parts.append(f"""
<section class="scene" data-scene="fix">
  <div class="fix-primary" data-text="{esc(fx['primary'])}">{esc(fx['primary'])}</div>
  <div class="fix-secondary">{esc(fx['secondary'])}</div>
</section>""")

    mc = s["mechanism"]
    m_accent = mc.get("accent_line", "c")
    parts.append(f"""
<section class="scene" data-scene="mechanism">
  <div class="mech-line{' accent' if m_accent == 'a' else ''}">{esc(mc['line_a'])}</div>
  <div class="mech-line{' accent' if m_accent == 'b' else ''}">{esc(mc['line_b'])}</div>
  <div class="mech-line{' accent' if m_accent == 'c' else ''}">{esc(mc['line_c'])}</div>
</section>""")

    cn = s["consequence"]
    parts.append(f"""
<section class="scene" data-scene="consequence">
  <div class="cons-a">{esc(cn['line_a'])}</div>
  <div class="cons-b">{esc(cn['line_b'])}</div>
  <div class="cons-c">{esc(cn['line_c'])}</div>
</section>""")

    cl = s["close"]
    parts.append(f"""
<section class="scene" data-scene="close">
  <div class="close-primary">{esc(cl['primary'])}</div>
  <div class="close-accent">{esc(cl['accent'])}</div>
  <div class="close-subtitle">{esc(cl['subtitle'])}</div>
</section>""")

    return "\n".join(parts)


# ===================================================================
# JS
# ===================================================================

# The runtime ships all 6 motion variants and all 3 audio variants and
# selects between them via the constants injected at build time. The
# extra ~6 KB of unused variant code per output is negligible compared
# to making the template easier to maintain and inspect.

JS_DRIVER_TEMPLATE = r"""
const MOTION_VARIANT = "__MOTION_VARIANT__";
const AUDIO_VARIANT  = "__AUDIO_VARIANT__";

const TL = [
  ["title",         0.00,  3.00],
  ["three_things",  3.00,  6.00],
  ["problem",       6.00,  9.00],
  ["specific_case", 9.00, 12.00],
  ["fix",          12.00, 15.00],
  ["mechanism",    15.00, 18.00],
  ["consequence",  18.00, 21.00],
  ["close",        21.00, 25.00],
];
const DURATION_S = 25.0;
const FADE_IN_S = 0.4;
const FADE_OUT_S = 0.27;

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const sceneEls = $$(".scene");

let startedAt = 0;
let raf = null;

const NEEDS_CHARS = ["lateral", "cascade", "stack"];
if (NEEDS_CHARS.includes(MOTION_VARIANT)) {
  // pre-split the fix-primary into per-character spans for the variants
  // that animate the headline char-by-char
  const el = document.querySelector('.fix-primary');
  if (el) {
    const text = el.dataset.text || el.textContent;
    el.textContent = "";
    for (const ch of text) {
      const span = document.createElement("span");
      span.className = "ch";
      span.textContent = ch;
      el.appendChild(span);
    }
  }
}

function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

function envelope(el, sceneT, dur) {
  let op = 1;
  if (sceneT < FADE_IN_S) op = sceneT / FADE_IN_S;
  else if (sceneT > dur - FADE_OUT_S) op = Math.max(0, (dur - sceneT) / FADE_OUT_S);
  el.style.opacity = op.toFixed(3);
}

// ---------- motion variant: rise (default) ----------
function applyRise(idx, sceneT, dur) {
  const el = sceneEls[idx];
  envelope(el, sceneT, dur);
  const name = el.dataset.scene;
  const children = el.children;
  if (name === "three_things") {
    const delays = [0, 0.1, 0.4, 0.65, 0.9];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const d = delays[i] || 0;
      const local = sceneT - d;
      if (local < 0) { c.style.opacity = 0; c.style.transform = "translateY(14px)"; continue; }
      const t = Math.min(1, local / 0.5);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = `translateY(${(14 * (1 - eased)).toFixed(2)}px)`;
      if (i === 1) c.style.width = `${(12 * eased).toFixed(2)}vmin`;
    }
  } else if (name === "fix") {
    const delays = [0, 0.55];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) { c.style.opacity = 0; continue; }
      const t = Math.min(1, local / 0.55);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      if (i === 0) {
        const scale = 0.95 + 0.05 * eased;
        c.style.transform = `scale(${scale.toFixed(3)})`;
      } else {
        c.style.transform = `translateY(${(12 * (1 - eased)).toFixed(2)}px)`;
      }
    }
  } else if (name === "mechanism" || name === "consequence" || name === "specific_case") {
    const delays = [0, 0.4, 0.95];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - (delays[i] || 0);
      if (local < 0) { c.style.opacity = 0; c.style.transform = "translateY(12px)"; continue; }
      const t = Math.min(1, local / 0.5);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = `translateY(${(12 * (1 - eased)).toFixed(2)}px)`;
    }
  } else if (name === "close") {
    const delays = [0, 0.45, 1.3];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - (delays[i] || 0);
      if (local < 0) { c.style.opacity = 0; c.style.transform = "translateY(14px)"; continue; }
      const t = Math.min(1, local / 0.6);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = `translateY(${(14 * (1 - eased)).toFixed(2)}px)`;
    }
  } else {
    const delays = [0, 0.27];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - (delays[i] || 0);
      if (local < 0) { c.style.opacity = 0; c.style.transform = "translateY(14px)"; continue; }
      const t = Math.min(1, local / 0.6);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = `translateY(${(14 * (1 - eased)).toFixed(2)}px)`;
    }
  }
}

// ---------- motion variant: lateral ----------
function applyLateral(idx, sceneT, dur) {
  const el = sceneEls[idx];
  envelope(el, sceneT, dur);
  const name = el.dataset.scene;
  const children = el.children;
  if (name === "title") {
    const delays = [0, 0.45];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) {
        c.style.opacity = 0;
        c.style.transform = i === 0 ? "translateY(24px)" : "translateX(-40px)";
        continue;
      }
      const t = Math.min(1, local / 0.6);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = i === 0
        ? `translateY(${(24 * (1 - eased)).toFixed(2)}px)`
        : `translateX(${(-40 * (1 - eased)).toFixed(2)}px)`;
    }
  } else if (name === "three_things") {
    const delays = [0, 0.15, 0.45, 0.75, 1.05];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) {
        c.style.opacity = 0;
        c.style.transform = i >= 2 ? "translateX(-60px)" : "";
        if (i === 1) c.style.width = "0vmin";
        continue;
      }
      const t = Math.min(1, local / 0.55);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      if (i === 1) c.style.width = `${(14 * eased).toFixed(2)}vmin`;
      else if (i >= 2) c.style.transform = `translateX(${(-60 * (1 - eased)).toFixed(2)}px)`;
    }
  } else if (name === "problem") {
    const delays = [0, 0.4];
    const fromX = [60, -60];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) { c.style.opacity = 0; c.style.transform = `translateX(${fromX[i]}px)`; continue; }
      const t = Math.min(1, local / 0.6);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = `translateX(${(fromX[i] * (1 - eased)).toFixed(2)}px)`;
    }
  } else if (name === "specific_case") {
    const delays = [0, 0.4, 0.85];
    const transforms = [
      (e) => `translateX(${(-50 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateY(${(-22 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateX(${(50 * (1 - e)).toFixed(2)}px)`,
    ];
    const init = ["translateX(-50px)", "translateY(-22px)", "translateX(50px)"];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) { c.style.opacity = 0; c.style.transform = init[i]; continue; }
      const t = Math.min(1, local / 0.55);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = transforms[i](eased);
    }
  } else if (name === "fix") {
    const primary = children[0];
    const chars = primary.querySelectorAll(".ch");
    const total = chars.length;
    const perCharDelay = 0.045;
    const charDur = 0.4;
    chars.forEach((ch, i) => {
      const local = sceneT - i * perCharDelay;
      if (local < 0) { ch.style.opacity = 0; ch.style.transform = "translateY(18px)"; return; }
      const t = Math.min(1, local / charDur);
      const eased = easeOut(t);
      ch.style.opacity = eased.toFixed(3);
      ch.style.transform = `translateY(${(18 * (1 - eased)).toFixed(2)}px)`;
    });
    primary.style.opacity = 1;
    const secondary = children[1];
    const secondaryDelay = total * perCharDelay + 0.25;
    const localS = sceneT - secondaryDelay;
    if (localS < 0) { secondary.style.opacity = 0; secondary.style.transform = "translateY(14px)"; }
    else {
      const t = Math.min(1, localS / 0.55);
      const eased = easeOut(t);
      secondary.style.opacity = eased.toFixed(3);
      secondary.style.transform = `translateY(${(14 * (1 - eased)).toFixed(2)}px)`;
    }
  } else if (name === "mechanism") {
    const delays = [0, 0.5, 1.0];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) { c.style.opacity = 0; c.style.transform = "translateX(-50px)"; continue; }
      const t = Math.min(1, local / 0.55);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      const isAccent = c.classList.contains("accent");
      if (isAccent) {
        const punchT = local - 0.55;
        let scale = 1.0;
        if (punchT >= 0 && punchT < 0.4) {
          const pt = punchT / 0.4;
          scale = 1.0 + 0.06 * Math.sin(pt * Math.PI);
        }
        c.style.transform = `translateX(${(-50 * (1 - eased)).toFixed(2)}px) scale(${scale.toFixed(3)})`;
        c.style.transformOrigin = "left center";
      } else {
        c.style.transform = `translateX(${(-50 * (1 - eased)).toFixed(2)}px)`;
      }
    }
  } else if (name === "consequence") {
    const delays = [0, 0.4, 0.85];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) { c.style.opacity = 0; c.style.transform = "translateY(-22px)"; continue; }
      const t = Math.min(1, local / 0.55);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = `translateY(${(-22 * (1 - eased)).toFixed(2)}px)`;
    }
  } else if (name === "close") {
    const delays = [0, 0.5, 1.3];
    const transforms = [
      (e) => `translateX(${(-60 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateX(${(60 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateY(${(14 * (1 - e)).toFixed(2)}px)`,
    ];
    const init = ["translateX(-60px)", "translateX(60px)", "translateY(14px)"];
    for (let i = 0; i < children.length; i++) {
      const c = children[i];
      const local = sceneT - delays[i];
      if (local < 0) { c.style.opacity = 0; c.style.transform = init[i]; continue; }
      const t = Math.min(1, local / 0.6);
      const eased = easeOut(t);
      c.style.opacity = eased.toFixed(3);
      c.style.transform = transforms[i](eased);
    }
  }
}

// ---------- motion variant: drop ----------
function applyDrop(idx, sceneT, dur) {
  const el = sceneEls[idx];
  envelope(el, sceneT, dur);
  const name = el.dataset.scene;
  const children = el.children;

  function dropLine(c, local, dur, dist) {
    if (local < 0) { c.style.opacity = 0; c.style.transform = `translateY(${-dist}px)`; return; }
    const t = Math.min(1, local / dur);
    const eased = easeOut(t);
    c.style.opacity = eased.toFixed(3);
    c.style.transform = `translateY(${(-dist * (1 - eased)).toFixed(2)}px)`;
  }

  if (name === "three_things") {
    const delays = [0, 0.12, 0.4, 0.7, 1.0];
    for (let i = 0; i < children.length; i++) {
      if (i === 1) {
        const local = sceneT - delays[i];
        if (local < 0) { children[i].style.width = "0vmin"; children[i].style.opacity = 0; continue; }
        const t = Math.min(1, local / 0.5);
        const eased = easeOut(t);
        children[i].style.opacity = eased.toFixed(3);
        children[i].style.width = `${(14 * eased).toFixed(2)}vmin`;
      } else {
        dropLine(children[i], sceneT - delays[i], 0.55, 18);
      }
    }
  } else if (name === "fix") {
    const primary = children[0];
    if (sceneT < 0) primary.style.opacity = 0;
    else {
      const t = Math.min(1, sceneT / 0.6);
      const eased = easeOut(t);
      primary.style.opacity = eased.toFixed(3);
      primary.style.transform = `scale(${(1.05 - 0.05 * eased).toFixed(3)})`;
    }
    dropLine(children[1], sceneT - 0.55, 0.55, 16);
  } else if (children.length === 2) {
    const delays = [0, 0.32];
    for (let i = 0; i < children.length; i++) dropLine(children[i], sceneT - delays[i], 0.6, 20);
  } else {
    const delays = [0, 0.4, 0.85];
    for (let i = 0; i < children.length; i++) dropLine(children[i], sceneT - delays[i], 0.55, 22);
  }
}

// ---------- motion variant: cascade ----------
function applyCascade(idx, sceneT, dur) {
  const el = sceneEls[idx];
  envelope(el, sceneT, dur);
  const name = el.dataset.scene;
  const children = el.children;

  function lineIn(c, local, dur, dist) {
    if (local < 0) { c.style.opacity = 0; c.style.transform = `translateX(${-dist}px)`; return; }
    const t = Math.min(1, local / dur);
    const eased = easeOut(t);
    c.style.opacity = eased.toFixed(3);
    c.style.transform = `translateX(${(-dist * (1 - eased)).toFixed(2)}px)`;
  }

  if (name === "three_things") {
    const delays = [0, 0.12, 0.4, 0.7, 1.0];
    for (let i = 0; i < children.length; i++) {
      if (i === 1) {
        const local = sceneT - delays[i];
        if (local < 0) { children[i].style.width = "0vmin"; children[i].style.opacity = 0; continue; }
        const t = Math.min(1, local / 0.5);
        const eased = easeOut(t);
        children[i].style.opacity = eased.toFixed(3);
        children[i].style.width = `${(14 * eased).toFixed(2)}vmin`;
      } else {
        lineIn(children[i], sceneT - delays[i], 0.55, 30);
      }
    }
  } else if (name === "fix") {
    const primary = children[0];
    const chars = primary.querySelectorAll(".ch");
    const total = chars.length;
    const perCharDelay = 0.04;
    const charDur = 0.4;
    chars.forEach((ch, i) => {
      const local = sceneT - i * perCharDelay;
      if (local < 0) { ch.style.opacity = 0; ch.style.transform = "translateX(-12px)"; return; }
      const t = Math.min(1, local / charDur);
      const eased = easeOut(t);
      ch.style.opacity = eased.toFixed(3);
      ch.style.transform = `translateX(${(-12 * (1 - eased)).toFixed(2)}px)`;
    });
    primary.style.opacity = 1;
    const secondaryDelay = total * perCharDelay + 0.2;
    lineIn(children[1], sceneT - secondaryDelay, 0.55, 24);
  } else if (children.length === 2) {
    const delays = [0, 0.32];
    for (let i = 0; i < children.length; i++) lineIn(children[i], sceneT - delays[i], 0.5, 24);
  } else {
    const delays = [0, 0.3, 0.6];
    for (let i = 0; i < children.length; i++) lineIn(children[i], sceneT - delays[i], 0.5, 24);
  }
}

// ---------- motion variant: stack ----------
function applyStack(idx, sceneT, dur) {
  const el = sceneEls[idx];
  envelope(el, sceneT, dur);
  const name = el.dataset.scene;
  const children = el.children;

  function slideUp(c, local, dur, dist) {
    if (local < 0) { c.style.opacity = 0; c.style.transform = `translateY(${dist}px)`; return; }
    const t = Math.min(1, local / dur);
    const eased = easeOut(t);
    c.style.opacity = eased.toFixed(3);
    c.style.transform = `translateY(${(dist * (1 - eased)).toFixed(2)}px)`;
  }

  if (name === "three_things") {
    const delays = [0, 0.12, 0.4, 0.7, 1.0];
    for (let i = 0; i < children.length; i++) {
      if (i === 1) {
        const local = sceneT - delays[i];
        if (local < 0) { children[i].style.width = "0vmin"; children[i].style.opacity = 0; continue; }
        const t = Math.min(1, local / 0.5);
        const eased = easeOut(t);
        children[i].style.opacity = eased.toFixed(3);
        children[i].style.width = `${(14 * eased).toFixed(2)}vmin`;
      } else {
        slideUp(children[i], sceneT - delays[i], 0.55, 24);
      }
    }
  } else if (name === "fix") {
    const primary = children[0];
    const chars = primary.querySelectorAll(".ch");
    const total = chars.length;
    const perCharDelay = 0.04;
    const charDur = 0.4;
    chars.forEach((ch, i) => {
      const local = sceneT - i * perCharDelay;
      if (local < 0) { ch.style.opacity = 0; ch.style.transform = "translateY(20px)"; return; }
      const t = Math.min(1, local / charDur);
      const eased = easeOut(t);
      ch.style.opacity = eased.toFixed(3);
      ch.style.transform = `translateY(${(20 * (1 - eased)).toFixed(2)}px)`;
    });
    primary.style.opacity = 1;
    const secondaryDelay = total * perCharDelay + 0.2;
    slideUp(children[1], sceneT - secondaryDelay, 0.55, 16);
  } else if (children.length === 2) {
    const delays = [0, 0.32];
    for (let i = 0; i < children.length; i++) slideUp(children[i], sceneT - delays[i], 0.55, 24);
  } else {
    const delays = [0, 0.4, 0.85];
    for (let i = 0; i < children.length; i++) slideUp(children[i], sceneT - delays[i], 0.55, 24);
  }
}

// ---------- motion variant: split ----------
function applySplit(idx, sceneT, dur) {
  const el = sceneEls[idx];
  envelope(el, sceneT, dur);
  const name = el.dataset.scene;
  const children = el.children;

  function applyT(c, local, durIn, init, fn) {
    if (local < 0) { c.style.opacity = 0; c.style.transform = init; return; }
    const t = Math.min(1, local / durIn);
    const eased = easeOut(t);
    c.style.opacity = eased.toFixed(3);
    c.style.transform = fn(eased);
  }

  if (name === "three_things") {
    const eyebrow = children[0];
    const rule = children[1];
    const items = [children[2], children[3], children[4]];
    applyT(eyebrow, sceneT, 0.55, "translateY(14px)",
      (e) => `translateY(${(14 * (1 - e)).toFixed(2)}px)`);
    {
      const local = sceneT - 0.15;
      if (local < 0) { rule.style.width = "0vmin"; rule.style.opacity = 0; }
      else {
        const t = Math.min(1, local / 0.5);
        const eased = easeOut(t);
        rule.style.opacity = eased.toFixed(3);
        rule.style.width = `${(14 * eased).toFixed(2)}vmin`;
      }
    }
    const itemDelays = [0.4, 0.6, 0.8];
    const itemTransforms = [
      (e) => `translateX(${(-50 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateY(${(14 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateX(${(50 * (1 - e)).toFixed(2)}px)`,
    ];
    const itemInits = ["translateX(-50px)", "translateY(14px)", "translateX(50px)"];
    items.forEach((c, i) => {
      applyT(c, sceneT - itemDelays[i], 0.55, itemInits[i], itemTransforms[i]);
    });
  } else if (name === "fix") {
    const primary = children[0];
    const secondary = children[1];
    if (sceneT < 0) primary.style.opacity = 0;
    else {
      const t = Math.min(1, sceneT / 0.55);
      const eased = easeOut(t);
      primary.style.opacity = eased.toFixed(3);
      primary.style.transform = `scale(${(0.95 + 0.05 * eased).toFixed(3)})`;
    }
    applyT(secondary, sceneT - 0.55, 0.55, "translateY(14px)",
      (e) => `translateY(${(14 * (1 - e)).toFixed(2)}px)`);
  } else if (children.length === 2) {
    applyT(children[0], sceneT, 0.55, "translateX(-50px)",
      (e) => `translateX(${(-50 * (1 - e)).toFixed(2)}px)`);
    applyT(children[1], sceneT, 0.55, "translateX(50px)",
      (e) => `translateX(${(50 * (1 - e)).toFixed(2)}px)`);
  } else {
    const transforms = [
      (e) => `translateX(${(-50 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateY(${(14 * (1 - e)).toFixed(2)}px)`,
      (e) => `translateX(${(50 * (1 - e)).toFixed(2)}px)`,
    ];
    const inits = ["translateX(-50px)", "translateY(14px)", "translateX(50px)"];
    const delays = [0, 0.3, 0.6];
    for (let i = 0; i < children.length; i++) {
      applyT(children[i], sceneT - delays[i], 0.55, inits[i], transforms[i]);
    }
  }
}

const MOTION_DISPATCH = {
  rise: applyRise,
  lateral: applyLateral,
  drop: applyDrop,
  cascade: applyCascade,
  stack: applyStack,
  split: applySplit,
};

function applySceneAnimations(idx, sceneT, dur) {
  (MOTION_DISPATCH[MOTION_VARIANT] || applyRise)(idx, sceneT, dur);
}

function resetScenes() {
  sceneEls.forEach((el) => {
    el.classList.remove("active");
    el.style.opacity = 0;
    Array.from(el.children).forEach(c => {
      c.style.opacity = 0;
      c.style.transform = "";
      if (c.classList.contains("tt-rule")) c.style.width = "0vmin";
    });
    const chars = el.querySelectorAll(".ch");
    chars.forEach((ch) => { ch.style.opacity = 0; ch.style.transform = ""; });
  });
}

function tick() {
  const t = (performance.now() - startedAt) / 1000;
  const clamped = Math.min(t, DURATION_S);
  let idx = 0;
  for (let i = 0; i < TL.length; i++) {
    if (clamped >= TL[i][1] && clamped < TL[i][2]) { idx = i; break; }
    if (clamped >= TL[i][2]) idx = i;
  }
  sceneEls.forEach((el, i) => el.classList.toggle("active", i === idx));
  const [, start, end] = TL[idx];
  applySceneAnimations(idx, clamped - start, end - start);

  $("#pf").style.width = `${(clamped / DURATION_S * 100).toFixed(2)}%`;
  const sec = Math.floor(clamped);
  const mm = String(Math.floor(sec / 60)).padStart(2, "0");
  const ss = String(sec % 60).padStart(2, "0");
  $("#clock").textContent = `${mm}:${ss}`;

  if (t < DURATION_S) raf = requestAnimationFrame(tick);
}

// =================== AUDIO ENGINE ===================
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
  lp.type = "lowpass";
  lp.frequency.value = 13000;
  masterGain.connect(lp).connect(audioCtx.destination);
}

function stopAllAudio() {
  liveNodes.forEach(n => { try { n.stop(); } catch (e) {} });
  liveNodes = [];
}

function track(node, when, dur) {
  node.start(when);
  node.stop(when + dur + 0.1);
  liveNodes.push(node);
}

function playPad(t0, totalDur, freqs) {
  freqs.forEach((f, i) => {
    const o = audioCtx.createOscillator();
    o.type = "sine";
    o.frequency.value = f * (1 + (i - 2) * 0.0008);
    const g = audioCtx.createGain();
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(0.03, t0 + 3.0);
    g.gain.setValueAtTime(0.03, t0 + totalDur - 2.5);
    g.gain.linearRampToValueAtTime(0.0001, t0 + totalDur);
    const lfo = audioCtx.createOscillator();
    const lfoGain = audioCtx.createGain();
    lfo.frequency.value = 0.12;
    lfoGain.gain.value = 0.008;
    lfo.connect(lfoGain).connect(g.gain);
    o.connect(g).connect(masterGain);
    track(o, t0, totalDur);
    track(lfo, t0, totalDur);
  });
  [65.41, 98.00].forEach((f) => {
    const o = audioCtx.createOscillator();
    o.type = "sine";
    o.frequency.value = f;
    const g = audioCtx.createGain();
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(0.025, t0 + 3.0);
    g.gain.setValueAtTime(0.025, t0 + totalDur - 2.5);
    g.gain.linearRampToValueAtTime(0.0001, t0 + totalDur);
    o.connect(g).connect(masterGain);
    track(o, t0, totalDur);
  });
}

function playSub(t0, totalDur) {
  [65.41, 130.81].forEach((f, i) => {
    const o = audioCtx.createOscillator();
    o.type = "sine";
    o.frequency.value = f;
    const g = audioCtx.createGain();
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(i === 0 ? 0.06 : 0.025, t0 + 2.0);
    g.gain.setValueAtTime(i === 0 ? 0.06 : 0.025, t0 + totalDur - 2.5);
    g.gain.linearRampToValueAtTime(0.0001, t0 + totalDur);
    const lfo = audioCtx.createOscillator();
    const lg = audioCtx.createGain();
    lfo.frequency.value = 0.13;
    lg.gain.value = 0.012;
    lfo.connect(lg).connect(g.gain);
    o.connect(g).connect(masterGain);
    track(o, t0, totalDur);
    track(lfo, t0, totalDur);
  });
}

function playSwell(t0) {
  const len = Math.floor(audioCtx.sampleRate * 1.4);
  const buf = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < len; i++) data[i] = (Math.random() * 2 - 1) * 0.4;
  const src = audioCtx.createBufferSource();
  src.buffer = buf;
  const bp = audioCtx.createBiquadFilter();
  bp.type = "bandpass";
  bp.frequency.value = 2200;
  bp.Q.value = 0.7;
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
  o.type = "sine";
  mod.type = "sine";
  o.frequency.value = freq;
  mod.frequency.value = freq * 3.2;
  modGain.gain.value = freq * 1.4;
  mod.connect(modGain).connect(o.frequency);
  const g = audioCtx.createGain();
  g.gain.setValueAtTime(0, t0);
  g.gain.linearRampToValueAtTime(vol, t0 + 0.005);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.6);
  o.connect(g).connect(masterGain);
  track(o, t0, 1.7);
  track(mod, t0, 1.7);
}

function playTick(t0, vol) {
  const len = Math.floor(audioCtx.sampleRate * 0.04);
  const buf = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
  const src = audioCtx.createBufferSource();
  src.buffer = buf;
  const hp = audioCtx.createBiquadFilter();
  hp.type = "highpass";
  hp.frequency.value = 6000;
  const g = audioCtx.createGain();
  g.gain.setValueAtTime(vol, t0);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.04);
  src.connect(hp).connect(g).connect(masterGain);
  track(src, t0, 0.05);
}

function playShimmer(t0, freq) {
  const o = audioCtx.createOscillator();
  o.type = "sine";
  o.frequency.value = freq;
  const g = audioCtx.createGain();
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.linearRampToValueAtTime(0.05, t0 + 0.9);
  g.gain.linearRampToValueAtTime(0.0001, t0 + 1.8);
  o.connect(g).connect(masterGain);
  track(o, t0, 2.0);
}

function playGlassBell(t0, freq, vol) {
  const fund = audioCtx.createOscillator();
  const partial = audioCtx.createOscillator();
  fund.type = "sine"; partial.type = "sine";
  fund.frequency.value = freq;
  partial.frequency.value = freq * 2.01;
  const g1 = audioCtx.createGain();
  const g2 = audioCtx.createGain();
  g1.gain.setValueAtTime(0, t0);
  g1.gain.linearRampToValueAtTime(vol, t0 + 0.01);
  g1.gain.exponentialRampToValueAtTime(0.0001, t0 + 2.4);
  g2.gain.setValueAtTime(0, t0);
  g2.gain.linearRampToValueAtTime(vol * 0.35, t0 + 0.01);
  g2.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.6);
  fund.connect(g1).connect(masterGain);
  partial.connect(g2).connect(masterGain);
  track(fund, t0, 2.5);
  track(partial, t0, 1.7);
}

function playLift(t0, freq) {
  const o = audioCtx.createOscillator();
  const o2 = audioCtx.createOscillator();
  o.type = "sine"; o2.type = "sine";
  o.frequency.value = freq;
  o2.frequency.value = freq * 2;
  const g = audioCtx.createGain();
  const g2 = audioCtx.createGain();
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.linearRampToValueAtTime(0.06, t0 + 1.1);
  g.gain.linearRampToValueAtTime(0.0001, t0 + 2.2);
  g2.gain.setValueAtTime(0.0001, t0);
  g2.gain.linearRampToValueAtTime(0.012, t0 + 1.1);
  g2.gain.linearRampToValueAtTime(0.0001, t0 + 2.2);
  o.connect(g).connect(masterGain);
  o2.connect(g2).connect(masterGain);
  track(o, t0, 2.4);
  track(o2, t0, 2.4);
}

function playFelted(t0, freq, vol) {
  const o = audioCtx.createOscillator();
  const o2 = audioCtx.createOscillator();
  o.type = "sine"; o2.type = "sine";
  o.frequency.value = freq;
  o2.frequency.value = freq * 2;
  const g = audioCtx.createGain();
  const g2 = audioCtx.createGain();
  g.gain.setValueAtTime(0, t0);
  g.gain.linearRampToValueAtTime(vol, t0 + 0.04);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + 2.6);
  g2.gain.setValueAtTime(0, t0);
  g2.gain.linearRampToValueAtTime(vol * 0.22, t0 + 0.04);
  g2.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.6);
  const lp = audioCtx.createBiquadFilter();
  lp.type = "lowpass"; lp.frequency.value = 3200;
  o.connect(g).connect(lp).connect(masterGain);
  o2.connect(g2).connect(lp);
  track(o, t0, 2.7);
  track(o2, t0, 2.7);
}

function scheduleAmbient(t0) {
  playPad(t0, 25, [130.81, 164.81, 196.00, 246.94, 293.66]);
  playSub(t0, 25);
  [3, 6, 9, 12, 15, 18, 21].forEach(s => playSwell(t0 + s - 0.6));
  playMallet(t0 + 12.0, 523.25, 0.22);
  playMallet(t0 + 12.05, 392.00, 0.16);
  playMallet(t0 + 21.0, 523.25, 0.22);
  playMallet(t0 + 21.05, 659.25, 0.18);
  playMallet(t0 + 22.5, 783.99, 0.18);
  [0.6, 3.4, 3.8, 4.1, 4.4, 6.4, 9.4, 15.4, 15.8, 16.4, 18.4].forEach(s => {
    playTick(t0 + s, 0.18);
  });
}

function scheduleMinimal(t0) {
  playPad(t0, 25, [130.81, 164.81, 196.00, 246.94, 293.66]);
  playSub(t0, 25);
  const shimmerNotes = [523.25, 659.25, 783.99, 987.77, 587.33, 659.25, 783.99];
  [3, 6, 9, 12, 15, 18, 21].forEach((s, i) => playShimmer(t0 + s - 0.6, shimmerNotes[i]));
  playGlassBell(t0 + 12.0, 523.25, 0.18);
  playGlassBell(t0 + 21.0, 523.25, 0.16);
  playGlassBell(t0 + 22.5, 783.99, 0.14);
}

function scheduleWarm(t0) {
  // Cmaj7 pad (drop the 9th D)
  playPad(t0, 25, [130.81, 164.81, 196.00, 246.94]);
  playSub(t0, 25);
  const liftNotes = [130.81, 164.81, 196.00, 246.94, 146.83, 164.81, 196.00];
  [3, 6, 9, 12, 15, 18, 21].forEach((s, i) => playLift(t0 + s - 0.8, liftNotes[i]));
  playFelted(t0 + 12.0, 523.25, 0.18);
  playFelted(t0 + 12.06, 392.00, 0.11);
  playFelted(t0 + 21.0, 523.25, 0.16);
  playFelted(t0 + 21.03, 659.25, 0.10);
  playFelted(t0 + 22.5, 783.99, 0.14);
}

const AUDIO_DISPATCH = {
  ambient: scheduleAmbient,
  minimal: scheduleMinimal,
  warm: scheduleWarm,
};

function scheduleScore(t0) {
  (AUDIO_DISPATCH[AUDIO_VARIANT] || scheduleAmbient)(t0);
}

async function play() {
  cancelAnimationFrame(raf);
  resetScenes();
  stopAllAudio();
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
  if (!soundEnabled) stopAllAudio();
});

play();
"""


def build_js(motion_variant, audio_variant):
    return (
        JS_DRIVER_TEMPLATE
        .replace("__MOTION_VARIANT__", motion_variant)
        .replace("__AUDIO_VARIANT__", audio_variant)
    )


def build_html(spec, theme, motion_variant, audio_variant):
    css = build_css(theme, motion_variant)
    scenes_html = build_scene_html(spec)
    js = build_js(motion_variant, audio_variant)
    title_text = spec.get("topic") or spec["scenes"]["title"]["headline"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
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
    parser.add_argument("spec", help="Path to scene-spec.json")
    parser.add_argument("output", help="Path to write HTML output")
    parser.add_argument("--theme", help="Path to theme.json (defaults to default_theme.json)")
    parser.add_argument("--motion-variant", choices=MOTION_VARIANTS, default=None,
                        help="motion treatment (overrides spec.motion_variant; default rise)")
    parser.add_argument("--audio-variant", choices=AUDIO_VARIANTS, default=None,
                        help="audio score (overrides spec.audio_variant; default ambient)")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    theme = resolve_theme(spec, args.theme)

    motion_variant = args.motion_variant or spec.get("motion_variant", "rise")
    audio_variant = args.audio_variant or spec.get("audio_variant", "ambient")
    if motion_variant not in MOTION_VARIANTS:
        raise SystemExit(f"unknown motion_variant: {motion_variant!r}, expected one of {MOTION_VARIANTS}")
    if audio_variant not in AUDIO_VARIANTS:
        raise SystemExit(f"unknown audio_variant: {audio_variant!r}, expected one of {AUDIO_VARIANTS}")

    html = build_html(spec, theme, motion_variant, audio_variant)
    Path(args.output).write_text(html)
    print(f"Wrote {args.output} ({len(html):,} bytes, motion={motion_variant}, audio={audio_variant})")


if __name__ == "__main__":
    main()
