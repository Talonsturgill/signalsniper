#!/usr/bin/env python3
"""
Project-native brand extraction for the daily-tribute pipeline.

Fetches the honored project's website (plus up to two linked stylesheets),
mines CSS custom properties / theme-color / hex frequencies, and derives the
five design tokens the renderer needs. Recognition is the quote-post trigger:
a tribute in the project's OWN colors reads as a gift, not a template.

Token roles are resolved by custom-property NAME first (bg/ink/accent/muted/
line vocabularies), frequency+saturation heuristics second. When a site ships
both light and dark variable sets, the dark set wins (X feed default).
All output tokens are contrast-fixed against the validator floors.

Exit codes: 0 ok, 3 insufficient signal (caller falls back to the brand
library / preset packs).

Usage:
    python brand_extract.py --url https://project.dev --out reports/brand-extract-DATE.json
"""

import argparse
import colorsys
import json
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROLE_VOCAB = OrderedDict([
    ("canvas", re.compile(r"(bg|background|canvas|surface|base)(?!-elevated)", re.I)),
    ("ink", re.compile(r"(ink|text|fg|foreground)(?!-soft)", re.I)),
    ("accent", re.compile(r"(accent|primary|brand|link|highlight)", re.I)),
    ("ink_muted", re.compile(r"(muted|secondary|subtle|dim)", re.I)),
    ("hairline", re.compile(r"(line|border|hairline|divider|rule)", re.I)),
])

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")
PROP_RE = re.compile(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\b")
CSS_LINK_RE = re.compile(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)", re.I)
THEME_RE = re.compile(r"name=[\"']theme-color[\"'][^>]*content=[\"'](#[0-9a-fA-F]{3,6})", re.I)


def fetch(url, limit_bytes=3_000_000):
    res = subprocess.run(
        ["curl", "-sSL", "--max-time", "20", "--range", f"0-{limit_bytes}", url],
        capture_output=True,
    )
    if res.returncode != 0 or not res.stdout:
        return None
    return res.stdout.decode("utf-8", errors="ignore")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(h):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1, c2):
    l1, l2 = luminance(c1), luminance(c2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def saturation(h):
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    _, _, s = colorsys.rgb_to_hls(r, g, b)
    return s


def adjust_light(h, delta):
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    ll = min(1.0, max(0.0, ll + delta))
    r2, g2, b2 = colorsys.hls_to_rgb(hh, ll, ss)
    return "#{:02x}{:02x}{:02x}".format(int(r2 * 255), int(g2 * 255), int(b2 * 255))


def mix(a, b, k):
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)
    return "#{:02x}{:02x}{:02x}".format(
        int(ra + (rb - ra) * k), int(ga + (gb - ga) * k), int(ba + (bb - ba) * k))


def fix_contrast(fg, canvas, floor, prefer_lighter):
    c = fg
    for _ in range(14):
        if contrast(c, canvas) >= floor:
            return c
        c = adjust_light(c, 0.05 if prefer_lighter else -0.05)
    return None


