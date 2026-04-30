#!/usr/bin/env python3
"""
editorial-kinetic-type audio synthesizer.

Produces a 25-second ambient soundtrack: Cmaj9 pad, sub drone on C2,
white-noise scene-transition swells, mallet bells on emphasis frames.

The audio is part of the format identity. Do NOT vary by theme.

Usage:
    python synth_audio.py <output.wav>
"""

import argparse
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy import signal as sig

SR = 44100
TOTAL_DUR = 25.0
TOTAL_SAMPLES = int(SR * TOTAL_DUR)

SCENE_TRANSITIONS = [3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0]
GATE_FIRST_HIT = 12.0
CLOSE_HIT_1 = 21.0
CLOSE_HIT_2 = 22.5

NOTES = {
    'C2': 65.41, 'C3': 130.81, 'E3': 164.81, 'G3': 196.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.00, 'B4': 493.88,
    'C5': 523.25, 'E5': 659.25, 'G5': 783.99,
}


def sec(t):
    return int(t * SR)


def n(name):
    return NOTES[name]


# ============ PAD ============
def evolving_pad(freqs, dur, attack=2.0, release=2.0, lfo_rate=0.15):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.zeros_like(t)
    for i, f in enumerate(freqs):
        wave += np.sin(2 * np.pi * f * t)
        detune_amt = 1 + 0.0015 * np.sin(2 * np.pi * (lfo_rate * (i + 1) * 0.7) * t)
        phase = np.cumsum(2 * np.pi * f * detune_amt / SR)
        wave += np.sin(phase) * 0.5
        wave += np.sin(2 * np.pi * f * 2 * t) * 0.08
    wave /= len(freqs) * 1.6
    b, a = sig.butter(2, 3500, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    breathing = 1 + 0.06 * np.sin(2 * np.pi * lfo_rate * t)
    wave = wave * breathing
    att_n = sec(attack)
    rel_n = sec(release)
    env = np.ones_like(wave)
    if len(env) > att_n:
        env[:att_n] = np.linspace(0, 1, att_n)
    if len(env) > rel_n:
        env[-rel_n:] = np.linspace(1, 0, rel_n)
    return wave * env


# ============ SUB DRONE ============
def sub_drone(freq, dur, attack=2.0, release=2.0):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    wave += np.sin(2 * np.pi * freq * 2 * t) * 0.2
    wave = np.tanh(wave * 1.1) * 0.9
    trem = 1 + 0.04 * np.sin(2 * np.pi * 0.13 * t)
    wave = wave * trem
    att_n = sec(attack)
    rel_n = sec(release)
    env = np.ones_like(wave)
    if len(env) > att_n:
        env[:att_n] = np.linspace(0, 1, att_n)
    if len(env) > rel_n:
        env[-rel_n:] = np.linspace(1, 0, rel_n)
    return wave * env


# ============ TRANSITIONS ============
def transition_swell(dur=1.2, peak_at=0.85, depth_freq=8000):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    np.random.seed(int(dur * 1000) % 1000)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(4, [600, depth_freq], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    peak_idx = int(peak_at * n_samp)
    env = np.zeros_like(noise)
    if peak_idx > 0:
        env[:peak_idx] = np.linspace(0, 1, peak_idx) ** 2
    if n_samp - peak_idx > 0:
        env[peak_idx:] = np.linspace(1, 0, n_samp - peak_idx) ** 1.6
    return noise * env * 0.18


def soft_thump(dur=0.5, freq_start=80, freq_end=40):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    freq = freq_start * np.exp(-t * 6) + freq_end
    phase = np.cumsum(2 * np.pi * freq / SR)
    body = np.sin(phase)
    env = np.exp(-t * 3.5)
    att_n = sec(0.02)
    if n_samp > att_n:
        env[:att_n] *= np.linspace(0, 1, att_n)
    return body * env * 0.55


# ============ MALLET ============
def mallet(freq, dur=2.0):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t) * 1.0
    wave += np.sin(2 * np.pi * freq * 2.0 * t) * 0.35 * np.exp(-t * 2.5)
    wave += np.sin(2 * np.pi * freq * 3.01 * t) * 0.18 * np.exp(-t * 4.5)
    wave += np.sin(2 * np.pi * freq * 4.7 * t) * 0.08 * np.exp(-t * 7)
    b, a = sig.butter(2, 5000, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    att_n = sec(0.005)
    env = np.ones_like(wave)
    env[:att_n] = np.linspace(0, 1, att_n)
    env *= np.exp(-t * 1.5)
    return wave * env * 0.45


# ============ UI TICK ============
def ui_tick(dur=0.08):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    np.random.seed(99)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(4, [3000, 10000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    env = np.exp(-t * 90)
    return noise * env * 0.08


# ============ MIXER ============
def add(track, sample, t_start, gain=1.0):
    start = sec(t_start)
    if start >= len(track) or start < 0:
        return
    end = min(start + len(sample), len(track))
    track[start:end] += sample[:end - start] * gain


def build_track():
    track = np.zeros(TOTAL_SAMPLES)

    # Pad layers
    pad_freqs = [n('C4'), n('E4'), n('G4'), n('B4'), n('D4')]
    add(track, evolving_pad(pad_freqs, TOTAL_DUR, attack=3.0, release=4.0, lfo_rate=0.12), 0, gain=0.65)
    add(track, evolving_pad([n('C3'), n('G3')], TOTAL_DUR, attack=4.0, release=4.0, lfo_rate=0.09), 0, gain=0.5)

    # Sub drone
    add(track, sub_drone(n('C2'), TOTAL_DUR, attack=3.5, release=3.5), 0, gain=0.45)

    # Scene transitions
    for tr in SCENE_TRANSITIONS:
        add(track, transition_swell(dur=1.2, peak_at=0.83), tr - 1.0, gain=1.0)
        add(track, soft_thump(dur=0.6), tr, gain=0.55)

    # Mallets
    add(track, mallet(n('C5'), dur=2.5), GATE_FIRST_HIT, gain=0.85)
    add(track, mallet(n('G4'), dur=2.5), GATE_FIRST_HIT + 0.08, gain=0.4)
    add(track, mallet(n('C5'), dur=3.0), CLOSE_HIT_1, gain=0.75)
    add(track, mallet(n('E5'), dur=3.0), CLOSE_HIT_1 + 0.04, gain=0.45)
    add(track, mallet(n('G5'), dur=3.0), CLOSE_HIT_2, gain=0.65)

    # UI ticks
    tick_times = [0.6, 3.4, 3.8, 4.1, 4.4, 6.4, 9.4, 15.4, 15.8, 16.4, 18.4]
    for tt in tick_times:
        if tt < TOTAL_DUR:
            add(track, ui_tick(), tt, gain=0.7)

    # Master
    track = np.tanh(track * 0.95) * 0.95
    b, a = sig.butter(2, 13000, btype='low', fs=SR)
    track = sig.lfilter(b, a, track)
    np.random.seed(5)
    air = np.random.normal(0, 0.0015, len(track))
    b, a = sig.butter(2, [400, 6000], btype='band', fs=SR)
    air = sig.lfilter(b, a, air)
    track = track + air
    fade_n = sec(2.5)
    track[-fade_n:] *= np.linspace(1, 0, fade_n)
    peak = np.max(np.abs(track))
    if peak > 0:
        track = track / peak * 0.6

    width_delay = sec(0.008)
    left = track.copy()
    right = track.copy()
    if len(right) > width_delay:
        right[width_delay:] = right[:-width_delay]
    stereo = np.column_stack([left, right])
    return (stereo * 32767).astype(np.int16)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="Path to write WAV file")
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    audio = build_track()
    wavfile.write(str(out_path), SR, audio)
    print(f"wrote {out_path}, {audio.shape[0]/SR:.2f}s")


if __name__ == "__main__":
    main()
