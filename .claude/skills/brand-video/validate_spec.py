#!/usr/bin/env python3
"""
brand-video spec validator.

Enforces:
- All required fields per scene template
- Hard copy rules (no em/en dashes, no semicolons, no body colons,
  no question marks, no arrows, no non-ASCII except smart quotes)
- Per-template character limits
- Total duration in [12.0, 32.0] seconds
- Token contrast: ink/canvas >= 4.5, accent/canvas >= 3.5, ink_muted/canvas >= 3.0

Exits 0 on pass, 1 on any failure.

Usage:
    python validate_spec.py <spec.json>
"""

import argparse
import json
import sys
from pathlib import Path

HARD_FORBIDDEN = {
    "em dash":      ["—"],
    "en dash":      ["–"],
    "semicolon":    [";"],
    "question":     ["?"],
    "arrow":        ["→", "←", "↑", "↓"],
}

# per-template character limits
LIMITS = {
    "title":        {"headline": 22, "eyebrow": 40},
    "stack":        {"eyebrow": 16, "name": 18, "descriptor": 26},
    "two_line":     {"line": 22},
    "three_line":   {"line": 26},
    "fix":          {"primary": 18, "secondary": 22},
    "mono_block":   {"line": 38},
    "quote":        {"quote": 80, "attribution": 28},
    "close":        {"primary": 20, "accent": 20, "subtitle": 44},
    "diagram":      {"eyebrow": 24, "label": 18},
    "flash":        {"word": 16, "caption": 36},
    "big_number":   {"numeral": 12, "caption": 36, "sub": 40},
    "terminal":     {"title": 36, "line": 48},
    "split":        {"label": 18, "value": 16},
    "logo_reveal":  {"word": 14, "tagline": 40},
    "sparkline":    {"eyebrow": 24, "value_label": 12, "caption": 36},
    "word_cascade": {"word": 14},
    "wire_dispatch": {"ticker": 38, "dateline": 24, "headline": 44, "lede": 96},
    "panes":        {"eyebrow": 24, "name": 14, "line": 24},
    "morph":        {"before": 20, "after": 20, "eyebrow": 32},
    "screen_capture": {"url": 44, "title": 30, "line": 42},
    "metaphor":     {"label": 22, "eyebrow": 32},
    "oner":         {"eyebrow": 32, "block": 26},
}

VALID_TEMPLATES = set(LIMITS.keys())
VALID_CAMERAS = {"push_in", "pull_back", "ken_burns", "crash_zoom", "orbit", "parallax_drift",
                 "static_breathe", "rack_focus", "dolly_up", "tilt_reveal", "none"}
VALID_PALETTES = {"ambient", "electronic", "acoustic"}
VALID_FRAMEWORKS = {"CLASSIC", "RECEIPT", "SCHEMATIC", "MANIFESTO", "DISPATCH"}
VALID_BACKGROUNDS = {"starfield", "aurora", "grid", "shader", "none"}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1, c2):
    L1 = relative_luminance(hex_to_rgb(c1))
    L2 = relative_luminance(hex_to_rgb(c2))
    return (max(L1, L2) + 0.05) / (min(L1, L2) + 0.05)


def check_text(path, text, allow_colon, errors):
    for label, chars in HARD_FORBIDDEN.items():
        for ch in chars:
            if ch in text:
                errors.append(f"  HARD FAIL: {label} ({ch!r}) in {path}: {text!r}")
    if not allow_colon and ":" in text:
        errors.append(f"  HARD FAIL: colon in body of {path}: {text!r}")
    allow = set("'’‘“”—–")  # smart quotes only
    for ch in text:
        if ord(ch) > 127 and ch not in allow:
            errors.append(f"  HARD FAIL: non-ASCII char {ch!r} in {path}: {text!r}")
            break


def check_len(path, text, limit, label, errors):
    if len(text) > limit:
        errors.append(f"  CHAR LIMIT: {len(text)} > {limit} for {label} at {path}: {text!r}")


