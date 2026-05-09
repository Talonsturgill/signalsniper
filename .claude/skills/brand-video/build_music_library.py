#!/usr/bin/env python3
"""
brand-video music library generator.

Synthesizes a small catalog of looping tracks for the daily-tribute pipeline.
Each track is rendered to a stereo MP3 and recorded in catalog.json with
mood, instruments, BPM, and which preset packs it fits. All tracks are
original instrumentals authored by the signalsniper pipeline. No third-party
licensing, no attribution required.

Tracks shipped (all 60s, master-bus normalized):
  - nightline.mp3  · 88 BPM dub-techno · subway-chrome, mono-terminal, cctv
  - signal.mp3     · 112 BPM minimal techno · geominimal, editorial-90s
  - paper-room.mp3 · 70 BPM felt piano + room · editorial-paper, claude, gallery
  - dispatch.mp3   · 92 BPM cinematic piano + cellos · gallery, claude, DISPATCH

Usage:
    python build_music_library.py [--out-dir .claude/skills/brand-video/music]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy import signal as sig
from scipy.io import wavfile

SR = 44100


def sec(t: float) -> int:
    return int(t * SR)


def env_ar(n: int, attack_s: float, release_s: float) -> np.ndarray:
    env = np.ones(n)
    a, r = sec(attack_s), sec(release_s)
    if n > a:
        env[:a] = np.linspace(0, 1, a)
    if n > r:
        env[-r:] = np.linspace(1, 0, r)
    return env


def lp(x: np.ndarray, hz: float, order: int = 4) -> np.ndarray:
    b, a = sig.butter(order, hz, btype="low", fs=SR)
    return sig.lfilter(b, a, x)


def hp(x: np.ndarray, hz: float, order: int = 4) -> np.ndarray:
    b, a = sig.butter(order, hz, btype="high", fs=SR)
    return sig.lfilter(b, a, x)


def bp(x: np.ndarray, lo: float, hi: float, order: int = 4) -> np.ndarray:
    b, a = sig.butter(order, [lo, hi], btype="band", fs=SR)
    return sig.lfilter(b, a, x)


def add(track: np.ndarray, sample: np.ndarray, t: float, gain: float = 1.0) -> None:
    start = sec(t)
    if start < 0 or start >= len(track):
        return
    end = min(start + len(sample), len(track))
    track[start:end] += sample[: end - start] * gain


# ============ INSTRUMENTS ============
def kick_808(dur: float = 0.55, base: float = 50.0, pitch_env_amt: float = 80.0) -> np.ndarray:
    n = sec(dur)
    t = np.linspace(0, dur, n, False)
    freq = base + pitch_env_amt * np.exp(-t * 30)
    phase = np.cumsum(2 * np.pi * freq / SR)
    body = np.sin(phase) + 0.4 * np.sin(2 * phase)
    body = np.tanh(body * 1.3)
    click = np.random.RandomState(7).normal(0, 0.7, n) * np.exp(-t * 200) * 0.25
    env = np.exp(-t * 5)
    a = sec(0.002)
    if n > a:
        env[:a] *= np.linspace(0, 1, a)
    return (body + click) * env * 0.75


def hat_closed(seed: int, dur: float = 0.07) -> np.ndarray:
    n = sec(dur)
    rng = np.random.RandomState(seed)
    noise = rng.uniform(-1, 1, n)
    noise = bp(noise, 6500, 16000, order=6)
    t = np.linspace(0, dur, n, False)
    env = np.exp(-t * 90)
    return noise * env * 0.30


def hat_open(seed: int, dur: float = 0.22) -> np.ndarray:
    n = sec(dur)
    rng = np.random.RandomState(seed)
    noise = rng.uniform(-1, 1, n)
    noise = bp(noise, 5500, 14000, order=6)
    t = np.linspace(0, dur, n, False)
    env = np.exp(-t * 16)
    return noise * env * 0.22


def snap(seed: int, dur: float = 0.18) -> np.ndarray:
    """Finger-snap / clap layered on a band-passed transient."""
    n = sec(dur)
    rng = np.random.RandomState(seed)
    noise = rng.uniform(-1, 1, n)
    noise = bp(noise, 1500, 4500, order=6)
    t = np.linspace(0, dur, n, False)
    env = np.exp(-t * 24) + 0.4 * np.exp(-((t - 0.012) ** 2) / 0.00002)
    return noise * env * 0.5


def saw(freq: float, dur: float, n_harm: int = 8) -> np.ndarray:
    n = sec(dur)
    t = np.linspace(0, dur, n, False)
    w = np.zeros(n)
    for h in range(1, n_harm + 1):
        w += np.sin(2 * np.pi * freq * h * t) / h
    return w


def square(freq: float, dur: float, n_harm: int = 7) -> np.ndarray:
    n = sec(dur)
    t = np.linspace(0, dur, n, False)
    w = np.zeros(n)
    for h in range(1, 2 * n_harm, 2):
        w += np.sin(2 * np.pi * freq * h * t) / h
    return w


def sub_bass(freq: float, dur: float, gate_rate_hz: float | None = None) -> np.ndarray:
    n = sec(dur)
    t = np.linspace(0, dur, n, False)
    w = np.sin(2 * np.pi * freq * t) + 0.18 * np.sin(2 * np.pi * 2 * freq * t)
    if gate_rate_hz:
        # rhythmic gate: fast attack, slow release per beat
        period = 1.0 / gate_rate_hz
        phase = (t % period) / period
        gate = np.exp(-phase * 4.0)
        w = w * gate
    return np.tanh(w * 1.15)


def pad(freqs: list[float], dur: float, lfo_hz: float = 0.07) -> np.ndarray:
    n = sec(dur)
    t = np.linspace(0, dur, n, False)
    w = np.zeros(n)
    for i, f in enumerate(freqs):
        det = 1 + 0.0018 * np.sin(2 * np.pi * (lfo_hz * (i + 1) * 0.6) * t)
        ph = np.cumsum(2 * np.pi * f * det / SR)
        w += np.sin(ph) + 0.45 * np.sin(2 * ph) * np.exp(-t * 0.25)
    w /= max(1, len(freqs))
    w = lp(w, 3500, order=2)
    breath = 1 + 0.05 * np.sin(2 * np.pi * lfo_hz * t)
    return w * breath


def piano_note(freq: float, dur: float = 1.6, brightness: float = 1.0, vel: float = 1.0) -> np.ndarray:
    n = sec(dur)
    t = np.linspace(0, dur, n, False)
    w = np.sin(2 * np.pi * freq * t)
    w += 0.45 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 0.9)
    w += 0.18 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 1.7)
    w += 0.10 * np.sin(2 * np.pi * 4 * freq * t) * np.exp(-t * 2.4) * brightness
    w += 0.05 * np.sin(2 * np.pi * 5.4 * freq * t) * np.exp(-t * 5.0) * brightness
    w = lp(w, 5500, order=2)
    a = sec(0.004)
    env = np.exp(-t * 1.2)
    if n > a:
        env[:a] *= np.linspace(0, 1, a)
    return w * env * vel * 0.45


def cello_note(freq: float, dur: float = 3.0, vel: float = 1.0) -> np.ndarray:
    n = sec(dur)
    t = np.linspace(0, dur, n, False)
    # narrow saw with vibrato
    w = np.zeros(n)
    vib = 1 + 0.0035 * np.sin(2 * np.pi * 5.0 * t)
    ph = np.cumsum(2 * np.pi * freq * vib / SR)
    for h in range(1, 7):
        w += np.sin(h * ph) / h
    w = lp(w, 2400, order=4)
    swell = 0.35 + 0.65 * np.sin(2 * np.pi * 0.18 * t - 1.0) ** 2
    swell = np.clip(swell, 0, 1)
    a = sec(0.6)
    env = np.ones(n)
    if n > a:
        env[:a] = np.linspace(0, 1, a)
    r = sec(0.8)
    if n > r:
        env[-r:] *= np.linspace(1, 0, r)
    return w * env * swell * vel * 0.32


def vinyl_crackle(dur: float, density: float = 60.0) -> np.ndarray:
    n = sec(dur)
    rng = np.random.RandomState(11)
    pops = np.zeros(n)
    n_pops = int(dur * density)
    for _ in range(n_pops):
        pos = rng.randint(0, n - 256)
        amp = rng.uniform(0.05, 0.25)
        decay = rng.uniform(0.0008, 0.004)
        ll = 256
        tt = np.linspace(0, ll / SR, ll, False)
        pop = (rng.normal(0, 1, ll)) * np.exp(-tt / decay) * amp
        pops[pos : pos + ll] += pop
    pops = bp(pops, 1500, 5500, order=4)
    hiss = rng.normal(0, 0.012, n)
    hiss = bp(hiss, 800, 6500, order=4)
    return pops + hiss


def reverse_cymbal(dur: float = 1.4) -> np.ndarray:
    n = sec(dur)
    rng = np.random.RandomState(31)
    noise = rng.uniform(-1, 1, n)
    noise = bp(noise, 2000, 12000, order=4)
    env = np.linspace(0, 1, n) ** 2.4
    return noise * env * 0.18


# ============ TRACK BUILDERS ============
def _master_bus(stereo_mix: np.ndarray, headroom: float = 0.85) -> np.ndarray:
    """Light limiter + lp roll-off + peak normalize."""
    x = np.tanh(stereo_mix * 0.95) * 0.95
    # gentle high-shelf trim via mild LP at 14k
    x = np.stack([lp(x[:, 0], 14000, order=2), lp(x[:, 1], 14000, order=2)], axis=1)
    peak = np.max(np.abs(x))
    if peak > 0:
        x = x / peak * headroom
    return x


def _stereo_widen(mono: np.ndarray, delay_s: float = 0.009) -> np.ndarray:
    d = sec(delay_s)
    L = mono.copy()
    R = mono.copy()
    if len(R) > d:
        R[d:] = R[:-d]
    return np.stack([L, R], axis=1)


def _intro_fade(track: np.ndarray, fade_s: float = 1.5) -> np.ndarray:
    n = sec(fade_s)
    if len(track) > n:
        ramp = np.linspace(0, 1, n)
        if track.ndim == 2:
            ramp = ramp[:, None]
        track[:n] *= ramp
    return track


def _outro_fade(track: np.ndarray, fade_s: float = 2.5) -> np.ndarray:
    n = sec(fade_s)
    if len(track) > n:
        ramp = np.linspace(1, 0, n)
        if track.ndim == 2:
            ramp = ramp[:, None]
        track[-n:] *= ramp
    return track


def build_nightline(total_s: float = 60.0) -> np.ndarray:
    """88 BPM dub-techno. Subway-chrome / mono-terminal / cctv. Dark, icy, late-night."""
    bpm = 88.0
    beat = 60.0 / bpm  # 0.681s
    n = sec(total_s)
    bus = np.zeros(n)

    # Pad: Cm9 — C, Eb, G, Bb, D — minor, brooding
    pad_freqs = [130.81, 155.56, 196.00, 233.08, 293.66]  # C3 Eb3 G3 Bb3 D4
    bus += pad(pad_freqs, total_s, lfo_hz=0.06) * 0.42

    # Sub-bass on root, gated to 8th-notes
    sub = sub_bass(65.41, total_s, gate_rate_hz=2 * bpm / 60.0)  # 2.93 Hz = 8ths
    bus += sub * 0.55

    # Lead stab: short minor 7th saw chord pulse on the offbeat (the "dub stab")
    stab_dur = 0.35
    stab = saw(196.00, stab_dur, n_harm=10) + 0.6 * saw(233.08, stab_dur, n_harm=10) + 0.35 * saw(293.66, stab_dur, n_harm=10)
    stab = lp(stab, 2200, order=3)
    stab_env = np.exp(-np.linspace(0, stab_dur, sec(stab_dur), False) * 9)
    stab_env[: sec(0.005)] = np.linspace(0, 1, sec(0.005))
    stab = stab * stab_env * 0.20

    # Light arp: pentatonic, eighth notes, soft
    arp_notes = [261.63, 311.13, 392.00, 466.16, 392.00, 311.13]  # C Eb G Bb G Eb
    arp_step = beat / 2
    arp_dur = arp_step * 0.85
    for k, t in enumerate(np.arange(beat * 4, total_s - 1.0, arp_step)):
        f = arp_notes[k % len(arp_notes)]
        nt = sec(arp_dur)
        tt = np.linspace(0, arp_dur, nt, False)
        v = (saw(f * 2, arp_dur, n_harm=5)) * np.exp(-tt * 6) * 0.10
        v = lp(v, 4500, order=2)
        add(bus, v, t, gain=0.7)

    # Drums: kick on every beat (4/4), open hat on 8th offbeats, closed on 16ths after bar 4
    for beat_idx in range(int(total_s / beat) + 1):
        t = beat_idx * beat
        if t > total_s - 0.6:
            break
        if t > beat * 4:  # let intro breathe
            add(bus, kick_808(dur=0.5), t, gain=0.85)
        # snap on 2 and 4 (offbeat backbeat)
        if beat_idx % 2 == 1 and t > beat * 8:
            add(bus, snap(seed=20 + beat_idx, dur=0.18), t, gain=0.55)
        # open hat on the eighth offbeat
        oh_t = t + beat * 0.5
        if oh_t < total_s - 0.5 and beat_idx > 6:
            add(bus, hat_open(seed=40 + beat_idx, dur=0.20), oh_t, gain=0.50)
        # dub stab on offbeat starting bar 4
        if beat_idx % 4 == 1 and beat_idx > 4:
            add(bus, stab, t + beat * 0.5, gain=1.0)

    # 16th hats once the groove establishes
    sixt = beat / 4
    for s_idx in range(int(total_s / sixt)):
        t = s_idx * sixt
        if t < beat * 12 or t > total_s - 0.3:
            continue
        if s_idx % 4 == 0:
            continue  # leave the kick room
        add(bus, hat_closed(seed=60 + s_idx, dur=0.06), t, gain=0.45)

    # Reverse-cymbal swell at bar 8 (bring the energy)
    rev_t = beat * 16 - 1.4
    if rev_t > 0:
        add(bus, reverse_cymbal(1.4), rev_t, gain=0.7)

    bus = lp(bus, 12500, order=2)
    stereo = _stereo_widen(bus, delay_s=0.011)
    stereo = _intro_fade(stereo, 1.5)
    stereo = _outro_fade(stereo, 3.0)
    return _master_bus(stereo, headroom=0.78)


def build_signal(total_s: float = 60.0) -> np.ndarray:
    """112 BPM minimal techno. Geominimal / editorial-90s / electronic. Bright, driving, optimistic."""
    bpm = 112.0
    beat = 60.0 / bpm
    n = sec(total_s)
    bus = np.zeros(n)

    # Pad: F major add9 — F, A, C, E, G — bright, hopeful
    pad_freqs = [174.61, 220.00, 261.63, 329.63, 392.00]
    bus += pad(pad_freqs, total_s, lfo_hz=0.10) * 0.36

    # Bassline: F2 on 1, C3 on 3, with a passing E on the and-of-4
    f2, c3, a2, e3 = 87.31, 130.81, 110.00, 164.81
    bar = beat * 4
    n_bars = int(total_s / bar) + 1
    for b in range(n_bars):
        t0 = b * bar
        if t0 > total_s - 0.3:
            break
        # stomping dotted-8ths bass
        notes = [(t0 + 0 * beat, f2, 0.9), (t0 + 1.5 * beat, a2, 0.55),
                 (t0 + 2.0 * beat, c3, 0.9), (t0 + 3.5 * beat, e3, 0.65)]
        for t, f, vel in notes:
            if t >= total_s - 0.3:
                continue
            d = beat * 0.45
            w = sub_bass(f, d, gate_rate_hz=None)
            tt = np.linspace(0, d, sec(d), False)
            env = np.exp(-tt * 9)
            a = sec(0.005)
            env[:a] = np.linspace(0, 1, a)
            add(bus, w * env, t, gain=vel * 0.7)

    # Sparse pluck: square wave eighths, F mixolydian top line
    pluck_notes = [523.25, 659.25, 783.99, 698.46, 587.33, 523.25]  # C E G F D C
    p_step = beat / 2
    for k, t in enumerate(np.arange(bar * 2, total_s - 0.5, p_step)):
        if k % 8 in (3, 7):
            continue  # rest
        f = pluck_notes[k % len(pluck_notes)]
        d = p_step * 0.7
        nt = sec(d)
        w = square(f, d, n_harm=5)
        env = np.exp(-np.linspace(0, d, nt, False) * 12)
        env[: sec(0.002)] = np.linspace(0, 1, sec(0.002))
        v = lp(w * env, 5500, order=2) * 0.07
        add(bus, v, t, gain=1.0)

    # Drums: kick on every beat, clap on 2+4, hats on 16ths starting bar 3
    for beat_idx in range(int(total_s / beat) + 1):
        t = beat_idx * beat
        if t > total_s - 0.5:
            break
        if t > beat * 3:
            add(bus, kick_808(dur=0.45, base=55, pitch_env_amt=70), t, gain=0.85)
        if beat_idx % 4 in (1, 3) and t > beat * 7:
            add(bus, snap(seed=110 + beat_idx, dur=0.18), t, gain=0.55)

    sixt = beat / 4
    for s_idx in range(int(total_s / sixt)):
        t = s_idx * sixt
        if t < beat * 11 or t > total_s - 0.3:
            continue
        if s_idx % 4 == 0:
            continue
        gain = 0.55 if s_idx % 2 == 1 else 0.30
        add(bus, hat_closed(seed=200 + s_idx, dur=0.05), t, gain=gain)

    # Riser into bar 8
    rev_t = bar * 7 - 1.2
    if rev_t > 0:
        add(bus, reverse_cymbal(1.4), rev_t, gain=0.65)

    bus = lp(bus, 13000, order=2)
    stereo = _stereo_widen(bus, delay_s=0.008)
    stereo = _intro_fade(stereo, 1.2)
    stereo = _outro_fade(stereo, 2.6)
    return _master_bus(stereo, headroom=0.80)


def build_paper_room(total_s: float = 60.0) -> np.ndarray:
    """70 BPM felt piano + room tone + vinyl crackle. Editorial-paper / claude / acoustic. Cozy, intimate."""
    n = sec(total_s)
    bus = np.zeros(n)

    # Soft cello bed: C minor (Cm — C Eb G)
    cello_freqs = [130.81, 155.56, 196.00]
    for f in cello_freqs:
        bus[: n] += cello_note(f, total_s, vel=0.8)[: n] * 0.35

    # Felt piano motif: simple Cm phrase, 8th-notes on a slow grid
    bpm = 70.0
    beat = 60.0 / bpm
    motif = [
        (0.0, 261.63),  # C4
        (1.0, 311.13),  # Eb4
        (2.0, 392.00),  # G4
        (3.0, 466.16),  # Bb4 (passing tension)
        (4.0, 392.00),
        (5.0, 311.13),
        (6.0, 261.63),
        (7.5, 233.08),  # Bb3 resolve down
    ]
    motif_dur = 8 * beat
    n_loops = int(total_s / motif_dur) + 1
    for loop in range(n_loops):
        t0 = loop * motif_dur
        if t0 > total_s - 1.0:
            break
        for offset, freq in motif:
            t = t0 + offset * beat
            if t >= total_s - 0.5:
                continue
            vel = 0.85 if (offset in (0.0, 4.0)) else 0.6
            add(bus, piano_note(freq, dur=2.4, brightness=0.7, vel=vel), t, gain=0.95)

    # Counter-melody every other loop: octave above
    for loop in range(1, n_loops, 2):
        t0 = loop * motif_dur
        for offset, freq in motif[::2]:
            t = t0 + offset * beat
            if t >= total_s - 0.5:
                continue
            add(bus, piano_note(freq * 2, dur=1.6, brightness=0.5, vel=0.4), t + 0.5 * beat, gain=0.7)

    # Room tone + vinyl crackle (the texture layer)
    bus += vinyl_crackle(total_s, density=70.0) * 0.4

    bus = lp(bus, 9500, order=2)
    stereo = _stereo_widen(bus, delay_s=0.013)
    stereo = _intro_fade(stereo, 1.8)
    stereo = _outro_fade(stereo, 3.2)
    return _master_bus(stereo, headroom=0.75)


def build_dispatch(total_s: float = 60.0) -> np.ndarray:
    """92 BPM cinematic piano + cellos + low pulse. Gallery / claude / DISPATCH. Reportorial, cool, deliberate."""
    bpm = 92.0
    beat = 60.0 / bpm
    n = sec(total_s)
    bus = np.zeros(n)

    # Low cellos — Am triad (A2 C3 E3)
    for f in [110.00, 130.81, 164.81]:
        bus[: n] += cello_note(f, total_s, vel=0.85)[: n] * 0.30

    # Piano motif: deliberate, A minor, every two beats — A C E A
    motif = [(0.0, 220.00), (2.0, 261.63), (4.0, 329.63), (6.0, 440.00)]
    motif_dur = 8 * beat
    n_loops = int(total_s / motif_dur) + 1
    for loop in range(n_loops):
        t0 = loop * motif_dur
        if t0 > total_s - 0.8:
            break
        for offset, f in motif:
            t = t0 + offset * beat
            if t >= total_s - 0.5:
                continue
            vel = 0.95 if offset == 0 else 0.7
            add(bus, piano_note(f, dur=2.6, brightness=0.85, vel=vel), t, gain=0.9)
        # answer phrase in the second half: third-up notes, softer
        if loop % 2 == 1:
            for offset, f in motif:
                t = t0 + (offset + 1.0) * beat
                if t >= total_s - 0.5:
                    continue
                add(bus, piano_note(f * 1.5, dur=1.6, brightness=0.55, vel=0.45), t, gain=0.7)

    # Slow heartbeat sub-pulse on 1 of each bar
    bar = 4 * beat
    n_bars = int(total_s / bar) + 1
    for b in range(n_bars):
        t = b * bar
        if t > total_s - 0.5:
            break
        if t < bar:
            continue
        add(bus, kick_808(dur=0.7, base=42, pitch_env_amt=40), t, gain=0.45)

    # Air swell every 16 bars
    rev_t = bar * 4 - 1.4
    while rev_t < total_s - 1.5:
        add(bus, reverse_cymbal(1.4), rev_t, gain=0.45)
        rev_t += bar * 8

    bus = lp(bus, 11000, order=2)
    stereo = _stereo_widen(bus, delay_s=0.012)
    stereo = _intro_fade(stereo, 2.0)
    stereo = _outro_fade(stereo, 3.5)
    return _master_bus(stereo, headroom=0.75)


# ============ I/O ============
TRACKS = {
    "nightline":  ("Nightline",   build_nightline,  88,  "dub-techno",        "subway-chrome / mono-terminal / cctv",       ["subway-chrome", "mono-terminal", "cctv"],         "electronic"),
    "signal":     ("Signal",      build_signal,    112,  "minimal techno",    "geominimal / editorial-90s / bold launch",   ["geominimal", "editorial-90s"],                    "electronic"),
    "paper-room": ("Paper Room",  build_paper_room, 70,  "felt piano + room", "editorial-paper / claude / cozy refined",    ["editorial-paper", "claude", "gallery"],           "acoustic"),
    "dispatch":   ("Dispatch",    build_dispatch,   92,  "cinematic piano",   "gallery / claude / DISPATCH framework",      ["gallery", "claude", "editorial-paper"],           "ambient"),
}


def encode_mp3(wav_path: Path, mp3_path: Path) -> None:
    """ffmpeg WAV -> MP3 at 192k stereo, with normalization."""
    cmd = [
        "ffmpeg", "-y", "-i", str(wav_path),
        "-codec:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        str(mp3_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr[-2000:])
        raise SystemExit(f"ffmpeg encode failed for {mp3_path}")


def write_track(slug: str, out_dir: Path, total_s: float = 60.0) -> dict:
    label, builder, bpm, mood, fits, presets, palette = TRACKS[slug]
    print(f"  building {slug} ({label}) {bpm} BPM {mood} ...", flush=True)
    audio = builder(total_s)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / f"{slug}.wav"
        wavfile.write(str(wav), SR, (audio * 32767).astype(np.int16))
        mp3 = out_dir / f"{slug}.mp3"
        encode_mp3(wav, mp3)
    return {
        "slug": slug,
        "title": label,
        "file": f"{slug}.mp3",
        "bpm": bpm,
        "mood": mood,
        "fits": fits,
        "preset_packs": presets,
        "audio_palette": palette,
        "duration_s": total_s,
        "license": "in-house, public domain (no attribution required)",
        "author": "signalsniper studio",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=".claude/skills/brand-video/music")
    parser.add_argument("--total", type=float, default=60.0)
    parser.add_argument("--only", default="", help="comma list of slugs")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    selected = [s for s in TRACKS if not only or s in only]

    catalog = []
    for slug in selected:
        catalog.append(write_track(slug, out_dir, total_s=args.total))

    cat_path = out_dir / "catalog.json"
    cat_path.write_text(json.dumps({"tracks": catalog, "version": 1}, indent=2) + "\n")
    print(f"wrote {cat_path} ({len(catalog)} tracks)")


if __name__ == "__main__":
    main()
