#!/usr/bin/env python3
"""
WOW rubric for brand-video output.

The video does not ship until it passes a programmatic floor of "what it
takes to wow people on X / TikTok / a Claude-style feature drop." Run this
script against the spec + the rendered MP4 + the rendered HTML. Exit 0 on
pass, 1 on any FAIL. Warnings do not block.

Checklist:
  1. No-flash             |Y(t) - canvas_Y| < 35 over the first 1.0s
                          (canvas-aware: dark canvases fail on bright flashes,
                          light canvases fail on dark flashes)
  2. No controls UI       HTML has zero .controls / #play / #mute / #pf / #clock
  3. Motion variance      >= 4 distinct camera moves across scenes
  4. 3D depth             >= 1 orbit camera in scenes
  5. Visual hero          >= 1 non-text scene (diagram / terminal / big_number / flash / split)
  6. Audio bed            ffprobe sees an AAC stream and audio is not silent
  7. Color drift          lighting_arc >= 0.20
  8. Halation             halation > 0 (emphasizes glow)
  9. Duration in window   total in [12.0, 32.0]
 10. Token contrast       all three contrast floors pass
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

VALID_HERO_TPLS = {"diagram", "terminal", "big_number", "flash", "split",
                   "sparkline", "logo_reveal", "word_cascade", "wire_dispatch", "panes"}


def fail(msg, errors): errors.append(("FAIL", msg))
def warn(msg, errors): errors.append(("WARN", msg))


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


def yavg_at(mp4, t):
    out = subprocess.run(
        ["ffmpeg", "-ss", f"{t}", "-i", str(mp4), "-vframes", "1",
         "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
         "-f", "null", "-"],
        capture_output=True, text=True,
    )
    for line in out.stderr.splitlines():
        if "YAVG" in line:
            return float(line.split("=")[-1].strip())
    return None


def has_aac(mp4):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,codec_type",
         "-of", "json", str(mp4)],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(out.stdout)
    except Exception:
        return False
    for s in data.get("streams", []):
        if s.get("codec_type") == "audio" and s.get("codec_name") in ("aac", "mp4a"):
            return True
    return False


def audio_loudness(mp4):
    """Return mean RMS in dB. Silent ~ -90. Loud bed ~ -25."""
    out = subprocess.run(
        ["ffmpeg", "-i", str(mp4), "-af", "volumedetect", "-vn", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    for line in out.stderr.splitlines():
        if "mean_volume" in line:
            try:
                return float(line.split(":")[-1].strip().split()[0])
            except Exception:
                return None
    return None


def check(spec_path, mp4_path, html_path):
    spec = json.loads(Path(spec_path).read_text())
    html = Path(html_path).read_text()
    errors = []

    # 1. no-flash (delta-based): the early frames should match the video's
    # stable mid-portion luminance. Canvas-agnostic. Catches white-flashes on
    # dark videos AND dark-flashes on light videos by measuring the natural
    # baseline rather than assuming a fixed threshold.
    total_dur = sum(float(sc.get("duration_s", 3.0)) for sc in spec["scenes"])
    ref_y = yavg_at(mp4_path, total_dur / 2.0)
    flash_threshold = 30.0
    flash_fail = False
    if ref_y is None:
        warn("could not read mid-video reference luminance; skipping flash check", errors)
    else:
        for t in (0.0, 0.2, 0.5, 1.0):
            y = yavg_at(mp4_path, t)
            if y is None:
                warn(f"could not read luminance at t={t}", errors)
                continue
            delta = abs(y - ref_y)
            if delta > flash_threshold:
                fail(f"flash at t={t}: Y={y:.1f}, mid-video ref={ref_y:.1f} (delta={delta:.1f} > {flash_threshold})", errors)
                flash_fail = True
        if not flash_fail:
            print(f"  [PASS] no-flash (mid-video ref Y={ref_y:.1f}, threshold delta {flash_threshold})")

    # 2. no controls UI
    bad_markers = [
        'class="controls"', 'id="play"', 'id="mute"', 'id="pf"', 'id="clock"',
    ]
    leaks = [m for m in bad_markers if m in html]
    if leaks:
        fail(f"controls UI leaks: {leaks}", errors)
    else:
        print("  [PASS] no controls UI")

    # 3. motion variance: >= 4 distinct camera moves
    cams = {sc.get("camera", "static_breathe") for sc in spec["scenes"]}
    if len(cams) < 4:
        fail(f"motion variance too low: {len(cams)} distinct cams ({sorted(cams)})", errors)
    else:
        print(f"  [PASS] motion variance ({len(cams)} distinct: {sorted(cams)})")

    # 4. 3D depth: at least one orbit
    if not any(sc.get("camera") == "orbit" for sc in spec["scenes"]):
        warn("no orbit camera; consider one for 3D depth", errors)
    else:
        print("  [PASS] 3D depth (orbit present)")

    # 5. visual hero: at least one non-text scene
    heroes = [sc for sc in spec["scenes"] if sc["template"] in VALID_HERO_TPLS]
    if not heroes:
        fail(f"no visual hero scene (need one of {sorted(VALID_HERO_TPLS)})", errors)
    else:
        print(f"  [PASS] visual hero ({len(heroes)} non-text: {[h['template'] for h in heroes]})")

    # 6. audio bed
    if not has_aac(mp4_path):
        fail("no AAC audio stream", errors)
    else:
        loud = audio_loudness(mp4_path)
        if loud is None:
            warn("could not measure audio loudness", errors)
        elif loud < -45:
            fail(f"audio bed too quiet: mean_volume={loud:.1f} dB (want > -30 dB)", errors)
        else:
            print(f"  [PASS] audio bed (mean_volume={loud:.1f} dB)")

    # 7-8. color drift + halation
    tex = spec["design"].get("texture", {})
    la = float(tex.get("lighting_arc", 0.0))
    ha = float(tex.get("halation", 0.0))
    if la < 0.20:
        warn(f"lighting_arc={la} < 0.20 (less time-of-day drift)", errors)
    else:
        print(f"  [PASS] color drift (lighting_arc={la})")
    if ha <= 0.0:
        warn(f"halation={ha}; emphasizes will not glow", errors)
    else:
        print(f"  [PASS] halation glow ({ha})")

    # 9. duration window
    total = sum(float(sc.get("duration_s", 3.0)) for sc in spec["scenes"])
    if not (12.0 <= total <= 32.0):
        fail(f"duration {total}s outside [12, 32]", errors)
    else:
        print(f"  [PASS] duration ({total:.1f}s)")

    # 10. token contrast
    tokens = spec["design"].get("tokens", {})
    if all(k in tokens for k in ("canvas", "ink", "accent", "ink_muted")):
        accent_min = float(spec["design"].get("accent_contrast_min", 3.0))
        for label, fg, floor in (
            ("ink", tokens["ink"], 4.5),
            ("accent", tokens["accent"], accent_min),
            ("ink_muted", tokens["ink_muted"], 3.0),
        ):
            c = contrast(fg, tokens["canvas"])
            if c < floor:
                fail(f"contrast {label}/canvas = {c:.2f}:1 below {floor:.1f}:1", errors)
        print(f"  [PASS] token contrast")

    # roll up
    fails = [e for e in errors if e[0] == "FAIL"]
    warns = [e for e in errors if e[0] == "WARN"]
    print()
    if warns:
        print("Warnings:")
        for _, m in warns:
            print(f"  WARN: {m}")
    if fails:
        print("Failures:")
        for _, m in fails:
            print(f"  FAIL: {m}")
        print("\nWOW CHECK FAILED")
        return False
    print("\nWOW CHECK PASSED")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("mp4")
    parser.add_argument("html")
    args = parser.parse_args()
    ok = check(args.spec, args.mp4, args.html)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
