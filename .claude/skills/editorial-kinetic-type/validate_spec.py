#!/usr/bin/env python3
"""
editorial-kinetic-type spec validator.

Checks a scene-spec.json against all SKILL.md copy rules, character limits,
and theme contrast requirements. Exits with 0 if valid, 1 if any failure.

Usage:
    python validate_spec.py <spec.json>
"""

import argparse
import json
import sys
from pathlib import Path


# ---- copy rules ----
HARD_FORBIDDEN = {
    "em dash": ["—"],
    "en dash": ["–"],
    "semicolon": [";"],
    "question mark": ["?"],
    "arrow": ["→", "←", "↑", "↓"],
}

MOTION_VARIANTS = {"rise", "lateral", "drop", "cascade", "stack", "split"}
AUDIO_VARIANTS = {"ambient", "minimal", "warm"}


def check_string(path, text, allow_colon=False, errors=None):
    if errors is None:
        errors = []
    for label, chars in HARD_FORBIDDEN.items():
        for ch in chars:
            if ch in text:
                errors.append(f"  HARD FAIL: {label} ({ch!r}) in {path}: {text!r}")
    if not allow_colon and ":" in text:
        errors.append(f"  HARD FAIL: colon in body of {path}: {text!r}")
    # Emoji check: any non-ASCII char that's not in our explicit allow list
    allow = set("'’–—""'")
    for ch in text:
        if ord(ch) > 127 and ch not in allow and ch not in "→←↑↓":
            # already flagged arrows above; flag others as emoji
            if ch not in "→←↑↓":
                errors.append(f"  HARD FAIL: non-ASCII char {ch!r} (possible emoji) in {path}: {text!r}")
                break
    return errors


def check_length(path, text, limit, label, errors):
    if len(text) > limit:
        errors.append(f"  CHAR LIMIT: {len(text)} > {limit} for {label} at {path}: {text!r}")


# ---- contrast ----
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


def validate(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    errors = []
    s = spec["scenes"]

    # Title
    check_string(".scenes.title.headline", s["title"]["headline"], errors=errors)
    check_string(".scenes.title.eyebrow", s["title"]["eyebrow"], errors=errors)
    check_length(".scenes.title.headline", s["title"]["headline"], 22, "headline (max 22)", errors)
    check_length(".scenes.title.eyebrow", s["title"]["eyebrow"], 40, "eyebrow", errors)

    # Three things
    tt = s["three_things"]
    check_string(".scenes.three_things.eyebrow", tt["eyebrow"], allow_colon=True, errors=errors)
    check_length(".scenes.three_things.eyebrow", tt["eyebrow"], 16, "three_things eyebrow", errors)
    if len(tt["items"]) != 3:
        errors.append(f"  STRUCTURE: three_things must have exactly 3 items, got {len(tt['items'])}")
    for i, item in enumerate(tt["items"]):
        check_string(f".scenes.three_things.items[{i}].name", item["name"], errors=errors)
        check_string(f".scenes.three_things.items[{i}].descriptor", item["descriptor"], errors=errors)
        check_length(f".scenes.three_things.items[{i}].name", item["name"], 18, "item name", errors)
        check_length(f".scenes.three_things.items[{i}].descriptor", item["descriptor"], 24, "descriptor", errors)

    # Problem
    for k in ("line_a", "line_b"):
        check_string(f".scenes.problem.{k}", s["problem"][k], errors=errors)
        check_length(f".scenes.problem.{k}", s["problem"][k], 22, "problem line", errors)

    # Specific case
    for k in ("line_a", "line_b", "line_c"):
        check_string(f".scenes.specific_case.{k}", s["specific_case"][k], errors=errors)
        check_length(f".scenes.specific_case.{k}", s["specific_case"][k], 24, "specific_case line", errors)

    # Fix
    check_string(".scenes.fix.primary", s["fix"]["primary"], errors=errors)
    check_string(".scenes.fix.secondary", s["fix"]["secondary"], errors=errors)
    check_length(".scenes.fix.primary", s["fix"]["primary"], 18, "fix.primary (largest type)", errors)
    check_length(".scenes.fix.secondary", s["fix"]["secondary"], 22, "fix.secondary", errors)

    # Mechanism
    for k in ("line_a", "line_b", "line_c"):
        check_string(f".scenes.mechanism.{k}", s["mechanism"][k], errors=errors)
        check_length(f".scenes.mechanism.{k}", s["mechanism"][k], 26, "mechanism line", errors)

    # Consequence
    for k in ("line_a", "line_b", "line_c"):
        check_string(f".scenes.consequence.{k}", s["consequence"][k], errors=errors)
        check_length(f".scenes.consequence.{k}", s["consequence"][k], 24, "consequence line", errors)

    # Close
    check_string(".scenes.close.primary", s["close"]["primary"], errors=errors)
    check_string(".scenes.close.accent", s["close"]["accent"], errors=errors)
    check_string(".scenes.close.subtitle", s["close"]["subtitle"], errors=errors)
    check_length(".scenes.close.primary", s["close"]["primary"], 18, "close.primary", errors)
    check_length(".scenes.close.accent", s["close"]["accent"], 18, "close.accent", errors)
    check_length(".scenes.close.subtitle", s["close"]["subtitle"], 40, "close.subtitle", errors)

    # Motion / audio variants (optional)
    if "motion_variant" in spec and spec["motion_variant"] not in MOTION_VARIANTS:
        errors.append(f"  VARIANT: motion_variant {spec['motion_variant']!r} not in {sorted(MOTION_VARIANTS)}")
    if "audio_variant" in spec and spec["audio_variant"] not in AUDIO_VARIANTS:
        errors.append(f"  VARIANT: audio_variant {spec['audio_variant']!r} not in {sorted(AUDIO_VARIANTS)}")

    # Theme contrast (only for custom themes)
    if isinstance(spec.get("theme"), dict):
        theme = spec["theme"]
        ink_bg = contrast(theme["ink"], theme["background"])
        accent_bg = contrast(theme["accent"], theme["background"])
        muted_bg = contrast(theme["muted"], theme["background"])
        print(f"Theme contrast:")
        print(f"  ink on background:    {ink_bg:5.2f}:1 (need 4.5+) {'PASS' if ink_bg >= 4.5 else 'FAIL'}")
        print(f"  accent on background: {accent_bg:5.2f}:1 (need 4.5+) {'PASS' if accent_bg >= 4.5 else 'FAIL'}")
        print(f"  muted on background:  {muted_bg:5.2f}:1 (need 3.0+) {'PASS' if muted_bg >= 3.0 else 'FAIL'}")
        if ink_bg < 4.5:
            errors.append(f"  CONTRAST: ink/background {ink_bg:.2f}:1 below 4.5:1 minimum")
        if accent_bg < 4.5:
            errors.append(f"  CONTRAST: accent/background {accent_bg:.2f}:1 below 4.5:1 minimum")
        if muted_bg < 3.0:
            errors.append(f"  CONTRAST: muted/background {muted_bg:.2f}:1 below 3.0:1 minimum")
    else:
        print("Theme: using default (no contrast check needed)")

    print()
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(e)
        return False
    print("VALIDATION PASSED")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", help="Path to scene-spec.json")
    args = parser.parse_args()
    ok = validate(args.spec)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
