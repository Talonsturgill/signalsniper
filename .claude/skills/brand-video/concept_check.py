#!/usr/bin/env python3
"""
Structural variety gate for the producer brain (routine v11).

Why this exists: the old `variety_check.py` rotates SURFACE parameters (color,
transition, foley, which templates) over a FIXED recipe -- open on the wordmark,
a node diagram, a terminal, a flash, close on the wordmark. Videos come out
numerically varied but PERCEPTUALLY identical: Kate Compton's "10,000 bowls of
oatmeal" problem. A viewer sees the STRUCTURE (the arc, the visual device, the
scene order), not the parameters decorating it.

This gate operates on the CONCEPT the producer phase commits to -- a structural
feature vector -- and refuses a video whose SHAPE repeats recent work. It is the
"a producer doesn't make two of the same movie" rule, made computable via
novelty-search-over-an-archive (Lehman & Stanley) with a Quality-Diversity
framing (Mouret & Clune). See VARIETY_ENGINE_RESEARCH.md.

The concept vector (produced by the producer's-reasoning phase, concept-DATE.json):
  arc, device, hero, open, close   -- categorical (from the banks below)
  scene_seq   -- ordered list of scene-block tokens (what's on screen, in order)
  device_seq  -- ordered list of per-scene visual devices

Distance between two concepts:
  D(A,B) = 0.45*d_cat + 0.40*d_seq + 0.15*d_set
    d_cat = Hamming over the 5 categoricals / 5
    d_seq = mean normalized Levenshtein over (scene_seq, device_seq)
    d_set = Jaccard distance over the scene_seq token SET   (the OLD weak check,
            deliberately starved to 15% so identity+order dominate)

Gate (fails the recipe-clones we ship today):
  - hard fail vs the immediately-previous video:  D(S, prev) >= 0.55
  - rolling-window novelty:  mean D to the k=4 nearest of the last 12 >= 0.50
  - absolute bans: no (arc, device) pair within 6 videos; no single categorical
    value within 3 videos.

Usage:
  concept_check.py <history.json> <concept-DATE.json>
  concept_check.py --digest <history.json>     # what's off the table this run
  concept_check.py --banks                     # print the authored banks
  concept_check.py --selftest
Exit 0 pass, 1 violation, 2 usage error.
"""

import argparse
import json
import sys
from pathlib import Path

# ---------------- THE BANKS (author as data; hold brand grammar fixed, vary these)
# node_diagram and terminal are now 2 of 12 devices, not the default -- the
# absolute (arc,device) ban + recency penalty keep them from becoming the recipe.
ARCS = [
    "pas", "before_after_bridge", "origin_build_log", "watch_it_work",
    "teardown", "sustained_metaphor", "data_story", "countdown_list",
    "question_answer", "myth_vs_reality", "what_if", "day_in_life",
    "head_to_head", "first_person_pov",
]
DEVICES = [
    "kinetic_type", "diegetic_ui", "screen_capture", "metaphor_illustration",
    "data_viz", "node_diagram", "terminal", "object_metaphor",
    "split_compare", "continuous_camera", "transformation_morph",
    "photographic_collage",
]
OPENS = [
    "cold_open_result", "question_on_black", "number_slam", "problem_friction",
    "ui_closeup", "metaphor_object_enter", "wordmark_reveal", "in_media_res",
]
CLOSES = [
    "wordmark_lockup", "call_to_look", "after_state_held", "thesis_card",
    "loop_back_to_open", "number_restated", "builder_credit", "punchline",
]
HEROES = [
    "speed_reveal", "scale_reveal", "side_by_side_flip", "data_spike",
    "one_command_all", "morph_complete", "impossible_possible",
    "live_counter", "elegant_output", "reaction_consequence",
]
BANKS = {"arc": ARCS, "device": DEVICES, "open": OPENS, "close": CLOSES, "hero": HEROES}
CATEGORICALS = ["arc", "device", "hero", "open", "close"]

# How each visual device maps onto the CURRENT renderer. The 6 with a template
# are buildable today (v11 #1); the 6 mapped to None need the visual-renderer
# rewrite (v11 #2 -- shader background, morph, continuous camera). Until then the
# producer's-reasoning phase must pick from renderable devices; the full bank
# still exists so the gate and the concept schema are ready when #2 lands.
REALIZATION_NOW = {
    "kinetic_type": "title", "diegetic_ui": "panes", "data_viz": "sparkline",
    "node_diagram": "diagram", "terminal": "terminal", "split_compare": "split",
    "transformation_morph": "morph",
    "screen_capture": None, "metaphor_illustration": None, "object_metaphor": None,
    "continuous_camera": None, "photographic_collage": None,
}


def renderable_devices():
    return [d for d in DEVICES if REALIZATION_NOW.get(d)]

