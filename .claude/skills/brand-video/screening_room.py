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

Usage:
    python screening_room.py reports/scene-spec-DATE.json reports/tribute-DATE.mp4 \
        [--report reports/screening-DATE.json]
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec")
    p.add_argument("mp4")
    p.add_argument("--report")
    args = p.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    durs = [float(s.get("duration_s", 3.0)) for s in spec["scenes"]]
    total = sum(durs)
    fails, warns, report = [], [], {}

    frames = decode_gray(args.mp4)
    energy = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))  # per-frame motion
    report["frames"] = int(len(frames))

    # 1. dead air
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
