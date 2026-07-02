#!/usr/bin/env python3
"""
Finishing pass for the daily-tribute pipeline: one deterministic conform step
that replaces the routine's inline ffmpeg mux.

Video (research-backed chain, in order):
  fps normalize -> lanczos downscale (if supersampled) -> filmic S-curve grade
  -> gated bloom -> whisper chromatic aberration -> vignette -> type sharpen
  -> deband -> temporal grain (dither) -> x264 crf 17 aq-mode=3

Audio:
  music bed (offset + fades) + rich foley stem, music sidechain-ducked under
  the foley hits, then two-pass loudnorm to -14 LUFS / -1.5 dBTP (X social
  target; linear=true so the duck dynamics survive).

Usage:
    python finish.py --raw /tmp/raw.mp4 --spec reports/scene-spec-DATE.json \
        --music .claude/skills/brand-video/music/Track.mp3 --music-offset 30 \
        --foley /tmp/foley-DATE.wav --out reports/tribute-DATE.mp4 [--trim 1.5]
        [--grade filmic|none] [--no-bloom]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run(cmd, **kw):
    res = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if res.returncode != 0:
        sys.stderr.write(res.stderr[-4000:])
        raise SystemExit(f"command failed: {' '.join(cmd[:6])}...")
    return res


def detect_content_start(raw, hint, window=1.2):
    """The sidecar t0 marks when the page SCHEDULED the animation; the first
    composited content frame lands ~100-200ms later (rAF + encode latency).
    Scan a small window after the hint for the first real frame-to-frame
    change so video t=0 is the true visual t=0 (poster + beat alignment)."""
    import numpy as np
    start = max(0.0, hint - 0.1)
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(window + 0.1),
           "-i", str(raw), "-vf", "fps=25,scale=160:160", "-pix_fmt", "gray",
           "-f", "rawvideo", "-"]
    buf = subprocess.run(cmd, capture_output=True).stdout
    n = len(buf) // (160 * 160)
    if n < 4:
        return hint
    fr = __import__("numpy").frombuffer(buf, dtype="uint8")[: n * 160 * 160].reshape(n, 160, 160).astype("float32")
    d = abs(fr[1:] - fr[:-1]).mean(axis=(1, 2))
    for i, x in enumerate(d):
        if x > 0.5:
            return round(start + (i + 1) / 25.0, 3)
    return hint


def spec_duration(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    return sum(float(s.get("duration_s", 3.0)) for s in spec["scenes"])


def build_video_chain(grade, bloom):
    pre = "fps=25,scale=1080:1080:flags=lanczos,format=yuv444p"
    steps = [pre]
    if grade == "filmic":
        # brightness-preserving filmic: gentle shadow LIFT + highlight glide.
        # The old curve crushed 0.25->0.22 and dimmed every dark-canvas video.
        steps.append("curves=master='0/0 0.25/0.27 0.5/0.54 0.75/0.80 1/1'")
        steps.append("eq=saturation=1.07:contrast=1.02:gamma=1.03")
    chain_a = ",".join(steps)
    post = [
        # blend-interpolate 25 -> 50fps: intermediate frames are crossfades,
        # which reads as natural motion blur on kinetic type (no warping)
        "minterpolate=fps=50:mi_mode=blend",
        "rgbashift=rh=1:bh=-1:edge=smear",
        "unsharp=5:5:0.45:5:5:0.0",
        "deband=1thr=0.012:2thr=0.012:3thr=0.012:range=16:blur=1",
        "noise=c0s=5:c0f=t+u",
        "format=yuv420p",
    ]
    chain_b = ",".join(post)
    if bloom:
        # bloom MUST blend in planar RGB: `blend` works per-plane, and a
        # screen blend on YUV chroma planes (centered at 128) pushes U/V
        # toward 192 — a hard magenta cast over every dark canvas. gbrp in,
        # screen per RGB plane (correct), then back to yuv444p for the rest.
        return (
            f"[0:v]{chain_a},format=gbrp,split=2[base][gl];"
            f"[gl]colorlevels=rimin=0.55:gimin=0.55:bimin=0.55,gblur=sigma=26:steps=3[glow];"
            f"[base][glow]blend=all_mode=screen:all_opacity=0.30,format=yuv444p,{chain_b}[vout]"
        )
    return f"[0:v]{chain_a},{chain_b}[vout]"


def build_audio_chain(duration, music_offset, fade_out_start, loudnorm_args):
    return (
        f"[1:a]atrim=start={music_offset}:end={music_offset + duration + 0.5},"
        f"asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={fade_out_start}:d=1.5[m];"
        f"[2:a]asplit=2[k][f];"
        f"[m][k]sidechaincompress=threshold=0.06:ratio=5:attack=6:release=260[duck];"
        f"[duck][f]amix=inputs=2:weights='1 0.85':normalize=0,"
        f"loudnorm={loudnorm_args}[aout]"
    )


def measure_loudness(raw, spec_dur, args):
    """Pass 1: measure integrated loudness of the mixed audio graph."""
    fade_out_start = spec_dur - 1.5
    audio = build_audio_chain(spec_dur, args.music_offset, fade_out_start,
                              "I=-14:TP=-1.5:LRA=11:print_format=json")
    cmd = [
        "ffmpeg", "-y", "-ss", str(args.trim), "-i", str(raw),
        "-i", str(args.music), "-i", str(args.foley),
        "-filter_complex", audio, "-map", "[aout]",
        "-t", f"{spec_dur}", "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", res.stderr, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True)
    p.add_argument("--spec", required=True)
    p.add_argument("--music", required=True)
    p.add_argument("--music-offset", type=float, default=30.0)
    p.add_argument("--foley", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--trim", default="auto",
                   help="Seconds of warmup to drop from the raw capture head. 'auto' (default) "
                        "reads <raw>.meta.json written by the CDP recorder for the EXACT "
                        "animation start; falls back to 1.5 when no sidecar exists.")
    p.add_argument("--grade", choices=["filmic", "none"], default="filmic")
    p.add_argument("--no-bloom", action="store_true")
    args = p.parse_args()

    if args.trim == "auto":
        sidecar = Path(str(args.raw) + ".meta.json")
        if sidecar.exists():
            hint = float(json.loads(sidecar.read_text())["trim_s"])
            args.trim = detect_content_start(args.raw, hint)
            print(f"trim: {args.trim:.3f}s (first content frame; sidecar hint {hint:.3f}s)")
        else:
            args.trim = 1.5
            print("trim: 1.5s (no sidecar; legacy fallback)", file=sys.stderr)
    else:
        args.trim = float(args.trim)

    dur = spec_duration(args.spec)
    fade_out_start = dur - 1.5

    measured = measure_loudness(args.raw, dur, args)
    if measured:
        ln = (
            f"I=-14:TP=-1.5:LRA=11:linear=true"
            f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
            f":measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}"
            f":offset={measured['target_offset']}"
        )
        print(f"loudnorm pass 1: I={measured['input_i']} TP={measured['input_tp']} LRA={measured['input_lra']}")
    else:
        ln = "I=-14:TP=-1.5:LRA=11"
        print("loudnorm pass 1 failed to parse; falling back to single-pass", file=sys.stderr)

    video = build_video_chain(args.grade, not args.no_bloom)
    audio = build_audio_chain(dur, args.music_offset, fade_out_start, ln)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(args.trim), "-i", str(args.raw),
        "-i", str(args.music),
        "-i", str(args.foley),
        "-filter_complex", f"{video};{audio}",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
        "-preset", "slow", "-crf", "20",
        "-maxrate", "10M", "-bufsize", "16M",
        "-x264-params", "aq-mode=3",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
        "-t", f"{dur}",
        str(args.out),
    ]
    run(cmd)
    size_mb = Path(args.out).stat().st_size / 1e6
    print(f"finished {args.out} ({dur:.1f}s, {size_mb:.1f} MB, grade={args.grade}, bloom={not args.no_bloom})")


if __name__ == "__main__":
    main()