# thresholds (see module docstring / research)
D_PREV_MIN = 0.55       # hard fail vs the previous video
NOVELTY_MIN = 0.50      # rolling-window novelty floor
NOVELTY_K = 4
ARCHIVE_N = 12
PAIR_BAN_WINDOW = 6     # (arc, device) may not repeat within N videos
CAT_BAN_WINDOW = 3      # a single categorical value may not repeat within N videos


def _levenshtein(a, b):
    a, b = list(a or []), list(b or [])
    if not a and not b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _norm_lev(a, b):
    a, b = a or [], b or []
    m = max(len(a), len(b))
    return (_levenshtein(a, b) / m) if m else 0.0


def d_cat(A, B):
    return sum(1 for k in CATEGORICALS if A.get(k) != B.get(k)) / len(CATEGORICALS)


def d_seq(A, B):
    s = _norm_lev(A.get("scene_seq"), B.get("scene_seq"))
    d = _norm_lev(A.get("device_seq"), B.get("device_seq"))
    return (s + d) / 2


def d_set(A, B):
    sa, sb = set(A.get("scene_seq") or []), set(B.get("scene_seq") or [])
    if not sa and not sb:
        return 0.0
    return 1 - len(sa & sb) / len(sa | sb)


def distance(A, B):
    return 0.45 * d_cat(A, B) + 0.40 * d_seq(A, B) + 0.15 * d_set(A, B)


def check(history_path, concept_path):
    history = json.loads(Path(history_path).read_text()) if Path(history_path).exists() else []
    S = json.loads(Path(concept_path).read_text())
    date = S.get("date")
    prior = [h for h in history if h.get("date") != date]
    fails = []

    # invalid bank values are a hard error (the producer picked something off-menu)
    for k in CATEGORICALS:
        v = S.get(k)
        if v is not None and v not in BANKS[k]:
            fails.append(f"{k}={v!r} is not in the {k} bank; pick from the authored banks (--banks)")

    if prior:
        last = prior[-1]
        d_prev = distance(S, last)
        if d_prev < D_PREV_MIN:
            fails.append(f"structure repeats the previous video ({last.get('date')}): "
                         f"D={d_prev:.2f} < {D_PREV_MIN} "
                         f"(d_cat={d_cat(S,last):.2f} d_seq={d_seq(S,last):.2f} d_set={d_set(S,last):.2f}). "
                         "Change the arc/device/hero/open/close or the scene ORDER -- not just the palette.")

        window = prior[-ARCHIVE_N:]
        dists = sorted(distance(S, v) for v in window)
        k = min(NOVELTY_K, len(dists))
        novelty = sum(dists[:k]) / k if k else 1.0
        if novelty < NOVELTY_MIN:
            fails.append(f"too close to recent work: novelty={novelty:.2f} < {NOVELTY_MIN} "
                         f"(mean distance to the {k} nearest of the last {len(window)}). "
                         "This concept sits in a crowded region of the form-space; move it.")

        # absolute (arc, device) pair ban within PAIR_BAN_WINDOW
        recent_pairs = [(v.get("arc"), v.get("device")) for v in prior[-PAIR_BAN_WINDOW:]]
        if (S.get("arc"), S.get("device")) in recent_pairs:
            fails.append(f"(arc={S.get('arc')}, device={S.get('device')}) was used within the last "
                         f"{PAIR_BAN_WINDOW} videos; that exact pairing is the recipe -- change one.")

        # single categorical value ban within CAT_BAN_WINDOW
        for kcat in CATEGORICALS:
            recent_vals = [v.get(kcat) for v in prior[-CAT_BAN_WINDOW:]]
            if S.get(kcat) in recent_vals:
                fails.append(f"{kcat}={S.get(kcat)!r} was used within the last {CAT_BAN_WINDOW} videos; "
                             f"rotate it (bank has {len(BANKS[kcat])} options).")

    print(f"Concept: arc={S.get('arc')} device={S.get('device')} hero={S.get('hero')} "
          f"open={S.get('open')} close={S.get('close')}")
    print(f"         scene_seq={S.get('scene_seq')}")
    print(f"History: {len(prior)} prior concepts")
    if fails:
        print()
        for f in fails:
            print(f"  FAIL: {f}")
        print("\nCONCEPT CHECK FAILED (the shape repeats recent work)")
        return False
    print("\nCONCEPT CHECK PASSED (a genuinely different shape)")
    return True


