#!/usr/bin/env python3
"""
Music selector for the daily-tribute pipeline.

Reads the catalog at .claude/skills/brand-video/music/catalog.json and the
rotation ledger at .claude/skills/brand-video/music/history.json. Picks the
single best track for today's spec given:

  - the chosen preset_pack (e.g. subway-chrome, claude, geominimal)
  - the chosen framework (e.g. RECEIPT, MANIFESTO)
  - the lifetime no-repeat rule: any slug already in history.json is
    permanently disqualified

Prints the chosen track to stdout as JSON. Exits non-zero if the library is
exhausted (every slug has shipped).

Usage:
    python music_select.py --preset subway-chrome --framework RECEIPT
    python music_select.py --preset claude --framework DISPATCH --record --date 2026-05-10 --project https://github.com/foo/bar

The --record flag appends the chosen entry to history.json so tomorrow's
selector won't pick it again. The pipeline should pass --record only after
the WOW gate passes and the mux is final.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "music"
CATALOG_PATH = ROOT / "catalog.json"
HISTORY_PATH = ROOT / "history.json"


def load_catalog():
    return json.loads(CATALOG_PATH.read_text())


def load_history():
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text())


def shipped_slugs(history):
    return {h.get("slug") for h in history if h.get("slug")}


def score(track, preset, framework):
    """Higher is better. 100 for direct preset hit, 50 for framework hit."""
    s = 0
    if preset and preset in track.get("preset_packs", []):
        s += 100
    if framework and framework in track.get("frameworks", []):
        s += 50
    # Tiebreaker: shorter tracks score microscopically lower so longer/richer tracks bubble up
    s += min(track.get("duration_s", 0) / 100.0, 5.0)
    return s


def select(preset, framework, history):
    catalog = load_catalog()
    used = shipped_slugs(history)

    candidates = [t for t in catalog["tracks"] if t["slug"] not in used]
    if not candidates:
        return None, "EXHAUSTED: every slug in catalog.json has shipped. Add new tracks to the library."

    # Rank by fit score; if no candidate matches preset OR framework, fall back to any unused track
    ranked = sorted(candidates, key=lambda t: score(t, preset, framework), reverse=True)
    best = ranked[0]
    if score(best, preset, framework) == 0:
        msg = (f"WARN: no track in the catalog matches preset={preset!r} or framework={framework!r}; "
               f"falling back to first unused track {best['slug']!r}. Consider expanding the catalog.")
    else:
        msg = f"OK: picked {best['slug']!r} (score={score(best, preset, framework):.1f}, preset={preset}, framework={framework})"
    return best, msg


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preset", required=True, help="aesthetic preset slug (e.g. subway-chrome)")
    p.add_argument("--framework", required=True, help="framework name (e.g. RECEIPT)")
    p.add_argument("--record", action="store_true", help="append this pick to history.json")
    p.add_argument("--date", help="ISO date for the recorded entry (required with --record)")
    p.add_argument("--project", help="project URL for the recorded entry (required with --record)")
    args = p.parse_args()

    history = load_history()
    track, msg = select(args.preset, args.framework, history)

    if track is None:
        print(msg, file=sys.stderr)
        sys.exit(2)

    print(msg, file=sys.stderr)

    if args.record:
        if not args.date or not args.project:
            print("ERROR: --record needs --date and --project", file=sys.stderr)
            sys.exit(3)
        history.append({"date": args.date, "slug": track["slug"], "project_url": args.project})
        HISTORY_PATH.write_text(json.dumps(history, indent=2) + "\n")
        print(f"recorded {track['slug']!r} for {args.date} in history.json", file=sys.stderr)

    print(json.dumps(track, indent=2))


if __name__ == "__main__":
    main()
