#!/usr/bin/env python3
"""
brand-video MP4 recorder.

Reads the bv-timeline meta tag from the HTML to learn total duration and
emphasis points, screen-records the page in headless 1080x1080 Chromium,
synthesizes the soundtrack via synth_audio.py, then muxes via ffmpeg.

Usage:
    python record_mp4.py <html_path> <output.mp4>

Requires playwright (pip install playwright && playwright install chromium),
ffmpeg in PATH, numpy, scipy.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


VIEWPORT = 1080
TAIL_S = 3.0  # extra seconds captured so trim can drop the warmup AND the final fade still records cleanly

# Pre-installed Chromium fallbacks for environments where the Playwright CDN
# download is blocked (e.g. sandboxed CI). Checked in order after the default.
CHROMIUM_FALLBACKS = [
    os.environ.get("BV_CHROMIUM", ""),
    "/opt/pw-browsers/chromium",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
    shutil.which("google-chrome") or "",
]


def ensure_playwright():
    try:
        import playwright  # noqa
    except ImportError:
        print("Installing playwright...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])


def launch_browser(p, args):
    """Launch Chromium: managed browser first, pre-installed fallbacks second."""
    try:
        return p.chromium.launch(args=args)
    except Exception as first_err:
        for candidate in CHROMIUM_FALLBACKS:
            if candidate and Path(candidate).exists():
                print(f"default chromium unavailable, using {candidate}", file=sys.stderr)
                return p.chromium.launch(executable_path=candidate, args=args)
        raise first_err


def read_bv_meta(html_path: Path):
    text = html_path.read_text()
    m = re.search(r"<meta\s+name=['\"]bv-timeline['\"]\s+content=['\"](.*?)['\"]\s*/?>", text, re.DOTALL)
    if not m:
        raise SystemExit("HTML missing <meta name='bv-timeline' content='...'/>")
    raw = m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return json.loads(raw)


def record_webm(html_path: Path, out_dir: Path, record_s: float, viewport: int = VIEWPORT) -> Path:
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = launch_browser(p, ["--autoplay-policy=no-user-gesture-required"])
        context = browser.new_context(
            viewport={"width": viewport, "height": viewport},
            record_video_dir=str(out_dir),
            record_video_size={"width": viewport, "height": viewport},
        )
        page = context.new_page()
        page.goto(f"file://{html_path.resolve()}")
        # Explicit font gate: fonts.ready alone misses faces not yet used in layout.
        page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
        page.wait_for_timeout(int(record_s * 1000))
        context.close()
        browser.close()

    webms = sorted(out_dir.glob("*.webm"))
    if not webms:
        raise SystemExit("Playwright did not produce a webm")
    return webms[-1]


def synth_wav(wav_path: Path, meta: dict):
    script = Path(__file__).parent / "synth_audio.py"
    subprocess.check_call([
        sys.executable, str(script),
        "--bv-meta", json.dumps(meta),
        "--output", str(wav_path),
    ])


def mux(webm_path: Path, wav_path: Path, mp4_path: Path, total_s: float):
    # Output an extra 2s up front so the next mux can -ss 1.5 the warmup and
    # still hand back total_s of real content.
    cmd = [
        "ffmpeg", "-y",
        "-i", str(webm_path),
        "-i", str(wav_path),
        "-t", f"{total_s + 2.0}",
        "-c:v", "libx264",
        "-profile:v", "baseline",
        "-level", "3.1",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-movflags", "+faststart",
        str(mp4_path),
    ]
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html", help="Path to brand-video HTML")
    parser.add_argument("output", help="Path to write MP4")
    parser.add_argument("--viewport", type=int, default=VIEWPORT,
                        help="Capture size in px (default 1080). 1620 supersamples 1.5x; "
                             "finish.py downscales to 1080 with lanczos for crisper type.")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found in PATH")

    html_path = Path(args.html).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    meta = read_bv_meta(html_path)
    total_s = float(meta["total_s"])
    record_s = total_s + TAIL_S
    print(f"Recording {total_s}s + {TAIL_S}s tail = {record_s}s at {args.viewport}px")

    ensure_playwright()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        webm = record_webm(html_path, tmp_dir / "video", record_s, viewport=args.viewport)
        wav = tmp_dir / "soundtrack.wav"
        synth_wav(wav, meta)
        mux(webm, wav, out_path, total_s)

    size_kb = out_path.stat().st_size / 1024
    print(f"Done. {out_path} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