def digest(history_path, n=ARCHIVE_N):
    history = json.loads(Path(history_path).read_text()) if Path(history_path).exists() else []
    recent = history[-n:]
    print("RECENT CONCEPTS (most recent last) -- do NOT repeat these shapes:")
    for e in recent:
        print(f"  {str(e.get('date')):12} arc={str(e.get('arc')):20} device={str(e.get('device')):22} "
              f"hero={str(e.get('hero')):18} open={str(e.get('open')):18} close={e.get('close')}")
    last3 = history[-CAT_BAN_WINDOW:]
    last6 = history[-PAIR_BAN_WINDOW:]
    banned = {k: sorted({v.get(k) for v in last3 if v.get(k)}) for k in CATEGORICALS}
    banned_pairs = sorted({(v.get("arc"), v.get("device")) for v in last6 if v.get("arc")})
    print("\nOFF THE TABLE this run:")
    for k in CATEGORICALS:
        free = [x for x in BANKS[k] if x not in banned[k]]
        print(f"  {k:7}: avoid {banned[k]}  -> choose from {free}")
    print(f"  (arc,device) pairs banned (last {PAIR_BAN_WINDOW}): {banned_pairs}")
    print("\nCommit to an arc+device+hero+open+close and a scene ORDER that is unlike the last video "
          f"(D >= {D_PREV_MIN}) and not crowded against the last {n} (novelty >= {NOVELTY_MIN}).")


def backfill(out_path="reports/concept-history.json", keep=40):
    """Rebuild the series-memory archive from reports/concept-*.json (the shipped
    concepts). The gate and the producer digest read this."""
    import glob
    import re
    def key(p):
        m = re.search(r"concept-(\d{4}-\d{2}-\d{2}\w?)", p)
        return m.group(1) if m else p
    files = [f for f in sorted(glob.glob("reports/concept-*.json"), key=key)
             if "concept-history" not in f]
    out = []
    for f in files:
        try:
            c = json.loads(Path(f).read_text())
            out.append({k: c.get(k) for k in (["date"] + CATEGORICALS + ["scene_seq", "device_seq"])})
        except Exception as e:
            print(f"  skip {f}: {e}")
    out = out[-keep:]
    Path(out_path).write_text(json.dumps(out, indent=2))
    print(f"wrote {out_path} with {len(out)} concepts (from {len(files)} files)")


def selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="concept_"))
    # the legacy recipe, shipped twice
    legacy = {"arc": "pas", "device": "node_diagram", "hero": "live_counter",
              "open": "wordmark_reveal", "close": "wordmark_lockup",
              "scene_seq": ["WORDMARK", "DIAGRAM", "TERMINAL", "FLASH", "WORDMARK"],
              "device_seq": ["kinetic_type", "node_diagram", "terminal", "kinetic_type", "kinetic_type"]}
    hist = [dict(legacy, date="d1"), dict(legacy, date="d2")]
    hp = tmp / "h.json"; hp.write_text(json.dumps(hist))
    # a clone of the recipe must HARD-FAIL
    clone = dict(legacy, date="d3")
    cp = tmp / "clone.json"; cp.write_text(json.dumps(clone))
    assert check(str(hp), str(cp)) is False, "a recipe clone must fail the structural gate"
    # a genuinely different shape must PASS
    fresh = {"date": "d3", "arc": "before_after_bridge", "device": "transformation_morph",
             "hero": "morph_complete", "open": "cold_open_result", "close": "loop_back_to_open",
             "scene_seq": ["COLD_RESULT", "THE_BEFORE", "THE_MORPH", "HERO_COMPLETE", "THESIS"],
             "device_seq": ["transformation_morph", "split_compare", "transformation_morph",
                            "transformation_morph", "kinetic_type"]}
    fp = tmp / "fresh.json"; fp.write_text(json.dumps(fresh))
    assert check(str(hp), str(fp)) is True, "a genuinely different concept must pass"
    # off-menu value is a hard error
    bad = dict(fresh, device="hologram")
    bp = tmp / "bad.json"; bp.write_text(json.dumps(bad))
    assert check(str(hp), str(bp)) is False, "an off-bank device must fail"
    # one categorical changed but same recipe otherwise -> still too close (fails)
    near = dict(legacy, date="d3", hero="scale_reveal")   # only hero differs
    npth = tmp / "near.json"; npth.write_text(json.dumps(near))
    assert check(str(hp), str(npth)) is False, "changing one categorical off a clone is not enough"
    print("\nSELFTEST PASSED (recipe clone fails, off-menu fails, one-tweak-of-a-clone fails, fresh shape passes)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("history", nargs="?")
    p.add_argument("concept", nargs="?")
    p.add_argument("--digest", action="store_true")
    p.add_argument("--banks", action="store_true")
    p.add_argument("--backfill", action="store_true")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        selftest(); return
    if args.backfill:
        backfill(); return
    if args.banks:
        out = {k: v for k, v in BANKS.items()}
        out["_device_renderable_now"] = renderable_devices()
        out["_device_needs_visual_rewrite_v11_#2"] = [d for d in DEVICES if not REALIZATION_NOW.get(d)]
        print(json.dumps(out, indent=2)); return
    if args.digest:
        if not args.history:
            p.error("--digest needs <history.json>")
        digest(args.history); return
    if not (args.history and args.concept):
        p.error("need <history.json> <concept.json>, or --digest / --banks / --selftest")
    sys.exit(0 if check(args.history, args.concept) else 1)


if __name__ == "__main__":
    main()
