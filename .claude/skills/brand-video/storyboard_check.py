#!/usr/bin/env python3
"""
Pre-production gate: validates the producer brief and the director's storyboard
before any copy is written or pixels rendered. Catches story problems where
they are cheapest to fix (the board), enforcing shot-intent discipline, shot
variety, the money shot, and the energy arc.

Usage:
    python storyboard_check.py reports/producer-brief-DATE.json \
        reports/storyboard-DATE.json [--spec reports/scene-spec-DATE.json]

Exit 0 on pass, 1 on any failure. --spec cross-checks that the written spec
kept the board's template sequence (timing lock discipline).
"""

import argparse
import json
import sys
from pathlib import Path

HERO_TPLS = {"diagram", "terminal", "big_number", "flash", "split",
             "sparkline", "logo_reveal", "word_cascade", "wire_dispatch"}
VALID_TEMPLATES = HERO_TPLS | {"title", "stack", "two_line", "three_line",
                               "fix", "mono_block", "quote", "close"}
VALID_CAMERAS = {"push_in", "pull_back", "ken_burns", "crash_zoom", "orbit",
                 "parallax_drift", "static_breathe", "rack_focus", "dolly_up",
                 "tilt_reveal", "none"}
VALID_FRAMEWORKS = {"CLASSIC", "RECEIPT", "SCHEMATIC", "MANIFESTO", "DISPATCH"}

BRIEF_REQUIRED = ["audience", "single_takeaway", "viewer_action",
                  "desired_feeling", "tone_adjectives", "references",
                  "success_criteria", "platform"]
SCENE_REQUIRED = ["intent", "template", "camera", "copy_note", "sound_cue", "energy"]


def check_brief(brief, errors):
    for f in BRIEF_REQUIRED:
        if f not in brief or brief[f] in (None, "", []):
            errors.append(f"BRIEF: missing field {f!r}")
    takeaway = brief.get("single_takeaway", "")
    if len(takeaway) > 160:
        errors.append(f"BRIEF: single_takeaway is {len(takeaway)} chars; if you can't say it in one sentence the brief isn't ready")
    if takeaway.count(".") > 1:
        errors.append("BRIEF: single_takeaway must be ONE sentence")
    tones = brief.get("tone_adjectives", [])
    if not (2 <= len(tones) <= 4):
        errors.append(f"BRIEF: tone_adjectives needs 2-4 entries, got {len(tones)}")
    if brief.get("platform") != "x":
        errors.append(f"BRIEF: platform must be 'x', got {brief.get('platform')!r}")


def check_board(board, errors, warnings):
    fw = board.get("framework")
    if fw not in VALID_FRAMEWORKS:
        errors.append(f"BOARD: framework {fw!r} invalid")
    scenes = board.get("scenes", [])
    if not (4 <= len(scenes) <= 8):
        errors.append(f"BOARD: needs 4-8 scenes, got {len(scenes)}")

    money = [i for i, s in enumerate(scenes) if s.get("money_shot")]
    if len(money) != 1:
        errors.append(f"BOARD: exactly one money_shot required, got {len(money)}")
    elif scenes:
        pos = money[0] / max(1, len(scenes) - 1)
        if not (0.45 <= pos <= 0.9):
            warnings.append(f"BOARD: money shot at scene {money[0] + 1}/{len(scenes)} "
                            f"(pos {pos:.0%}); the peak belongs at 60-80% of runtime")

    tpls, cams = set(), set()
    for i, s in enumerate(scenes):
        for f in SCENE_REQUIRED:
            if f not in s or s[f] in (None, ""):
                errors.append(f"BOARD scene {i}: missing {f!r}")
        tpl = s.get("template")
        if tpl not in VALID_TEMPLATES:
            errors.append(f"BOARD scene {i}: unknown template {tpl!r}")
        tpls.add(tpl)
        cam = s.get("camera")
        if cam not in VALID_CAMERAS:
            errors.append(f"BOARD scene {i}: unknown camera {cam!r}")
        cams.add(cam)
        intent = s.get("intent", "")
        if intent and (len(intent) < 12 or intent.strip().lower() == str(tpl).lower()):
            errors.append(f"BOARD scene {i}: intent must state the shot's JOB, not its template name")
        energy = s.get("energy")
        if energy is not None and not (0.0 <= float(energy) <= 1.0):
            errors.append(f"BOARD scene {i}: energy {energy} outside 0..1")

    if len(tpls) < 4:
        errors.append(f"BOARD: only {len(tpls)} distinct templates ({sorted(tpls)}); a director plans shot variety, need 4+")
    if len(cams) < 4:
        errors.append(f"BOARD: only {len(cams)} distinct cameras ({sorted(cams)}); need 4+")
    if not (tpls & HERO_TPLS):
        errors.append("BOARD: no visual-hero template on the board")

    energies = [float(s.get("energy", 0)) for s in scenes if s.get("energy") is not None]
    if len(energies) == len(scenes) and len(scenes) >= 4:
        peak_i = energies.index(max(energies))
        pos = peak_i / (len(scenes) - 1)
        if not (0.4 <= pos <= 0.9):
            warnings.append(f"BOARD: energy curve peaks at scene {peak_i + 1} (pos {pos:.0%}); aim for 60-80%")
        if energies[0] >= max(energies):
            warnings.append("BOARD: energy starts at the peak; leave room to build")


def check_spec_lock(board, spec, errors):
    b_seq = [s.get("template") for s in board.get("scenes", [])]
    s_seq = [s.get("template") for s in spec.get("scenes", [])]
    if b_seq != s_seq:
        errors.append(f"TIMING LOCK: spec template sequence {s_seq} diverged from board {b_seq}; "
                      "re-board first, don't improvise structure at the writing desk")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("brief")
    p.add_argument("board")
    p.add_argument("--spec", help="optional scene-spec to cross-check the timing lock")
    args = p.parse_args()

    brief = json.loads(Path(args.brief).read_text())
    board = json.loads(Path(args.board).read_text())
    errors, warnings = [], []
    check_brief(brief, errors)
    check_board(board, errors, warnings)
    if args.spec:
        spec = json.loads(Path(args.spec).read_text())
        check_spec_lock(board, spec, errors)

    for w in warnings:
        print(f"  WARN: {w}")
    if errors:
        for e in errors:
            print(f"  FAIL: {e}")
        print("\nSTORYBOARD CHECK FAILED")
        sys.exit(1)
    print("\nSTORYBOARD CHECK PASSED"
          + (f" ({len(warnings)} warning(s))" if warnings else ""))


if __name__ == "__main__":
    main()
