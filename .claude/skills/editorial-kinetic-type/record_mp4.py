#!/usr/bin/env python3
"""
editorial-kinetic-type mp4 recorder.

Uses Playwright headless Chromium to play the HTML video in a 1080x1080
viewport for 26 seconds, captures it as webm, then muxes the silent webm
with the wav from synth_audio.py to produce an H.264 + AAC mp4.

The Web Audio API soundtrack inside the HTML is silent in headless capture
(Playwright does not record tab audio), which is why we synthesize the
audio separately and mux it in.

Usage:
    python record_mp4.py <html_path> <output.mp4>

Requires:
    - playwright (pip install playwright && playwright install chromium)
    - ffmpeg in PATH
    - numpy, scipy (for synth_audio.py)
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


VIEWPORT = 1080
DURATION_S = 25.0
RECORD_S = 26.0  # add 1s tail to capture the fade out


def ensure_playwright():
    try:
        import playwright  # noqa
    except ImportError:
        print("Installing playwright...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    # ensure chromium is installed
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit("playwright install chromium failed")


def record_webm(html_path: Path, out_dir: Path) -> Path:
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        context = browser.new_context(
            viewport={"width": VIEWPORT, "height": VIEWPORT},
            record_video_dir=str(out_dir),
            record_video_size={"width": VIEWPORT, "height": VIEWPORT},
        )
        page = context.new_page()
        page.goto(f"file://{html_path.resolve()}")
        # the page calls play() automatically on load; wait through the run
        page.wait_for_timeout(int(RECORD_S * 1000))
        context.close()
        browser.close()

    webms = sorted(out_dir.glob("*.webm"))
    if not webms:
        raise SystemExit("Playwright did not produce a webm file")
    return webms[-1]


def synth_wav(out_path: Path):
    script = Path(__file__).parent / "synth_audio.py"
    subprocess.check_call([sys.executable, str(script), str(out_path)])


def mux(webm_path: Path, wav_path: Path, mp4_path: Path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(webm_path),
        "-i", str(wav_path),
        "-t", f"{DURATION_S}",
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
        "-shortest",
        str(mp4_path),
    ]
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html", help="Path to the HTML video")
    parser.add_argument("output", help="Path to write the MP4")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found in PATH")

    ensure_playwright()

    html_path = Path(args.html).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        print(f"Recording {html_path.name} -> webm")
        webm = record_webm(html_path, tmp_dir / "video")
        print(f"Synthesizing soundtrack")
        wav = tmp_dir / "soundtrack.wav"
        synth_wav(wav)
        print(f"Muxing to {out_path}")
        mux(webm, wav, out_path)

    print(f"Done. {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