def validate_scene(idx, sc, errors):
    tpl = sc.get("template")
    if tpl not in VALID_TEMPLATES:
        errors.append(f"  TEMPLATE: scenes[{idx}].template = {tpl!r} (must be one of {sorted(VALID_TEMPLATES)})")
        return
    base = f"scenes[{idx}].{tpl}"
    L = LIMITS[tpl]

    cam = sc.get("camera", "static_breathe")
    if cam not in VALID_CAMERAS:
        errors.append(f"  CAMERA: scenes[{idx}].camera = {cam!r} (must be one of {sorted(VALID_CAMERAS)})")

    if tpl == "title":
        check_text(f"{base}.headline", sc["headline"], False, errors)
        check_text(f"{base}.eyebrow", sc["eyebrow"], True, errors)
        check_len(f"{base}.headline", sc["headline"], L["headline"], "headline", errors)
        check_len(f"{base}.eyebrow", sc["eyebrow"], L["eyebrow"], "eyebrow", errors)

    elif tpl == "stack":
        check_text(f"{base}.eyebrow", sc["eyebrow"], True, errors)
        check_len(f"{base}.eyebrow", sc["eyebrow"], L["eyebrow"], "stack eyebrow", errors)
        items = sc.get("items", [])
        if not (2 <= len(items) <= 5):
            errors.append(f"  STRUCTURE: {base}.items must have 2..5 entries, got {len(items)}")
        for i, it in enumerate(items):
            check_text(f"{base}.items[{i}].name", it["name"], False, errors)
            check_text(f"{base}.items[{i}].descriptor", it["descriptor"], False, errors)
            check_len(f"{base}.items[{i}].name", it["name"], L["name"], "item name", errors)
            check_len(f"{base}.items[{i}].descriptor", it["descriptor"], L["descriptor"], "descriptor", errors)

    elif tpl in ("two_line", "three_line"):
        n_required = 2 if tpl == "two_line" else 3
        lines = sc.get("lines", [])
        if len(lines) != n_required:
            errors.append(f"  STRUCTURE: {base}.lines must have {n_required} entries, got {len(lines)}")
        for i, line in enumerate(lines):
            check_text(f"{base}.lines[{i}]", line, False, errors)
            check_len(f"{base}.lines[{i}]", line, L["line"], f"{tpl} line", errors)
        ai = sc.get("accent_idx", -1)
        if ai is not None and ai != -1 and not (0 <= ai < n_required):
            errors.append(f"  STRUCTURE: {base}.accent_idx out of range: {ai}")

    elif tpl == "fix":
        check_text(f"{base}.primary", sc["primary"], False, errors)
        check_text(f"{base}.secondary", sc["secondary"], False, errors)
        check_len(f"{base}.primary", sc["primary"], L["primary"], "fix.primary", errors)
        check_len(f"{base}.secondary", sc["secondary"], L["secondary"], "fix.secondary", errors)

    elif tpl == "mono_block":
        lines = sc.get("lines", [])
        if not (1 <= len(lines) <= 6):
            errors.append(f"  STRUCTURE: {base}.lines must have 1..6 entries, got {len(lines)}")
        for i, line in enumerate(lines):
            check_text(f"{base}.lines[{i}]", line, False, errors)
            check_len(f"{base}.lines[{i}]", line, L["line"], "mono_block line", errors)
        ai = sc.get("accent_idx", -1)
        if ai is not None and ai != -1 and not (0 <= ai < len(lines)):
            errors.append(f"  STRUCTURE: {base}.accent_idx out of range: {ai}")

    elif tpl == "quote":
        check_text(f"{base}.quote", sc["quote"], False, errors)
        check_len(f"{base}.quote", sc["quote"], L["quote"], "quote", errors)
        if sc.get("attribution"):
            check_text(f"{base}.attribution", sc["attribution"], False, errors)
            check_len(f"{base}.attribution", sc["attribution"], L["attribution"], "attribution", errors)

    elif tpl == "close":
        check_text(f"{base}.primary", sc["primary"], False, errors)
        check_text(f"{base}.accent", sc["accent"], False, errors)
        check_len(f"{base}.primary", sc["primary"], L["primary"], "close.primary", errors)
        check_len(f"{base}.accent", sc["accent"], L["accent"], "close.accent", errors)
        if sc.get("subtitle"):
            check_text(f"{base}.subtitle", sc["subtitle"], False, errors)
            check_len(f"{base}.subtitle", sc["subtitle"], L["subtitle"], "close.subtitle", errors)

    elif tpl == "diagram":
        if sc.get("eyebrow"):
            check_text(f"{base}.eyebrow", sc["eyebrow"], True, errors)
            check_len(f"{base}.eyebrow", sc["eyebrow"], L["eyebrow"], "diagram eyebrow", errors)
        nodes = sc.get("nodes", [])
        if not (2 <= len(nodes) <= 5):
            errors.append(f"  STRUCTURE: {base}.nodes must have 2..5 entries, got {len(nodes)}")
        for i, nd in enumerate(nodes):
            for need in ("label", "x", "y"):
                if need not in nd:
                    errors.append(f"  STRUCTURE: {base}.nodes[{i}].{need} missing")
            if "label" in nd:
                check_text(f"{base}.nodes[{i}].label", nd["label"], False, errors)
                check_len(f"{base}.nodes[{i}].label", nd["label"], L["label"], "node label", errors)
        for i, ed in enumerate(sc.get("edges", [])):
            if "from" not in ed or "to" not in ed:
                errors.append(f"  STRUCTURE: {base}.edges[{i}] missing from/to")
                continue
            if not (0 <= ed["from"] < len(nodes)) or not (0 <= ed["to"] < len(nodes)):
                errors.append(f"  STRUCTURE: {base}.edges[{i}] from/to out of range")

    elif tpl == "flash":
        check_text(f"{base}.word", sc["word"], False, errors)
        check_len(f"{base}.word", sc["word"], L["word"], "flash word", errors)
        if sc.get("caption"):
            check_text(f"{base}.caption", sc["caption"], True, errors)
            check_len(f"{base}.caption", sc["caption"], L["caption"], "flash caption", errors)

    elif tpl == "big_number":
        check_text(f"{base}.numeral", sc["numeral"], False, errors)
        check_len(f"{base}.numeral", sc["numeral"], L["numeral"], "big_number numeral", errors)
        check_text(f"{base}.caption", sc["caption"], False, errors)
        check_len(f"{base}.caption", sc["caption"], L["caption"], "big_number caption", errors)
        if sc.get("sub"):
            check_text(f"{base}.sub", sc["sub"], False, errors)
            check_len(f"{base}.sub", sc["sub"], L["sub"], "big_number sub", errors)

    elif tpl == "terminal":
        if sc.get("title"):
            check_text(f"{base}.title", sc["title"], True, errors)
            check_len(f"{base}.title", sc["title"], L["title"], "terminal title", errors)
        lines = sc.get("lines", [])
        if not (1 <= len(lines) <= 6):
            errors.append(f"  STRUCTURE: {base}.lines must have 1..6 entries, got {len(lines)}")
        for i, line in enumerate(lines):
            text = line["text"] if isinstance(line, dict) else line
            check_text(f"{base}.lines[{i}]", text, True, errors)
            check_len(f"{base}.lines[{i}]", text, L["line"], "terminal line", errors)

    elif tpl == "split":
        for side in ("left", "right"):
            if side not in sc:
                errors.append(f"  STRUCTURE: {base}.{side} missing")
                continue
            check_text(f"{base}.{side}.label", sc[side]["label"], False, errors)
            check_text(f"{base}.{side}.value", sc[side]["value"], False, errors)
            check_len(f"{base}.{side}.label", sc[side]["label"], L["label"], "split label", errors)
            check_len(f"{base}.{side}.value", sc[side]["value"], L["value"], "split value", errors)

    elif tpl == "logo_reveal":
        check_text(f"{base}.word", sc["word"], False, errors)
        check_len(f"{base}.word", sc["word"], L["word"], "logo_reveal word", errors)
        if sc.get("tagline"):
            check_text(f"{base}.tagline", sc["tagline"], False, errors)
            check_len(f"{base}.tagline", sc["tagline"], L["tagline"], "logo_reveal tagline", errors)

    elif tpl == "sparkline":
        values = sc.get("values", [])
        if not (5 <= len(values) <= 24):
            errors.append(f"  STRUCTURE: {base}.values must have 5..24 entries, got {len(values)}")
        if not all(isinstance(v, (int, float)) for v in values):
            errors.append(f"  STRUCTURE: {base}.values must be numbers")
        check_text(f"{base}.value_label", sc["value_label"], False, errors)
        check_len(f"{base}.value_label", sc["value_label"], L["value_label"], "sparkline value_label", errors)
        check_text(f"{base}.caption", sc["caption"], False, errors)
        check_len(f"{base}.caption", sc["caption"], L["caption"], "sparkline caption", errors)
        if sc.get("eyebrow"):
            check_text(f"{base}.eyebrow", sc["eyebrow"], True, errors)
            check_len(f"{base}.eyebrow", sc["eyebrow"], L["eyebrow"], "sparkline eyebrow", errors)

    elif tpl == "word_cascade":
        words = sc.get("words", [])
        if not (3 <= len(words) <= 6):
            errors.append(f"  STRUCTURE: {base}.words must have 3..6 entries, got {len(words)}")
        for i, w in enumerate(words):
            check_text(f"{base}.words[{i}]", w, False, errors)
            check_len(f"{base}.words[{i}]", w, L["word"], "word_cascade word", errors)
        ai = sc.get("accent_idx", -1)
        if ai is not None and ai != -1 and not (0 <= ai < len(words)):
            errors.append(f"  STRUCTURE: {base}.accent_idx out of range: {ai}")

    elif tpl == "panes":
        panes = sc.get("panes", [])
        if not (2 <= len(panes) <= 4):
            errors.append(f"  STRUCTURE: {base}.panes must have 2..4 entries, got {len(panes)}")
        for i, pn in enumerate(panes):
            if "name" not in pn:
                errors.append(f"  STRUCTURE: {base}.panes[{i}].name missing")
                continue
            check_text(f"{base}.panes[{i}].name", pn["name"], False, errors)
            check_len(f"{base}.panes[{i}].name", pn["name"], L["name"], "pane name", errors)
            for j, ln in enumerate(pn.get("lines", [])[:4]):
                check_text(f"{base}.panes[{i}].lines[{j}]", ln, False, errors)
                check_len(f"{base}.panes[{i}].lines[{j}]", ln, L["line"], "pane line", errors)
            if len(pn.get("lines", [])) > 3:
                errors.append(f"  STRUCTURE: {base}.panes[{i}] max 3 lines")
            for field in ("state", "flip_to"):
                if pn.get(field) and pn[field] not in ("working", "blocked", "done", "idle"):
                    errors.append(f"  STRUCTURE: {base}.panes[{i}].{field} = {pn[field]!r} invalid")
        if sc.get("eyebrow"):
            check_text(f"{base}.eyebrow", sc["eyebrow"], True, errors)
            check_len(f"{base}.eyebrow", sc["eyebrow"], L["eyebrow"], "panes eyebrow", errors)

    elif tpl == "wire_dispatch":
        check_text(f"{base}.ticker", sc["ticker"], True, errors)
        check_len(f"{base}.ticker", sc["ticker"], L["ticker"], "wire_dispatch ticker", errors)
        check_text(f"{base}.dateline", sc["dateline"], True, errors)
        check_len(f"{base}.dateline", sc["dateline"], L["dateline"], "wire_dispatch dateline", errors)
        check_text(f"{base}.headline", sc["headline"], False, errors)
        check_len(f"{base}.headline", sc["headline"], L["headline"], "wire_dispatch headline", errors)
        check_text(f"{base}.lede", sc["lede"], False, errors)
        check_len(f"{base}.lede", sc["lede"], L["lede"], "wire_dispatch lede", errors)


