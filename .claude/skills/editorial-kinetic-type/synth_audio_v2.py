#!/usr/bin/env python3
"""
editorial-kinetic-type audio synthesizer, v2 (minimal product-drop variant).

Same Cmaj9 pad and C2 sub drone as v1. Removes the white-noise transition
swells, the soft sub thumps at boundaries, and the high-passed UI ticks.
Adds subtle harmonic shimmers (pure sines on chord tones) at scene
boundaries and softer glass-bell chimes at the two emphasis moments.

Used only by tribute-2026-05-01-v2.html. The canonical synth_audio.py
is unchanged so the daily routine keeps producing v1 audio.

Usage:
    python synth_audio_v2.py <output.wav>
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

# Cmaj9 chord tones used for both the pad voicing and the boundary shimmers.
SHIMMER_NOTES_HZ = [523.25, 659.25, 783.99, 987.77, 587.33, 659.25, 783.99]

NOTES = {
    'C2': 65.41, 'C3': 130.81, 'E3': 164.81, 'G3': 196.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.00, 'B4': 493.88,
    'C5': 523.25, 'E5': 659.25, 'G5': 783.99,
}


def sec(t):
    return int(t * SR)


def n(name):
    return NOTES[name]


# ============ PAD (unchanged from v1) ============
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


# ============ SUB DRONE (unchanged from v1) ============
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


# ============ SHIMMER (new) ============
def shimmer(freq, dur=1.8):
    """Pure sine on a chord tone, slow linear fade in then fade out.
    Mirrors playShimmer in the HTML."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    half = n_samp // 2
    env = np.zeros(n_samp)
    env[:half] = np.linspace(0, 1, half)
    env[half:] = np.linspace(1, 0, n_samp - half)
    return wave * env


# ============ GLASS BELL (new) ============
def glass_bell(freq, dur=2.5):
    """Sine fundamental + 2nd partial with quick decay. Brighter than the
    v1 mallet, but quieter — mirrors playGlassBell in the HTML."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    fund = np.sin(2 * np.pi * freq * t)
    partial_dur_n = sec(min(dur, 1.6))
    partial_t = t[:partial_dur_n]
    partial_env = np.exp(-partial_t * 3.5)
    partial = np.zeros(n_samp)
    partial[:partial_dur_n] = np.sin(2 * np.pi * freq * 2.01 * partial_t) * partial_env * 0.35
    fund_env = np.exp(-t * 1.5)
    att_n = sec(0.01)
    if n_samp > att_n:
        fund_env[:att_n] *= np.linspace(0, 1, att_n)
    wave = fund * fund_env + partial
    return wave


# ============ MIXER ============
def add(track, sample, t_start, gain=1.0):
    start = sec(t_start)
    if start >= len(track) or start < 0:
        return
    end = min(start + len(sample), len(track))
    track[start:end] += sample[:end - start] * gain


def build_track():
    track = np.zeros(TOTAL_SAMPLES)

    pad_freqs = [n('C4'), n('E4'), n('G4'), n('B4'), n('D4')]
    add(track, evolving_pad(pad_freqs, TOTAL_DUR, attack=3.0, release=4.0, lfo_rate=0.12), 0, gain=0.65)
    add(track, evolving_pad([n('C3'), n('G3')], TOTAL_DUR, attack=4.0, release=4.0, lfo_rate=0.09), 0, gain=0.5)

    add(track, sub_drone(n('C2'), TOTAL_DUR, attack=3.5, release=3.5), 0, gain=0.45)

    # Boundary shimmers: same chord-tone progression as the HTML.
    for tr, freq in zip(SCENE_TRANSITIONS, SHIMMER_NOTES_HZ):
        add(track, shimmer(freq, dur=1.8), tr - 0.6, gain=0.32)

    # Two glass bells at the emphasis moments.
    add(track, glass_bell(n('C5'), dur=2.5), GATE_FIRST_HIT, gain=0.55)
    add(track, glass_bell(n('C5'), dur=2.5), CLOSE_HIT_1, gain=0.5)
    add(track, glass_bell(n('G5'), dur=2.5), CLOSE_HIT_2, gain=0.42)

    # Master bus: same chain as v1 (saturate + low-pass + airy noise + outro fade + normalize).
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
