#!/usr/bin/env python3
"""
Variety / signature enforcer for the daily-tribute pipeline (routine v8).

Why this exists: the old anti-repeat only rotated framework, palette and music.
Everything a viewer actually FEELS as "the same automation" was unconstrained --
the transition treatment (a scale-kick on every cut), the foley swipe (a
byte-identical whoosh), the structural shape (open on a wordmark, product beat,
star-count, close), and the camera grammar. Across 10 straight videos: `close`
closed 10/10, a title/logo opened 9/10, a star-count beat ran 9/10. That reads
as a template, not a producer.

This gate derives a per-video SIGNATURE and refuses a video whose grammar repeats
recent work. It runs alongside anti_repeat_check, at storyboard/spec time.

The craft it encodes (real editing/sound grammar):
- The hard cut is the invisible default; stylized boundaries are reserved and
  VARIED. No transition treatment may recur within ~a work-week.
- The foley family (whoosh+hit vs riser+braam vs tape-stop+drop vs click-minimal
  vs sub-impact vs reverse-swell) rotates; a swipe is not on every video.
- Structure varies: the open slot, the close slot, the template mix, the camera
  mix, and the presence of an on-screen metric are not allowed to become fixtures.

Usage:
    variety_check.py reports/variety-history.json reports/scene-spec-DATE.json
    variety_check.py --backfill            # rebuild the ledger from reports/scene-spec-*.json
    variety_check.py --signature reports/scene-spec-DATE.json   # print one signature
    variety_check.py --selftest

Exit 0 pass, 1 violation, 2 usage error.
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path

GROWTH_TEMPLATES = {"sparkline", "big_number"}
# Legacy videos predate transition_style/foley_style; they were, in fact, always
# these two. Recording that truthfully is what forces the NEXT video off them.
LEGACY_TRANSITION = "cut_kick"
LEGACY_FOLEY = "whoosh_thud"

TRANSITION_LOOKBACK = 4     # a transition treatment may not recur within N videos
FOLEY_LOOKBACK = 4          # a foley family may not recur within N videos

# The palettes the producer chooses from (kept in sync with build_html /
# synth_audio). A boundary treatment and a transient family per video.
TRANSITION_STYLES = ("hard_cut", "cut_kick", "glitch", "push", "dip", "bloom")
FOLEY_STYLES = ("whoosh_thud", "riser_braam", "tapestop_drop",
                "click_minimal", "sub_impact", "reverse_swell")

# ---------------- color anti-repeat (routine v10) ----------------------------
# The old signature rotated framework/background/template/camera but had NO color
# dimension, so three near-black + hot-orange videos shipped back to back and the
# gate passed every time (2026-07-04 caveman #ff7f33, 07-04c mcp-use #ff7f33,
# 07-05 t3mp3st #ff7a61). Two consecutive videos must not READ as the same
# palette. Research-grounded thresholds (see CINEMATIC_RESEARCH.md): a dominant/
# accent reads as GENUINELY different when it rotates >= 60 deg on the hue wheel
# (past the 30-60 deg "analogous / same family" band; workwithcolor) AND ΔE00 >= 11
# (past Zschuessler's "more different than similar" boundary). A canvas value flip
# (dark<->light) or an accent temperature flip (warm<->cool) is an alternative,
# equally-visible way to differ -- so a legitimately-orange brand can still ship
# next to another orange one by flipping the canvas or temperature instead.
COLOR_HUE_MIN = 60.0      # degrees, circular hue distance of the accent
COLOR_DE00_MIN = 11.0     # CIEDE2000 of the accent


def _hex_rgb(h):
    h = (h or "").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    except ValueError:
        return None


def _luma(h):
    rgb = _hex_rgb(h)
    if not rgb:
        return None
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hue_deg(h):
    rgb = _hex_rgb(h)
    if not rgb:
        return None
    r, g, b = rgb
    mx, mn = max(rgb), min(rgb)
    if mx == mn:
        return None                 # achromatic: no hue
    d = mx - mn
    if mx == r:
        hh = ((g - b) / d) % 6
    elif mx == g:
        hh = (b - r) / d + 2
    else:
        hh = (r - g) / d + 4
    return (hh * 60.0) % 360.0


def _hue_dist(a, b):
    if a is None or b is None:
        return 180.0                # one is achromatic: treat as maximally distinct
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _temp(h):
    hue = _hue_deg(h)
    if hue is None:
        return "neutral"
    return "warm" if (hue < 90 or hue >= 330) else "cool"


def _value_bucket(h):
    l = _luma(h)
    if l is None:
        return "mid"
    return "dark" if l < 0.42 else ("light" if l > 0.62 else "mid")


def _srgb_to_lab(h):
    rgb = _hex_rgb(h)
    if not rgb:
        return None

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t):
        return t ** (1.0 / 3) if t > 0.008856 else (7.787 * t + 16.0 / 116)
    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _delta_e00(lab1, lab2):
    """CIEDE2000 perceptual color difference."""
    import math
    if not lab1 or not lab2:
        return 100.0
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    avg_Lp = (L1 + L2) / 2
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    avg_C = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(avg_C ** 7 / (avg_C ** 7 + 25 ** 7))) if avg_C > 0 else 0.0
    a1p, a2p = a1 * (1 + G), a2 * (1 + G)
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)

    def hp(ap, bp):
        if ap == 0 and bp == 0:
            return 0.0
        h = math.degrees(math.atan2(bp, ap))
        return h + 360 if h < 0 else h
    h1p, h2p = hp(a1p, b1), hp(a2p, b2)
    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360
    else:
        dhp = h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)
    if C1p * C2p == 0:
        avg_hp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        avg_hp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        avg_hp = (h1p + h2p + 360) / 2
    else:
        avg_hp = (h1p + h2p - 360) / 2
    avg_Cp = (C1p + C2p) / 2
    T = (1 - 0.17 * math.cos(math.radians(avg_hp - 30))
         + 0.24 * math.cos(math.radians(2 * avg_hp))
         + 0.32 * math.cos(math.radians(3 * avg_hp + 6))
         - 0.20 * math.cos(math.radians(4 * avg_hp - 63)))
    d_ro = 30 * math.exp(-(((avg_hp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(avg_Cp ** 7 / (avg_Cp ** 7 + 25 ** 7)) if avg_Cp > 0 else 0.0
    Sl = 1 + (0.015 * (avg_Lp - 50) ** 2) / math.sqrt(20 + (avg_Lp - 50) ** 2)
    Sc = 1 + 0.045 * avg_Cp
    Sh = 1 + 0.015 * avg_Cp * T
    Rt = -math.sin(math.radians(2 * d_ro)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


def color_distinct(this, prev):
    """Do these two videos read as different palettes? (ok, reason)."""
    dh = _hue_dist(this.get("accent_hue"), prev.get("accent_hue"))
    de = _delta_e00(_srgb_to_lab(this.get("accent_hex")),
                    _srgb_to_lab(prev.get("accent_hex")))
    if dh >= COLOR_HUE_MIN and de >= COLOR_DE00_MIN:
        return True, f"accent differs (Δhue {dh:.0f}deg, ΔE00 {de:.0f})"
    if this.get("canvas_value") != prev.get("canvas_value"):
        return True, f"canvas value flips {prev.get('canvas_value')}->{this.get('canvas_value')}"
    if this.get("temp") != prev.get("temp"):
        return True, f"temperature flips {prev.get('temp')}->{this.get('temp')}"
    return False, (f"accent too close to {prev.get('date', 'prev')} "
                   f"(Δhue {dh:.0f}deg < {COLOR_HUE_MIN:.0f}, ΔE00 {de:.0f} < {COLOR_DE00_MIN:.0f}), "
                   f"same canvas value ({this.get('canvas_value')}) and temperature ({this.get('temp')})")


def derive_signature(spec):
    d = spec.get("design", {}) or {}
    scenes = spec.get("scenes", []) or []
    tpls = [sc.get("template") for sc in scenes]
    cams = [sc.get("camera") for sc in scenes]
    bgv = d.get("background")
    bg = bgv.get("style") if isinstance(bgv, dict) else bgv
    motv = d.get("motion")
    mot = motv.get("register") if isinstance(motv, dict) else motv
    tokens = d.get("tokens", {}) or {}
    accent = tokens.get("accent")
    canvas = tokens.get("canvas")
    return {
        "date": spec.get("date"),
        "project_url": spec.get("project_url") or spec.get("project"),
        "framework": d.get("framework"),
        "background": bg,
        "motion_register": mot,
        "transition_style": d.get("transition_style", LEGACY_TRANSITION),
        "foley_style": d.get("foley_style", LEGACY_FOLEY),
        "open_template": tpls[0] if tpls else None,
        "close_template": tpls[-1] if tpls else None,
        "templates": sorted(set(t for t in tpls if t)),
        "cameras": sorted(set(c for c in cams if c)),
        "has_growth_beat": any(t in GROWTH_TEMPLATES for t in tpls),
        # color fingerprint (v10)
        "accent_hex": accent,
        "canvas_hex": canvas,
        "accent_hue": _hue_deg(accent),
        "temp": _temp(accent),
        "canvas_value": _value_bucket(canvas),
    }


def jaccard(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def _count_slot(entries, slot, value):
    return sum(1 for e in entries if e.get(slot) == value)


def check(history_path, spec_path):
    history = json.loads(Path(history_path).read_text()) if Path(history_path).exists() else []
    spec = json.loads(Path(spec_path).read_text())
    sig = derive_signature(spec)
    today = sig["date"]
    prior = [h for h in history if h.get("date") != today]

    fails, notes = [], []
    last = prior[-1] if prior else None
    last2 = prior[-2] if len(prior) >= 2 else None
    last3 = prior[-3:]
    last4 = prior[-4:]

    # 1. transition treatment must not recur within the lookback window
    recent_tr = [e.get("transition_style") for e in prior[-TRANSITION_LOOKBACK:]]
    if sig["transition_style"] in recent_tr:
        fails.append(f"transition_style {sig['transition_style']!r} used within the last "
                     f"{TRANSITION_LOOKBACK} videos {recent_tr}; pick a treatment not in that set")

    # 2. foley family must not recur within the lookback window
    recent_fo = [e.get("foley_style") for e in prior[-FOLEY_LOOKBACK:]]
    if sig["foley_style"] in recent_fo:
        fails.append(f"foley_style {sig['foley_style']!r} used within the last "
                     f"{FOLEY_LOOKBACK} videos {recent_fo}; pick a different transient family")

    # 3. background must not equal the immediately-previous video
    if last and sig["background"] and sig["background"] == last.get("background"):
        fails.append(f"background {sig['background']!r} matches the previous video; vary the field")

    # 4. motion register must not equal the previous video
    if last and sig["motion_register"] and sig["motion_register"] == last.get("motion_register"):
        fails.append(f"motion_register {sig['motion_register']!r} matches the previous video")

    # 5/6. an open/close template may not occupy its slot in >=2 of the last 3
    if last3:
        oc = _count_slot(last3, "open_template", sig["open_template"])
        if oc >= 2:
            fails.append(f"open_template {sig['open_template']!r} already opened {oc} of the last 3 "
                         "videos; the opening shape is becoming a fingerprint")
        cc = _count_slot(last3, "close_template", sig["close_template"])
        if cc >= 2:
            fails.append(f"close_template {sig['close_template']!r} already closed {cc} of the last 3 "
                         "videos; find a different ending beat")

    # 7. template mix must not be a near-copy of the previous video
    if last:
        j = jaccard(sig["templates"], last.get("templates", []))
        if j > 0.6:
            fails.append(f"template mix is {j:.0%} the same as the previous video (>60%); "
                         "compose a genuinely different set of shots")

    # 8. must bring at least one template neither of the last 2 videos used
    if last:
        seen = set(last.get("templates", [])) | set(last2.get("templates", []) if last2 else [])
        fresh = set(sig["templates"]) - seen
        if not fresh:
            fails.append("no new template vs the last 2 videos; bring at least one shot the "
                         "recent videos did not use")

    # 9. camera grammar must not be a near-copy of the previous video
    if last:
        jc = jaccard(sig["cameras"], last.get("cameras", []))
        if jc > 0.7:
            fails.append(f"camera mix is {jc:.0%} the same as the previous video (>70%); "
                         "re-choose the camera moves")

    # 10. an on-screen growth/metric beat may not run 3 videos in a row
    if sig["has_growth_beat"] and last and last2 and \
            last.get("has_growth_beat") and last2.get("has_growth_beat"):
        fails.append("a star-count / growth beat has run in the last 2 videos; skip the on-screen "
                     "metric this time (the scoreboard is not mandatory)")

    # 11. COLOR (v10): must not read as the same palette as either of the last 2.
    for prev in [p for p in (last, last2) if p]:
        ok, why = color_distinct(sig, prev)
        if not ok:
            hue = prev.get("accent_hue")
            hue_s = f"{hue:.0f}deg" if isinstance(hue, (int, float)) else "n/a"
            fails.append(f"color: {why}; rotate the accent hue >= {COLOR_HUE_MIN:.0f}deg off "
                         f"{hue_s}, pick a different project-native color, or flip the canvas "
                         f"value / temperature so this video does not look like the last one")

    print(f"Signature: transition={sig['transition_style']} foley={sig['foley_style']} "
          f"bg={sig['background']} motion={sig['motion_register']}")
    print(f"           open={sig['open_template']} close={sig['close_template']} "
          f"growth={sig['has_growth_beat']}")
    _hue = sig.get("accent_hue")
    print(f"           accent={sig['accent_hex']} hue={f'{_hue:.0f}deg' if isinstance(_hue,(int,float)) else 'n/a'} "
          f"temp={sig['temp']} canvas={sig['canvas_hex']}({sig['canvas_value']})")
    print(f"           templates={sig['templates']}")
    print(f"           cameras={sig['cameras']}")
    print(f"History: {len(prior)} prior videos")
    if fails:
        print()
        for f in fails:
            print(f"  FAIL: {f}")
        print("\nVARIETY CHECK FAILED")
        return False
    print("\nVARIETY CHECK PASSED")
    return True


def _spec_date_key(path):
    m = re.search(r"scene-spec-(\d{4}-\d{2}-\d{2}\w?)", path)
    return m.group(1) if m else path


def backfill(out_path="reports/variety-history.json", keep=40):
    specs = sorted(glob.glob("reports/scene-spec-*.json"), key=_spec_date_key)
    sigs = []
    for p in specs:
        try:
            sigs.append(derive_signature(json.loads(Path(p).read_text())))
        except Exception as e:
            print(f"  skip {p}: {e}")
    sigs = sigs[-keep:]
    Path(out_path).write_text(json.dumps(sigs, indent=2))
    print(f"wrote {out_path} with {len(sigs)} signatures (from {len(specs)} specs)")
    from collections import Counter
    print("  transition_style history:", dict(Counter(s["transition_style"] for s in sigs)))
    print("  foley_style history:     ", dict(Counter(s["foley_style"] for s in sigs)))
    print("  close_template history:  ", dict(Counter(s["close_template"] for s in sigs)))
    print("  growth-beat count:       ", sum(1 for s in sigs if s["has_growth_beat"]), "/", len(sigs))


def digest(history_path="reports/variety-history.json", n=6):
    """The producer's memory: what the recent videos DID, and therefore what is
    off the table this run. Read this at the creative sit-down so the storyboard
    is composed to differ, not just to satisfy the gate after the fact."""
    history = json.loads(Path(history_path).read_text()) if Path(history_path).exists() else []
    recent = history[-n:]
    print("RECENT GRAMMAR (most recent last):")
    for e in recent:
        print(f"  {e.get('date','?'):11} tr={e.get('transition_style'):10} "
              f"fo={e.get('foley_style'):13} bg={str(e.get('background')):9} "
              f"open={str(e.get('open_template')):12} close={str(e.get('close_template')):11} "
              f"growth={e.get('has_growth_beat')}")
    last = history[-1] if history else {}
    last2 = history[-2] if len(history) >= 2 else {}
    last3 = history[-3:]
    tr_used = [e.get("transition_style") for e in history[-TRANSITION_LOOKBACK:]]
    fo_used = [e.get("foley_style") for e in history[-FOLEY_LOOKBACK:]]
    blocked_open = [t for t in set(e.get("open_template") for e in last3)
                    if _count_slot(last3, "open_template", t) >= 2]
    blocked_close = [t for t in set(e.get("close_template") for e in last3)
                     if _count_slot(last3, "close_template", t) >= 2]
    must_skip_growth = bool(last.get("has_growth_beat") and last2.get("has_growth_beat"))
    print("\nOFF THE TABLE this run:")
    print(f"  transition_style: {sorted(set(tr_used))}   -> choose from {[t for t in TRANSITION_STYLES if t not in tr_used]}")
    print(f"  foley_style:      {sorted(set(fo_used))}   -> choose from {[f for f in FOLEY_STYLES if f not in fo_used]}")
    print(f"  background != {last.get('background')!r}   motion_register != {last.get('motion_register')!r}")
    print(f"  open_template avoid {blocked_open}   close_template avoid {blocked_close}")
    print(f"  on-screen star/growth beat: {'MUST SKIP (ran the last 2 videos)' if must_skip_growth else 'allowed (but earn it, not a reflex)'}")
    print("  COLOR -- do NOT let this video look like the last 2 (the #1 'same automation' tell):")
    for e in history[-2:]:
        hue = e.get("accent_hue")
        hs = f"{hue:.0f}deg" if isinstance(hue, (int, float)) else "n/a"
        print(f"      {e.get('date','?'):11} accent {str(e.get('accent_hex')):9} hue {hs:6} "
              f"{str(e.get('temp')):7} canvas {e.get('canvas_value')}")
    print(f"      -> this run's accent must sit >= {COLOR_HUE_MIN:.0f}deg off BOTH hues AND ΔE00 >= "
          f"{COLOR_DE00_MIN:.0f}, OR flip the canvas value (dark<->light) or temperature (warm<->cool). "
          "Plan >= 2 temperature beats across the runtime (a color script), not one flat wash.")
    if last.get("templates"):
        print(f"  previous template mix (stay <=60% same): {last.get('templates')}")
    print("\nBring at least one shot the last 2 videos did not use, and let the open/close "
          "shape, camera grammar, transition and foley all move off recent work.")


def selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="variety_"))
    hist = [
        {"date": "d1", "transition_style": "cut_kick", "foley_style": "whoosh_thud",
         "background": "grid", "motion_register": "fade", "open_template": "title",
         "close_template": "close", "templates": ["title", "terminal", "diagram", "close"],
         "cameras": ["push_in", "orbit", "pull_back"], "has_growth_beat": True},
        {"date": "d2", "transition_style": "cut_kick", "foley_style": "whoosh_thud",
         "background": "aurora", "motion_register": "fade", "open_template": "logo_reveal",
         "close_template": "close", "templates": ["logo_reveal", "terminal", "flash", "close"],
         "cameras": ["push_in", "crash_zoom", "pull_back"], "has_growth_beat": True},
    ]
    hp = tmp / "h.json"; hp.write_text(json.dumps(hist))
    # A spec that repeats EVERYTHING (legacy grammar) must fail.
    bad = {"date": "d3", "design": {"framework": "MANIFESTO", "background": {"style": "aurora"},
           "motion": {"register": "fade"}}, "scenes": [
        {"template": "logo_reveal", "camera": "push_in"},
        {"template": "terminal", "camera": "crash_zoom"},
        {"template": "sparkline", "camera": "dolly_up"},
        {"template": "close", "camera": "pull_back"}]}
    bp = tmp / "bad.json"; bp.write_text(json.dumps(bad))
    assert check(str(hp), str(bp)) is False
    # A spec with fresh transition+foley, different structure, no growth, new template, must pass.
    good = {"date": "d3", "design": {"framework": "MANIFESTO", "background": {"style": "starfield"},
            "motion": {"register": "cut"}, "transition_style": "dip", "foley_style": "riser_braam"},
            "scenes": [
        {"template": "wire_dispatch", "camera": "static_breathe"},
        {"template": "panes", "camera": "rack_focus"},
        {"template": "mono_block", "camera": "parallax_drift"},
        {"template": "quote", "camera": "ken_burns"}]}
    gp = tmp / "good.json"; gp.write_text(json.dumps(good))
    assert check(str(hp), str(gp)) is True

    # color gate: a near-identical dark+orange palette back-to-back must FAIL.
    hist_c = [{"date": "c1", "transition_style": "hard_cut", "foley_style": "click_minimal",
               "background": "grid", "motion_register": "cut", "open_template": "title",
               "close_template": "close", "templates": ["title", "terminal"], "cameras": ["push_in"],
               "has_growth_beat": False, "accent_hex": "#ff7f33", "canvas_hex": "#0a0a0a",
               "accent_hue": _hue_deg("#ff7f33"), "temp": "warm", "canvas_value": "dark"}]
    hcp = tmp / "hc.json"; hcp.write_text(json.dumps(hist_c))
    same = {"date": "c2", "design": {"framework": "RECEIPT", "background": {"style": "starfield"},
            "motion": {"register": "fade"}, "transition_style": "glitch", "foley_style": "sub_impact",
            "tokens": {"accent": "#ff7a61", "canvas": "#0a0a0a"}},
            "scenes": [{"template": "wire_dispatch", "camera": "orbit"},
                       {"template": "mono_block", "camera": "ken_burns"}]}
    scp = tmp / "same.json"; scp.write_text(json.dumps(same))
    assert check(str(hcp), str(scp)) is False, "near-same orange-on-black must fail the color gate"
    teal = json.loads(json.dumps(same))
    teal["design"]["tokens"]["accent"] = "#18b0a0"        # cool teal: clears the gate
    tcp = tmp / "teal.json"; tcp.write_text(json.dumps(teal))
    assert check(str(hcp), str(tcp)) is True, "a teal accent (only change) must clear the color gate"

    print("\nSELFTEST PASSED (legacy-grammar repeat fails, fresh-grammar passes, "
          "same-orange color repeat fails, teal clears)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("history", nargs="?")
    p.add_argument("spec", nargs="?")
    p.add_argument("--backfill", action="store_true")
    p.add_argument("--digest", action="store_true",
                   help="print the recent-grammar digest for the creative sit-down")
    p.add_argument("--signature", help="print the signature of one scene-spec")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        selftest(); return
    if args.backfill:
        backfill(); return
    if args.digest:
        digest(args.history or "reports/variety-history.json"); return
    if args.signature:
        print(json.dumps(derive_signature(json.loads(Path(args.signature).read_text())), indent=2))
        return
    if not (args.history and args.spec):
        p.error("need <history> <spec>, or --backfill / --signature / --selftest")
    sys.exit(0 if check(args.history, args.spec) else 1)


if __name__ == "__main__":
    main()
