#!/usr/bin/env python3
"""
Animatic editor for the daily-tribute pipeline: snap scene cuts to music beats.

Studio practice cuts picture to the track, not the reverse. This tool:
  1. decodes the chosen music bed (from its play offset) via an ffmpeg pipe
  2. finds onsets with spectral flux (SuperFlux-style max-filter, numpy/scipy only)
  3. estimates BPM from the novelty autocorrelation
  4. snaps each interior scene boundary to the nearest onset within a window,
     respecting per-scene duration bounds, then leads each cut by one frame
     (40ms) so the visual impact lands ON the transient
  5. writes the retimed durations back into the spec and records
     design.beat = {bpm, offset_s, aligned, median_drift_ms}

Usage:
    python beat_align.py --music music/Track.mp3 --offset 30 \
        --spec reports/scene-spec-DATE.json --write
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import stft, find_peaks
from scipy.ndimage import uniform_filter1d, maximum_filter1d

FS = 22050
HOP = 512
NPERSEG = 2048
LEAD_S = 0.04  # cut leads the transient by one frame at 25fps


def decode_audio(path, offset, duration):
    cmd = [
        "ffmpeg", "-v", "error", "-ss", str(offset), "-t", str(duration),
        "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(FS), "-",
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr.decode()[-2000:])
        raise SystemExit("ffmpeg decode failed")
    return np.frombuffer(res.stdout, dtype=np.float32)


def onset_novelty(x):
    _, _, Z = stft(x, FS, nperseg=NPERSEG, noverlap=NPERSEG - HOP)
    S = np.log1p(10 * np.abs(Z))
    S = maximum_filter1d(S, 3, axis=0)  # SuperFlux vibrato robustness
    flux = np.maximum(np.diff(S, axis=1), 0).sum(axis=0)
    novelty = flux - uniform_filter1d(flux, 21)
    return novelty


def detect_onsets(novelty):
    height = float(np.std(novelty)) * 1.2
    distance = max(1, int(0.12 * FS / HOP))
    peaks, _ = find_peaks(novelty, height=height, distance=distance)
    return peaks * HOP / FS


def estimate_bpm(novelty):
    n = novelty - novelty.mean()
    ac = np.correlate(n, n, mode="full")[len(n) - 1:]
    frame_dur = HOP / FS
    best_bpm, best_score = None, -np.inf
    for lag in range(int(60 / 180 / frame_dur), int(60 / 60 / frame_dur) + 1):
        if lag >= len(ac):
            break
        bpm = 60.0 / (lag * frame_dur)
        prior = np.exp(-0.5 * ((np.log2(bpm / 120.0)) / 0.6) ** 2)  # log-normal at 120
        score = ac[lag] * prior
        if score > best_score:
            best_score, best_bpm = score, bpm
    return round(best_bpm, 1) if best_bpm else None


def snap(spec, onsets, max_shift, lo, hi):
    scenes = spec["scenes"]
    durs = [float(s.get("duration_s", 3.0)) for s in scenes]
    boundaries = np.cumsum(durs)[:-1]  # interior cuts
    new_bounds = []
    prev = 0.0
    drifts = []
    for i, b in enumerate(boundaries):
        nominal = prev + durs[i]
        cand = None
        if len(onsets):
            deltas = np.abs(onsets - nominal)
            j = int(np.argmin(deltas))
            if deltas[j] <= max_shift:
                snapped = float(onsets[j]) - LEAD_S
                # respect this scene's bounds and leave the next scene feasible
                if lo <= snapped - prev <= hi:
                    cand = snapped
                    drifts.append(abs(snapped + LEAD_S - nominal) * 1000)
        if cand is None:
            cand = nominal
        new_bounds.append(cand)
        prev = cand
    # rebuild durations; final scene keeps its authored length
    new_durs = []
    prev = 0.0
    for b in new_bounds:
        new_durs.append(round(b - prev, 2))
        prev = b
    new_durs.append(round(durs[-1], 2))
    return new_durs, (float(np.median(drifts)) if drifts else 0.0), len(drifts)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--music", required=True)
    p.add_argument("--offset", type=float, default=30.0)
    p.add_argument("--spec", required=True)
    p.add_argument("--write", action="store_true", help="write retimed durations into the spec")
    p.add_argument("--max-shift", type=float, default=0.45)
    p.add_argument("--min", dest="lo", type=float, default=2.5)
    p.add_argument("--max", dest="hi", type=float, default=4.5)
    args = p.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    total = sum(float(s.get("duration_s", 3.0)) for s in spec["scenes"])

    x = decode_audio(args.music, args.offset, total + 4.0)
    novelty = onset_novelty(x)
    onsets = detect_onsets(novelty)
    bpm = estimate_bpm(novelty)

    new_durs, median_drift, snapped_n = snap(spec, onsets, args.max_shift, args.lo, args.hi)
    new_total = sum(new_durs)

    report = {
        "bpm": bpm,
        "onsets_found": int(len(onsets)),
        "cuts_snapped": snapped_n,
        "cuts_total": len(spec["scenes"]) - 1,
        "median_drift_ms": round(median_drift, 1),
        "durations": new_durs,
        "total_s": round(new_total, 2),
    }
    print(json.dumps(report, indent=2))

    if not (12.0 <= new_total <= 32.0):
        print(f"REFUSED: retimed total {new_total:.2f}s outside [12,32]; spec unchanged", file=sys.stderr)
        sys.exit(1)

    if args.write:
        for s, d in zip(spec["scenes"], new_durs):
            s["duration_s"] = d
        spec.setdefault("design", {})["beat"] = {
            "bpm": bpm,
            "offset_s": args.offset,
            "aligned": snapped_n > 0,
            "median_drift_ms": round(median_drift, 1),
        }
        Path(args.spec).write_text(json.dumps(spec, indent=2) + "\n")
        print(f"wrote retimed spec: {args.spec}", file=sys.stderr)


if __name__ == "__main__":
    main()
