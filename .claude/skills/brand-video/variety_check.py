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


def derive_signature(spec):
    d = spec.get("design", {}) or {}
    scenes = spec.get("scenes", []) or []
    tpls = [sc.get("template") for sc in scenes]
    cams = [sc.get("camera") for sc in scenes]
    bgv = d.get("background")
    bg = bgv.get("style") if isinstance(bgv, dict) else bgv
    motv = d.get("motion")
    mot = motv.get("register") if isinstance(motv, dict) else motv
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

    print(f"Signature: transition={sig['transition_style']} foley={sig['foley_style']} "
          f"bg={sig['background']} motion={sig['motion_register']}")
    print(f"           open={sig['open_template']} close={sig['close_template']} "
          f"growth={sig['has_growth_beat']}")
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
    print("\nSELFTEST PASSED (legacy-grammar repeat fails, fresh-grammar video passes)")


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
