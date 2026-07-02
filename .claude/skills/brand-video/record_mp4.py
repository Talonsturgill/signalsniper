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
import base64
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


PERF_PROBE = """
window.__ft = [];
(function(){ let last = 0;
  function s(t){ if (last) window.__ft.push(t - last); last = t; requestAnimationFrame(s); }
  requestAnimationFrame(s); })();
"""


def rehearse_perf(page, seconds=3.0, slow_ms=50.0, max_slow_frac=0.08, median_budget_ms=36.0):
    """Sample rAF frame times while the animation plays. A page that cannot
    paint fast enough produces a duplicated-frame slideshow in the screencast;
    refuse to record it.

    Gate on the FRACTION of slow frames plus the median, not a raw p95: one
    isolated GC pause in a short window costs a single invisible duplicate
    frame, while systemic slowness (the thing this gate exists for) shows up
    as a high slow-fraction or a high median."""
    page.wait_for_timeout(int(seconds * 1000))
    ft = page.evaluate("window.__ft.slice(30)") or []  # drop post-load warmup samples
    if len(ft) < 30:
        raise SystemExit("perf rehearsal: page produced almost no frames; renderer is stalled")
    srt = sorted(ft)
    p50 = srt[len(srt) // 2]
    slow_frac = sum(1 for x in ft if x > slow_ms) / len(ft)
    print(f"perf rehearsal: rAF p50={p50:.0f}ms slow-frames({slow_ms:.0f}ms+)={slow_frac:.1%} "
          f"(budget: median<={median_budget_ms:.0f}ms, slow<{max_slow_frac:.0%})", file=sys.stderr)
    if p50 > median_budget_ms or slow_frac > max_slow_frac:
        raise SystemExit(
            f"perf rehearsal FAILED: median {p50:.0f}ms / slow-frame share {slow_frac:.0%}. "
            "The capture would be a duplicated-frame slideshow. Reduce full-stage filters/"
            "blends or viewport before recording.")
    return p50, slow_frac


def record_cdp(html_path: Path, out_dir: Path, record_s: float, viewport: int = VIEWPORT,
               perf_gate: bool = True):
    """Capture via CDP Page.startScreencast (JPEG frames + epoch timestamps).

    Playwright's built-in recorder encodes VP8 in-process and its backpressure
    throttles the compositor to a slideshow (~9fps at 1080). Raw JPEG screencast
    frames with immediate acks keep pace with a 60fps page, and the frame
    timestamps + the page's __bvT0abs marker give an EXACT animation-start trim.
    Returns (frames_dir, timestamps, t0_epoch_s).
    """
    from playwright.sync_api import sync_playwright

    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    stamps = []

    with sync_playwright() as p:
        browser = launch_browser(p, ["--autoplay-policy=no-user-gesture-required"])
        page = browser.new_page(viewport={"width": viewport, "height": viewport})
        if perf_gate:
            page.add_init_script(PERF_PROBE)
        page.goto(f"file://{html_path.resolve()}")
        page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
        if perf_gate:
            rehearse_perf(page)

        client = page.context.new_cdp_session(page)
        counter = {"n": 0}

        def on_frame(params):
            i = counter["n"]
            counter["n"] += 1
            (frames_dir / f"f{i:05d}.jpg").write_bytes(base64.b64decode(params["data"]))
            stamps.append(float(params["metadata"]["timestamp"]))
            try:
                client.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
            except Exception:
                pass

        client.on("Page.screencastFrame", on_frame)
        client.send("Page.startScreencast", {
            "format": "jpeg", "quality": 85,
            "maxWidth": viewport, "maxHeight": viewport, "everyNthFrame": 1,
        })
        # The rehearsal already played the opening seconds on this page. Reload
        # with the screencast rolling so the capture contains the animation's
        # true t=0; the sidecar trim cuts the reload warmup exactly.
        page.reload(wait_until="load")
        page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
        page.wait_for_timeout(int(record_s * 1000))
        try:
            client.send("Page.stopScreencast")
        except Exception:
            pass
        t0_abs = page.evaluate("window.__bvT0abs || 0") / 1000.0
        browser.close()

    if counter["n"] < record_s * 10:
        raise SystemExit(f"CDP screencast produced only {counter['n']} frames for {record_s:.0f}s; capture failed")
    return frames_dir, stamps, t0_abs


def assemble_cdp(frames_dir: Path, stamps, mp4_path: Path):
    """Assemble timestamped JPEG frames into a VFR-faithful H.264 file."""
    lines = []
    n = len(stamps)
    for i in range(n):
        dur = (stamps[i + 1] - stamps[i]) if i + 1 < n else 1 / 25
        dur = min(max(dur, 1 / 120), 1.0)
        lines.append(f"file 'frames/f{i:05d}.jpg'")
        lines.append(f"duration {dur:.6f}")
    lines.append(f"file 'frames/f{n-1:05d}.jpg'")
    concat = frames_dir.parent / "concat.txt"
    concat.write_text("\n".join(lines) + "\n")
    subprocess.check_call([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-fps_mode", "vfr", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
        "-pix_fmt", "yuv420p", str(mp4_path),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def record_webm(html_path: Path, out_dir: Path, record_s: float, viewport: int = VIEWPORT,
                perf_gate: bool = True) -> Path:
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = launch_browser(p, ["--autoplay-policy=no-user-gesture-required"])

        if perf_gate:
            # Rehearse on a throwaway page first so the stall never reaches tape.
            probe_page = browser.new_page(viewport={"width": viewport, "height": viewport})
            probe_page.add_init_script(PERF_PROBE)
            probe_page.goto(f"file://{html_path.resolve()}")
            probe_page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
            rehearse_perf(probe_page)
            probe_page.close()

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
                        help="Capture size in px (default 1080). Only supersample when the "
                             "perf rehearsal proves the page holds 60fps at that size.")
    parser.add_argument("--no-perf-gate", action="store_true",
                        help="Skip the pre-record frame-time rehearsal (not recommended)")
    parser.add_argument("--engine", choices=["cdp", "playwright"], default="cdp",
                        help="cdp (default): JPEG screencast, keeps pace with the page and "
                             "records the exact animation-start trim. playwright: legacy "
                             "recorder (VP8 backpressure throttles the page; avoid).")
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
        if args.engine == "cdp":
            frames_dir, stamps, t0_abs = record_cdp(
                html_path, tmp_dir, record_s, viewport=args.viewport,
                perf_gate=not args.no_perf_gate)
            assemble_cdp(frames_dir, stamps, out_path)
            trim = max(0.0, t0_abs - stamps[0]) if t0_abs else 1.5
            fps_seen = (len(stamps) - 1) / max(0.001, stamps[-1] - stamps[0])
            sidecar = {
                "engine": "cdp", "trim_s": round(trim, 3), "frames": len(stamps),
                "capture_fps": round(fps_seen, 1), "t0_abs": t0_abs,
            }
            Path(str(out_path) + ".meta.json").write_text(json.dumps(sidecar, indent=2) + "\n")
            size_kb = out_path.stat().st_size / 1024
            print(f"Done. {out_path} ({size_kb:.0f} KB, {len(stamps)} frames @ ~{fps_seen:.0f}fps, trim_s={trim:.3f})")
        else:
            webm = record_webm(html_path, tmp_dir / "video", record_s, viewport=args.viewport,
                               perf_gate=not args.no_perf_gate)
            wav = tmp_dir / "soundtrack.wav"
            synth_wav(wav, meta)
            mux(webm, wav, out_path, total_s)
            size_kb = out_path.stat().st_size / 1024
            print(f"Done. {out_path} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
