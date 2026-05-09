#!/usr/bin/env python3
"""
Anti-repeat pre-flight for the daily tribute pipeline.

Reads reports/style-history.json (the run ledger) and the proposed
reports/style-pick-$DATE.json (today's pick). Refuses today's pick if it
violates any of the rules in WRITING_RULES.md.

Exits 0 on pass, 1 on violation.

Usage:
    python anti_repeat_check.py reports/style-history.json reports/style-pick-2026-05-09.json
"""

import argparse
import json
import sys
from pathlib import Path

# All five frameworks the routine rotates through.
ALL_FRAMEWORKS = {"CLASSIC", "RECEIPT", "SCHEMATIC", "MANIFESTO", "DISPATCH"}

# How many days back the (brand_slug, aesthetic_slug) pair must NOT match.
PRESET_LOOKBACK = 14


def err(msg, errors): errors.append(msg)


def check(history_path, pick_path):
    history = json.loads(Path(history_path).read_text()) if Path(history_path).exists() else []
    pick = json.loads(Path(pick_path).read_text())

    today = pick.get("date")
    today_brand = pick.get("brand_slug")
    today_aesthetic = pick.get("preset_slug") or pick.get("aesthetic_slug")
    today_framework = pick.get("framework")

    # Drop any entry that's already today's date so we don't compare against ourselves.
    prior = [h for h in history if h.get("date") != today]

    errors = []

    # Framework rule
    prior_frameworks = [h.get("framework") for h in prior if h.get("framework")]
    if len(prior_frameworks) < 5:
        if today_framework in prior_frameworks:
            err(f"FRAMEWORK: {today_framework!r} already used in history "
                f"(prior: {prior_frameworks}). Pick one not yet used: "
                f"{sorted(ALL_FRAMEWORKS - set(prior_frameworks))}", errors)
    else:
        most_recent = prior_frameworks[-1] if prior_frameworks else None
        if today_framework == most_recent:
            err(f"FRAMEWORK: {today_framework!r} matches the most recent entry. "
                f"Pick anything but {most_recent!r}.", errors)

    # Preset / aesthetic rule
    recent = prior[-PRESET_LOOKBACK:]
    for h in recent:
        h_brand = h.get("brand_slug")
        h_aesth = h.get("aesthetic_slug")
        if today_brand and h_brand and today_brand == h_brand:
            err(f"BRAND: {today_brand!r} used on {h.get('date')} "
                f"(within last {PRESET_LOOKBACK} entries).", errors)
        if today_aesthetic and h_aesth and today_aesthetic == h_aesth:
            err(f"AESTHETIC: {today_aesthetic!r} used on {h.get('date')} "
                f"(within last {PRESET_LOOKBACK} entries).", errors)

    # Report
    print(f"Today: date={today}  brand={today_brand}  aesthetic={today_aesthetic}  framework={today_framework}")
    print(f"History entries: {len(prior)} prior")
    if errors:
        print()
        for e in errors:
            print(f"  FAIL: {e}")
        print("\nANTI-REPEAT CHECK FAILED")
        return False
    print("\nANTI-REPEAT CHECK PASSED")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("history")
    parser.add_argument("pick")
    args = parser.parse_args()
    ok = check(args.history, args.pick)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
