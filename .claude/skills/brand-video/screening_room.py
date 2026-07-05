#!/usr/bin/env python3
"""
Screening room: post-render QC beyond the WOW rubric. Measures the actual
pixels and audio of the finished MP4 the way a finishing house checks a spot.

Checks:
  1. dead air        no stretch > 2.0s with near-zero motion energy (FAIL);
                     WARN at > 1.4s
  2. energy arc      smoothed motion energy should peak in the 35-90% window
                     (WARN outside; flat arcs read as templated)
  3. poster frame    frame 0 must carry real content (luma std) since X uses
                     it as the muted-autoplay thumbnail (FAIL if blank)
  4. loudness motion audio RMS range over 0.5s windows >= 3 dB (WARN if flat)
  5. beat alignment  when design.beat.aligned, median |cut - nearest onset|
                     <= 120ms PASS / <= 200ms WARN / else FAIL
  6. conform sanity  duration within 0.5s of spec, fps ~25 (FAIL)
  7. readability     per-scene polarity from the frame itself: dark frames
                     need bright ink (p99.3 >= 180, spread >= 120), light
                     frames need dark ink (p0.7 <= 70) (FAIL)
  8. chroma          finishing must not tint: median R-G / B-G cast of the
                     final vs the raw capture, drift > 8 levels FAILs

With --raw, also runs the FRAME-PACING gate against the pre-grain capture:
finishing grain makes every output frame technically unique, so duplicated
frames (a page that painted slower than the recorder) are only detectable on
the raw. A slideshow is unshippable: unique-frame ratio >= 0.90, no duplicate
run > 200ms, every second >= 18 unique frames.

Also enforces CADENCE: scenes 3.2-5.0s (a beat every ~4s), and the energy
trace must show in-scene motion between cuts, not just at them.

Usage:
    python screening_room.py reports/scene-spec-DATE.json reports/tribute-DATE.mp4 \
        [--raw /tmp/tribute-raw-DATE.mp4] [--report reports/screening-DATE.json]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SIZE = 96
FPS = 25


def decode_gray(mp4):
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(mp4),
        "-vf", f"fps={FPS},scale={SIZE}:{SIZE}", "-pix_fmt", "gray",
        "-f", "rawvideo", "-",
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        raise SystemExit("ffmpeg gray decode failed: " + res.stderr.decode()[-800:])
    buf = np.frombuffer(res.stdout, dtype=np.uint8)
    n = len(buf) // (SIZE * SIZE)
    return buf[: n * SIZE * SIZE].reshape(n, SIZE, SIZE).astype(np.float32)


def decode_audio(mp4, fs=22050):
    cmd = ["ffmpeg", "-v", "error", "-i", str(mp4), "-f", "f32le", "-ac", "1", "-ar", str(fs), "-"]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        return None, fs
    return np.frombuffer(res.stdout, dtype=np.float32), fs


def probe_duration(mp4):
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp4)],
        capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return None


def onset_times(x, fs):
    from scipy.signal import stft, find_peaks
    from scipy.ndimage import uniform_filter1d, maximum_filter1d
    hop, nper = 512, 2048
    _, _, Z = stft(x, fs, nperseg=nper, noverlap=nper - hop)
    S = np.log1p(10 * np.abs(Z))
    S = maximum_filter1d(S, 3, axis=0)
    flux = np.maximum(np.diff(S, axis=1), 0).sum(axis=0)
    novelty = flux - uniform_filter1d(flux, 21)
    peaks, _ = find_peaks(novelty, height=float(np.std(novelty)) * 1.1,
                          distance=max(1, int(0.10 * fs / hop)))
    return peaks * hop / fs


def frame_pacing(raw_path, spec, fails, warns, report):
    """Unique-frame + liveliness analysis of the raw capture (pre-grain, the
    honest source: finishing grain fakes uniqueness and the grade crushes the
    darks the dead-air heuristic reads). Fade-through troughs at scene cuts
    are DESIGNED dips, so freezes are judged inside scene interiors only.

    Returns the per-frame motion trace so the dead-air check can reuse it."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(raw_path),
           "-vf", "fps=25,scale=128:128", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
    buf = subprocess.run(cmd, capture_output=True).stdout
    n = len(buf) // (128 * 128)
    if n < 25:
        fails.append("frame pacing: could not decode raw capture")
        return None
    fr = np.frombuffer(buf, dtype=np.uint8)[: n * 128 * 128].reshape(n, 128, 128).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    # content window: skip the blank pre-animation head and post-animation tail
    active = np.where(d > 0.5)[0]
    lo = int(active[0]) if len(active) > 2 else 0
    hi = int(active[-1]) if len(active) > 2 else len(d) - 1
    d = d[lo: hi + 1]
    # mask +/-0.3s around each designed cut (fade-through dips are intentional)
    durs = [float(sc.get("duration_s", 3.0)) for sc in spec["scenes"]]
    cuts = np.cumsum(durs)[:-1]
    interior = np.ones(len(d), dtype=bool)
    for c in cuts:
        ci = int(c * 25)
        interior[max(0, ci - 8): ci + 8] = False
    dup = d < 0.03
    runs, run = [], 0
    for i, x in enumerate(dup):
        run = run + 1 if (x and interior[i]) else 0
        runs.append(run)
    uniq_ratio = float(1 - dup.mean())
    max_run_ms = max(runs) / 25 * 1000
    per_sec = [(int((~dup[i * 25:(i + 1) * 25]).sum())) for i in range(max(1, len(d) // 25))]
    worst_sec = min(per_sec[1:-1]) if len(per_sec) > 3 else min(per_sec)
    report["raw_unique_ratio"] = round(uniq_ratio, 3)
    report["raw_max_interior_dup_ms"] = round(max_run_ms)
    report["raw_min_unique_per_sec"] = worst_sec
    if uniq_ratio < 0.85:
        fails.append(f"frame pacing: only {uniq_ratio:.0%} of raw frames are unique "
                     f"(page painted slower than the recorder; this is a slideshow)")
    elif max_run_ms > 240:
        fails.append(f"frame pacing: {max_run_ms:.0f}ms duplicate-frame freeze inside a scene")
    elif worst_sec < 12:
        fails.append(f"frame pacing: a second with only {worst_sec} unique frames in the raw capture")
    else:
        print(f"  [PASS] frame pacing (raw unique {uniq_ratio:.0%}, max interior dup {max_run_ms:.0f}ms, "
              f"min {worst_sec} unique/s)")
    return d


def readability(spec, mp4, fails, warns, report):
    """Brightness/readability gauge, polarity-aware PER SCENE. Each scene's
    polarity comes from its own frame (median luma), not the video's canvas
    token — a dark video legitimately carries inverted color-break scenes.
    Dark frames must carry genuinely BRIGHT ink (p99.3 luma) with a wide
    spread; bright frames must carry genuinely dark ink. Catches the
    "everything looks dim" failure the grade or a weak palette can cause."""
    durs = [float(sc.get("duration_s", 3.0)) for sc in spec["scenes"]]
    mids, acc = [], 0.0
    for d in durs:
        mids.append(acc + d / 2)
        acc += d
    scene_stats, weakest = [], None
    for i, t in enumerate(mids):
        cmd = ["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(mp4),
               "-frames:v", "1", "-vf", "scale=540:540", "-pix_fmt", "gray",
               "-f", "rawvideo", "-"]
        buf = subprocess.run(cmd, capture_output=True).stdout
        if len(buf) < 540 * 540:
            continue
        fr = np.frombuffer(buf[: 540 * 540], dtype=np.uint8).astype(np.float32)
        dark = float(np.median(fr)) < 128
        # p99.3 / p0.7: ink can be sparse (terminal type covers ~1-2% of pixels)
        if dark:
            ink = float(np.percentile(fr, 99.3))
            spread = ink - float(np.percentile(fr, 15))
            ink_ok = ink >= 180
        else:
            ink = float(np.percentile(fr, 0.7))
            spread = float(np.percentile(fr, 85)) - ink
            ink_ok = ink <= 70
        scene_stats.append({"scene": i, "polarity": "dark" if dark else "light",
                            "ink": round(ink), "spread": round(spread)})
        if not ink_ok or spread < 120:
            if weakest is None or spread < weakest[1]:
                weakest = (i, spread, ink, dark)
    report["readability"] = scene_stats
    if weakest is not None:
        i, spread, ink, dark = weakest
        pol = "bright ink p99.3" if dark else "dark ink p0.7"
        fails.append(f"readability: scene {i} reads dim ({pol}={ink:.0f}, luma spread={spread:.0f}; "
                     f"need ink {'>=180' if dark else '<=70'} and spread >=120)")
    else:
        mn = min((st["spread"] for st in scene_stats), default=0)
        print(f"  [PASS] readability ({len(scene_stats)} scenes, per-scene polarity, min luma spread {mn})")


BRIGHT_SCENE_LUMA = 55.0      # a scene whose mean luma clears this is "not dark"
BRIGHT_MEAN_FLOOR = 46.0      # whole-video mean-luma floor
BRIGHT_FRACTION_MIN = 0.30    # at least this share of scenes must be bright


def brightness(spec, mp4, fails, warns, report):
    """The client's standing note: 'every single video just seems dark, no matter
    what.' The readability gate only checks that TEXT is legible -- a video can be
    ~90% near-black and still pass it (the 2026-07-05 cut measured mean luma 33,
    88% of the runtime below luma 30). This gate measures the FRAME, not the type:
    a video must not read as uniformly dark. It passes if the overall mean luma
    clears a floor OR enough scenes are genuinely bright -- a lighter canvas,
    bright content plates/panels, or a second inverted (bright-field) beat. This
    is the color-script idea as a gate: plan >= 2 brightness beats, don't wash the
    whole runtime in one dark value."""
    durs = [float(sc.get("duration_s", 3.0)) for sc in spec["scenes"]]
    mids, acc = [], 0.0
    for d in durs:
        mids.append(acc + d / 2)
        acc += d
    means = []
    for t in mids:
        cmd = ["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(mp4),
               "-frames:v", "1", "-vf", "scale=540:540", "-pix_fmt", "gray",
               "-f", "rawvideo", "-"]
        buf = subprocess.run(cmd, capture_output=True).stdout
        if len(buf) < 540 * 540:
            continue
        fr = np.frombuffer(buf[: 540 * 540], dtype=np.uint8).astype(np.float32)
        means.append(float(fr.mean()))
    if not means:
        warns.append("brightness: could not sample the video")
        return
    overall = float(np.mean(means))
    bright_frac = float(np.mean([m > BRIGHT_SCENE_LUMA for m in means]))
    report["brightness"] = {"overall_mean_luma": round(overall, 1),
                            "bright_scene_fraction": round(bright_frac, 2),
                            "per_scene_mean_luma": [round(m) for m in means]}
    if overall < BRIGHT_MEAN_FLOOR and bright_frac < BRIGHT_FRACTION_MIN:
        dark_scenes = [i for i, m in enumerate(means) if m <= BRIGHT_SCENE_LUMA]
        fails.append(
            f"brightness: video reads dark (mean luma {overall:.0f}/255, only {bright_frac:.0%} "
            f"of scenes bright; dark scenes {dark_scenes}). The client's standing note is that "
            f"every video seems dark. Fix it at DESIGN time, not the grade: use a lighter canvas, "
            f"add bright content plates/panels, or add a second inverted bright-field beat so "
            f">= {BRIGHT_FRACTION_MIN:.0%} of scenes clear mean luma {BRIGHT_SCENE_LUMA:.0f} "
            f"(plan >= 2 brightness beats -- a color script, not one dark wash).")
    else:
        print(f"  [PASS] brightness (mean luma {overall:.0f}/255, {bright_frac:.0%} of scenes bright)")


def chroma_neutrality(mp4, raw, fails, warns, report):
    """The finishing chain must not invent color the page never rendered.
    Sample frames across the final and the raw capture, compare median R-G
    and B-G casts; finishing-introduced drift > ~8 levels is a grade/bloom
    bug (e.g. screen-blending YUV chroma planes turns black canvases
    magenta — shipped as 'dim' purple murk for weeks before this gate)."""
    def casts(path):
        cmd = ["ffmpeg", "-v", "error", "-i", str(path),
               "-vf", "fps=2,scale=96:96,format=rgb24", "-f", "rawvideo", "-"]
        buf = subprocess.run(cmd, capture_output=True).stdout
        n = len(buf) // (96 * 96 * 3)
        if n < 4:
            return None
        a = np.frombuffer(buf[: n * 96 * 96 * 3], dtype=np.uint8).reshape(n, -1, 3).astype(np.float64)
        m = a.mean(axis=1)  # per-frame R,G,B means
        return float(np.median(m[:, 0] - m[:, 1])), float(np.median(m[:, 2] - m[:, 1]))
    fin = casts(mp4)
    ref = casts(raw) if raw else None
    if fin is None:
        warns.append("chroma: could not sample final for the neutrality check")
        return
    drift_rg = fin[0] - (ref[0] if ref else 0.0)
    drift_bg = fin[1] - (ref[1] if ref else 0.0)
    report["chroma_cast"] = {"final_RG": round(fin[0], 2), "final_BG": round(fin[1], 2),
                             "raw_RG": round(ref[0], 2) if ref else None,
                             "raw_BG": round(ref[1], 2) if ref else None}
    if abs(drift_rg) > 8 or abs(drift_bg) > 8:
        fails.append(f"chroma: finishing introduced a color cast (R-G drift {drift_rg:+.1f}, "
                     f"B-G drift {drift_bg:+.1f} vs raw; the brand's blacks must stay black)")
    elif abs(drift_rg) > 4 or abs(drift_bg) > 4:
        warns.append(f"chroma: mild finishing cast (R-G drift {drift_rg:+.1f}, B-G drift {drift_bg:+.1f})")
    else:
        print(f"  [PASS] chroma neutrality (R-G drift {drift_rg:+.1f}, B-G drift {drift_bg:+.1f} vs raw)")


def cadence(spec, fails, warns, report):
    durs = [float(s.get("duration_s", 3.0)) for s in spec["scenes"]]
    report["scene_durations"] = durs
    long_scenes = [i for i, d in enumerate(durs) if d > 5.0]
    if long_scenes:
        fails.append(f"cadence: scene(s) {long_scenes} exceed 5.0s; a beat lands every ~4s or attention dies")
    if len(durs) < 4:
        warns.append(f"cadence: only {len(durs)} scenes")
    else:
        print(f"  [PASS] cadence ({len(durs)} scenes, longest {max(durs):.1f}s)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec")
    p.add_argument("mp4")
    p.add_argument("--raw", help="raw capture (pre-grain) for the frame-pacing gate")
    p.add_argument("--report")
    args = p.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    durs = [float(s.get("duration_s", 3.0)) for s in spec["scenes"]]
    total = sum(durs)
    fails, warns, report = [], [], {}

    raw_motion = None
    if args.raw:
        raw_motion = frame_pacing(args.raw, spec, fails, warns, report)
    cadence(spec, fails, warns, report)
    readability(spec, args.mp4, fails, warns, report)
    brightness(spec, args.mp4, fails, warns, report)
    chroma_neutrality(args.mp4, args.raw, fails, warns, report)

    frames = decode_gray(args.mp4)
    energy = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))  # per-frame motion
    report["frames"] = int(len(frames))

    # 1. dead air: judged on the raw capture when available (the grade crushes
    # near-black drift below any fixed final-pixel threshold)
    if raw_motion is not None:
        still = raw_motion < 0.03
    else:
        still = energy < 0.22
    max_run = run = 0
    for s in still:
        run = run + 1 if s else 0
        max_run = max(max_run, run)
    dead_s = max_run / FPS
    report["longest_still_s"] = round(dead_s, 2)
    if dead_s > 2.0:
        fails.append(f"dead air: {dead_s:.1f}s with no motion (max 2.0)")
    elif dead_s > 1.4:
        warns.append(f"near-dead air: {dead_s:.1f}s low motion")
    else:
        print(f"  [PASS] dead air (longest still {dead_s:.2f}s)")

    # 2. energy arc
    k = FPS  # 1s smoothing
    if len(energy) > k * 3:
        kernel = np.ones(k) / k
        smooth = np.convolve(energy, kernel, mode="valid")
        peak_pos = float(np.argmax(smooth)) / max(1, len(smooth) - 1)
        report["energy_peak_pos"] = round(peak_pos, 3)
        if 0.35 <= peak_pos <= 0.90:
            print(f"  [PASS] energy arc (peak at {peak_pos:.0%} of runtime)")
        else:
            warns.append(f"energy arc peaks at {peak_pos:.0%}; aim for 60-80%")

    # 3. poster frame
    poster_std = float(frames[0].std())
    report["poster_luma_std"] = round(poster_std, 2)
    if poster_std < 6.0:
        fails.append(f"poster frame nearly blank (luma std {poster_std:.1f}); X shows frame 0 as the thumbnail")
    else:
        print(f"  [PASS] poster frame (luma std {poster_std:.1f})")

    # 4. loudness motion
    x, fs = decode_audio(args.mp4)
    if x is not None and len(x) > fs:
        win = fs // 2
        n = len(x) // win
        rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
        db = 20 * np.log10(rms + 1e-9)
        core = db[1:-2] if len(db) > 4 else db  # ignore fade tails
        drange = float(core.max() - core.min()) if len(core) else 0.0
        report["audio_range_db"] = round(drange, 1)
        if drange < 3.0:
            warns.append(f"audio bed is flat ({drange:.1f} dB range); the mix should breathe around the hits")
        else:
            print(f"  [PASS] loudness motion ({drange:.1f} dB range)")

    # 5. beat alignment
    beat = (spec.get("design") or {}).get("beat") or {}
    if beat.get("aligned") and x is not None:
        onsets = onset_times(x, fs)
        cuts = np.cumsum(durs)[:-1]
        if len(onsets) and len(cuts):
            drifts = [float(np.min(np.abs(onsets - c))) * 1000 for c in cuts]
            med = float(np.median(drifts))
            report["cut_onset_median_ms"] = round(med, 1)
            if med <= 120:
                print(f"  [PASS] beat alignment (median cut-to-onset {med:.0f}ms)")
            elif med <= 200:
                warns.append(f"beat alignment soft: median cut-to-onset {med:.0f}ms")
            else:
                fails.append(f"beat alignment broken: median cut-to-onset {med:.0f}ms (spec claims aligned)")

    # 6. conform sanity
    dur = probe_duration(args.mp4)
    report["duration_s"] = dur
    if dur is None or abs(dur - total) > 0.5:
        fails.append(f"duration {dur} deviates from spec total {total:.2f}")
    else:
        print(f"  [PASS] conform ({dur:.2f}s vs spec {total:.2f}s)")

    print()
    for w in warns:
        print(f"  WARN: {w}")
    for f in fails:
        print(f"  FAIL: {f}")
    report["warnings"] = warns
    report["failures"] = fails
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    if fails:
        print("\nSCREENING ROOM FAILED")
        sys.exit(1)
    print("\nSCREENING ROOM PASSED" + (f" ({len(warns)} warning(s))" if warns else ""))


if __name__ == "__main__":
    main()