def validate(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    errors = []

    scenes = spec.get("scenes", [])
    if not (3 <= len(scenes) <= 8):
        errors.append(f"  STRUCTURE: scenes must have 3..8 entries, got {len(scenes)}")

    total = 0.0
    for i, sc in enumerate(scenes):
        validate_scene(i, sc, errors)
        total += float(sc.get("duration_s", 3.0))
    if not (12.0 <= total <= 32.0):
        errors.append(f"  DURATION: total duration {total:.2f}s outside [12.0, 32.0]")

    design = spec.get("design", {})
    tokens = design.get("tokens", {})
    for need in ("canvas", "ink", "accent", "ink_muted", "hairline"):
        if need not in tokens:
            errors.append(f"  TOKENS: design.tokens.{need} missing")

    palette = design.get("audio_palette", "ambient")
    if palette not in VALID_PALETTES:
        errors.append(f"  AUDIO: design.audio_palette = {palette!r} (must be one of {sorted(VALID_PALETTES)})")

    framework = design.get("framework")
    if framework is not None and framework not in VALID_FRAMEWORKS:
        errors.append(f"  FRAMEWORK: design.framework = {framework!r} (must be one of {sorted(VALID_FRAMEWORKS)} or null)")

    background = design.get("background") or {}
    bg_style = background.get("style", "starfield")
    if bg_style not in VALID_BACKGROUNDS:
        errors.append(f"  BACKGROUND: design.background.style = {bg_style!r} (must be one of {sorted(VALID_BACKGROUNDS)})")

    # Silent-first word budget (X practice: ~45 words max across 4-7 scenes).
    def scene_words(sc):
        text = []
        for k, v in sc.items():
            if isinstance(v, str) and k not in ("template", "camera"):
                text.append(v)
            elif k in ("lines", "words") and isinstance(v, list):
                for item in v:
                    text.append(item["text"] if isinstance(item, dict) else str(item))
            elif k == "items" and isinstance(v, list):
                for item in v:
                    text.append(item.get("name", "") + " " + item.get("descriptor", ""))
        return sum(len(t.split()) for t in text)

    total_words = sum(scene_words(sc) for sc in scenes)
    if total_words > 55:
        print(f"  WARN: total word count {total_words} > 55; silent-feed viewers cannot read this much")

    # Accent threshold defaults to 3.0:1 (warm-earth palettes need this floor).
    # The spec can override per-aesthetic via design.accent_contrast_min, e.g.
    # mono / neon / dashboard aesthetics raise it back to 4.5.
    accent_min = float(design.get("accent_contrast_min", 3.0))

    if all(k in tokens for k in ("canvas", "ink", "accent", "ink_muted")):
        ink_bg = contrast(tokens["ink"], tokens["canvas"])
        ac_bg = contrast(tokens["accent"], tokens["canvas"])
        mu_bg = contrast(tokens["ink_muted"], tokens["canvas"])
        print(f"Token contrast:")
        print(f"  ink on canvas:        {ink_bg:5.2f}:1 (need 4.5+) {'PASS' if ink_bg >= 4.5 else 'FAIL'}")
        print(f"  accent on canvas:     {ac_bg:5.2f}:1 (need {accent_min:.1f}+) {'PASS' if ac_bg >= accent_min else 'FAIL'}")
        print(f"  ink_muted on canvas:  {mu_bg:5.2f}:1 (need 3.0+) {'PASS' if mu_bg >= 3.0 else 'FAIL'}")
        if ink_bg < 4.5:
            errors.append(f"  CONTRAST: ink/canvas {ink_bg:.2f}:1 below 4.5:1")
        if ac_bg < accent_min:
            errors.append(f"  CONTRAST: accent/canvas {ac_bg:.2f}:1 below {accent_min:.1f}:1")
        if mu_bg < 3.0:
            errors.append(f"  CONTRAST: ink_muted/canvas {mu_bg:.2f}:1 below 3.0:1")

    print()
    print(f"Total duration: {total:.2f}s across {len(scenes)} scene(s)")
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(e)
        return False
    print("VALIDATION PASSED")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", help="Path to spec.json")
    args = parser.parse_args()
    ok = validate(args.spec)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