def extract(url):
    html = fetch(url)
    if not html:
        return None, ["page fetch failed"]
    notes = []
    props = PROP_RE.findall(html)
    theme = THEME_RE.findall(html)
    hexes = Counter(h.lower() for h in HEX_RE.findall(html))

    css_urls = CSS_LINK_RE.findall(html)[:2]
    base = url.rstrip("/")
    for cu in css_urls:
        if cu.startswith("//"):
            cu = "https:" + cu
        elif cu.startswith("/"):
            m = re.match(r"(https?://[^/]+)", base)
            cu = (m.group(1) if m else base) + cu
        elif not cu.startswith("http"):
            cu = base + "/" + cu
        css = fetch(cu)
        if css:
            props += PROP_RE.findall(css)
            hexes.update(h.lower() for h in HEX_RE.findall(css))
            notes.append(f"stylesheet mined: {cu}")

    if not props and not hexes:
        return None, notes + ["no colors found"]

    # Group custom-prop variants by name. Sites ship the same var several times
    # (light theme, dark theme, scoped demo themes); resolve each name to the
    # variant that matches the wanted pole AND is most frequent site-wide, so a
    # one-off scoped theme block can't hijack the real brand color.
    by_name = {}
    for name, val in props:
        by_name.setdefault(name, []).append(val.lower())
    bg_variants = [v for n, vs in by_name.items() if ROLE_VOCAB["canvas"].search(n) for v in vs]
    dark_theme = any(luminance(v) < 0.2 for v in bg_variants)

    def resolve(name, variants, role):
        pool = variants
        if role == "canvas" and dark_theme:
            darks = [v for v in variants if luminance(v) < 0.5]
            pool = darks or variants
        elif role == "ink" and dark_theme:
            lights = [v for v in variants if luminance(v) > 0.5]
            pool = lights or variants
        return max(pool, key=lambda v: hexes.get(v, 0))

    tokens, provenance = {}, {}
    for role, pat in ROLE_VOCAB.items():
        for name, variants in by_name.items():
            if pat.search(name):
                tokens[role] = resolve(name, variants, role)
                provenance[role] = f"css var {name}"
                break

    if theme and "canvas" not in tokens:
        t = theme[0].lower()
        if len(t) == 4:
            t = "#" + "".join(ch * 2 for ch in t[1:])
        tokens["canvas"] = t
        provenance["canvas"] = "meta theme-color"

    # Frequency + saturation fallbacks
    common = [h for h, _ in hexes.most_common(40)]
    if "canvas" not in tokens and common:
        darks = [h for h in common if luminance(h) < 0.12]
        tokens["canvas"] = darks[0] if darks else min(common, key=luminance)
        provenance["canvas"] = "frequency heuristic (darkest common)"
    if "ink" not in tokens and common:
        tokens["ink"] = max(common, key=luminance)
        provenance["ink"] = "frequency heuristic (lightest common)"
    if "accent" not in tokens and common:
        sat = [(h, saturation(h)) for h in common if 0.08 < luminance(h) < 0.85]
        sat.sort(key=lambda kv: -kv[1])
        if sat and sat[0][1] > 0.35:
            tokens["accent"] = sat[0][0]
            provenance["accent"] = "frequency heuristic (most saturated)"

    if "canvas" not in tokens or "accent" not in tokens:
        return None, notes + [f"insufficient roles resolved: {sorted(tokens)}"]

    canvas = tokens["canvas"]
    dark = luminance(canvas) < 0.5

    # Never ship pure #000/#fff: they melt into X's Lights Out / light chrome.
    if canvas == "#000000":
        canvas = "#0b0b0c"
        provenance["canvas"] += " (nudged off pure black)"
    elif canvas == "#ffffff":
        canvas = "#faf9f7"
        provenance["canvas"] += " (nudged off pure white)"
    tokens["canvas"] = canvas

    ink = tokens.get("ink")
    if ink == "#ffffff":
        ink = "#f2f0eb"
        provenance["ink"] = provenance.get("ink", "") + " (softened from pure white)"
    elif ink == "#000000":
        ink = "#141412"
        provenance["ink"] = provenance.get("ink", "") + " (softened from pure black)"
    if not ink or contrast(ink, canvas) < 4.5:
        fixed = fix_contrast(ink, canvas, 4.5, dark) if ink else None
        ink = fixed or ("#f2f0ea" if dark else "#141412")
        provenance["ink"] = provenance.get("ink", "") + " (contrast-fixed)"
    tokens["ink"] = ink

    accent = fix_contrast(tokens["accent"], canvas, 4.5, dark)
    if accent is None:
        return None, notes + ["accent could not reach 4.5:1 on canvas"]
    if accent != tokens["accent"]:
        provenance["accent"] += f" (lightness-nudged from {tokens['accent']})"
    tokens["accent"] = accent

    def hue_gap(a, b):
        ra, ga, ba = (c / 255 for c in hex_to_rgb(a))
        rb, gb, bb = (c / 255 for c in hex_to_rgb(b))
        ha, _, sa = colorsys.rgb_to_hls(ra, ga, ba)
        hb, _, sb = colorsys.rgb_to_hls(rb, gb, bb)
        if sa < 0.06 or sb < 0.06:  # near-gray: hue meaningless
            return 0.0
        d = abs(ha - hb)
        return min(d, 1 - d) * 360

    muted = tokens.get("ink_muted")
    # A muted token from a different theme block reads off-brand: require it to
    # sit between ink and canvas with comfortable contrast AND share ink's
    # temperature (muted is dimmed ink, not a foreign gray), else derive it.
    if not muted or not (3.5 <= contrast(muted, canvas) <= contrast(ink, canvas)) \
            or hue_gap(muted, ink) > 60:
        muted = mix(ink, canvas, 0.42)
        if contrast(muted, canvas) < 3.0:
            muted = mix(ink, canvas, 0.28)
        provenance["ink_muted"] = "derived mix(ink, canvas)"
    tokens["ink_muted"] = muted

    hairline = tokens.get("hairline")
    if not hairline or not (1.05 < contrast(hairline, canvas) < 3.5):
        hairline = mix(ink, canvas, 0.85)
        provenance["hairline"] = "derived mix(ink, canvas, 0.85)"
    tokens["hairline"] = hairline

    named = sum(1 for r in ("canvas", "ink", "accent") if "css var" in provenance.get(r, ""))
    confidence = "high" if named >= 3 else ("medium" if named >= 1 else "low")
    return {
        "tokens": {k: tokens[k] for k in ("canvas", "ink", "ink_muted", "accent", "hairline")},
        "provenance": provenance,
        "confidence": confidence,
        "dark_canvas": dark,
    }, notes


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--out", help="write JSON here (also printed to stdout)")
    args = p.parse_args()

    result, notes = extract(args.url)
    if result is None:
        print(json.dumps({"error": "insufficient signal", "notes": notes}, indent=2))
        sys.exit(3)

    result["source_url"] = args.url
    result["notes"] = notes
    out = json.dumps(result, indent=2)
    print(out)
    if args.out:
        Path(args.out).write_text(out + "\n")


if __name__ == "__main__":
    main()
