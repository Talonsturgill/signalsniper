#!/usr/bin/env python3
"""
editorial-kinetic-type audio synthesizer.

Three named audio variants share the same Cmaj-family pad and C2 sub
drone but differ in how scene boundaries are marked and how the two
emphasis hits at 12.0s and 21.0s/22.5s sound:

    ambient  white-noise transition swells, sub thumps, mallet bells,
             UI ticks. The original format-identity score.
    minimal  sine shimmers on chord tones at boundaries, soft glass
             bells at the emphasis moments, no swells, no thumps,
             no UI ticks. Reads like a product-drop pad bloom.
    warm     Cmaj7 pad (drop the 9th), octave-down sine lift tones at
             boundaries, felted-piano bells at the emphasis moments.
             No swells.

Used by build_html.py (via the spec field) and by record_mp4.py for
the MP4 mux. The HTML's Web Audio score must mirror whichever variant
this script produces, scheduled at the same sync points.

Usage:
    python synth_audio.py <output.wav> [--audio-variant ambient|minimal|warm]
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

SHIMMER_NOTES_HZ = [523.25, 659.25, 783.99, 987.77, 587.33, 659.25, 783.99]
LIFT_NOTES_HZ = [130.81, 164.81, 196.00, 246.94, 146.83, 164.81, 196.00]

VARIANTS = ("ambient", "minimal", "warm")

NOTES = {
    'C2': 65.41, 'C3': 130.81, 'E3': 164.81, 'G3': 196.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.00, 'B4': 493.88,
    'C5': 523.25, 'E5': 659.25, 'G5': 783.99,
}


def sec(t):
    return int(t * SR)


def n(name):
    return NOTES[name]


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


def transition_swell(dur=1.2, peak_at=0.85, depth_freq=8000):
    n_samp = sec(dur)
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


def ui_tick(dur=0.08):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    np.random.seed(99)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(4, [3000, 10000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    env = np.exp(-t * 90)
    return noise * env * 0.08


def shimmer(freq, dur=1.8):
    """Pure sine on a chord tone with a triangular fade. Used by the
    minimal variant at scene boundaries."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    half = n_samp // 2
    env = np.zeros(n_samp)
    env[:half] = np.linspace(0, 1, half)
    env[half:] = np.linspace(1, 0, n_samp - half)
    return wave * env


def glass_bell(freq, dur=2.5):
    """Sine fundamental + 2nd partial with quick decay. Brighter than a
    mallet, quieter — used by the minimal variant at emphasis moments."""
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
    return fund * fund_env + partial


def lift_tone(freq, dur=2.2):
    """Low sine with a slow fade-in and fade-out, used by the warm
    variant at scene boundaries. Triangular envelope, peak at midpoint."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    wave += np.sin(2 * np.pi * freq * 2 * t) * 0.15
    half = n_samp // 2
    env = np.zeros(n_samp)
    env[:half] = np.linspace(0, 1, half) ** 1.4
    env[half:] = np.linspace(1, 0, n_samp - half) ** 1.4
    return wave * env


def felted_piano(freq, dur=2.8):
    """Soft attack, long decay, dampened upper partials. Suggests a
    felted-piano hammer rather than a hard mallet. Warm variant only."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t) * 1.0
    wave += np.sin(2 * np.pi * freq * 2.0 * t) * 0.22 * np.exp(-t * 1.8)
    wave += np.sin(2 * np.pi * freq * 3.0 * t) * 0.08 * np.exp(-t * 3.2)
    b, a = sig.butter(2, 3200, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    att_n = sec(0.04)
    env = np.ones_like(wave)
    if n_samp > att_n:
        env[:att_n] = np.linspace(0, 1, att_n) ** 0.7
    env *= np.exp(-t * 1.1)
    return wave * env


def add(track, sample, t_start, gain=1.0):
    start = sec(t_start)
    if start >= len(track) or start < 0:
        return
    end = min(start + len(sample), len(track))
    track[start:end] += sample[:end - start] * gain


def master(track):
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


def build_track_ambient():
    track = np.zeros(TOTAL_SAMPLES)
    pad_freqs = [n('C4'), n('E4'), n('G4'), n('B4'), n('D4')]
    add(track, evolving_pad(pad_freqs, TOTAL_DUR, attack=3.0, release=4.0, lfo_rate=0.12), 0, gain=0.65)
    add(track, evolving_pad([n('C3'), n('G3')], TOTAL_DUR, attack=4.0, release=4.0, lfo_rate=0.09), 0, gain=0.5)
    add(track, sub_drone(n('C2'), TOTAL_DUR, attack=3.5, release=3.5), 0, gain=0.45)
    for tr in SCENE_TRANSITIONS:
        add(track, transition_swell(dur=1.2, peak_at=0.83), tr - 1.0, gain=1.0)
        add(track, soft_thump(dur=0.6), tr, gain=0.55)
    add(track, mallet(n('C5'), dur=2.5), GATE_FIRST_HIT, gain=0.85)
    add(track, mallet(n('G4'), dur=2.5), GATE_FIRST_HIT + 0.08, gain=0.4)
    add(track, mallet(n('C5'), dur=3.0), CLOSE_HIT_1, gain=0.75)
    add(track, mallet(n('E5'), dur=3.0), CLOSE_HIT_1 + 0.04, gain=0.45)
    add(track, mallet(n('G5'), dur=3.0), CLOSE_HIT_2, gain=0.65)
    for tt in [0.6, 3.4, 3.8, 4.1, 4.4, 6.4, 9.4, 15.4, 15.8, 16.4, 18.4]:
        if tt < TOTAL_DUR:
            add(track, ui_tick(), tt, gain=0.7)
    return master(track)


def build_track_minimal():
    track = np.zeros(TOTAL_SAMPLES)
    pad_freqs = [n('C4'), n('E4'), n('G4'), n('B4'), n('D4')]
    add(track, evolving_pad(pad_freqs, TOTAL_DUR, attack=3.0, release=4.0, lfo_rate=0.12), 0, gain=0.65)
    add(track, evolving_pad([n('C3'), n('G3')], TOTAL_DUR, attack=4.0, release=4.0, lfo_rate=0.09), 0, gain=0.5)
    add(track, sub_drone(n('C2'), TOTAL_DUR, attack=3.5, release=3.5), 0, gain=0.45)
    for tr, freq in zip(SCENE_TRANSITIONS, SHIMMER_NOTES_HZ):
        add(track, shimmer(freq, dur=1.8), tr - 0.6, gain=0.32)
    add(track, glass_bell(n('C5'), dur=2.5), GATE_FIRST_HIT, gain=0.55)
    add(track, glass_bell(n('C5'), dur=2.5), CLOSE_HIT_1, gain=0.5)
    add(track, glass_bell(n('G5'), dur=2.5), CLOSE_HIT_2, gain=0.42)
    return master(track)


def build_track_warm():
    track = np.zeros(TOTAL_SAMPLES)
    # Cmaj7 pad — drop the 9th D for less tension, more grounded
    pad_freqs = [n('C4'), n('E4'), n('G4'), n('B4')]
    add(track, evolving_pad(pad_freqs, TOTAL_DUR, attack=3.5, release=4.5, lfo_rate=0.10), 0, gain=0.7)
    add(track, evolving_pad([n('C3'), n('G3')], TOTAL_DUR, attack=4.0, release=4.0, lfo_rate=0.08), 0, gain=0.55)
    add(track, sub_drone(n('C2'), TOTAL_DUR, attack=3.5, release=3.5), 0, gain=0.5)
    for tr, freq in zip(SCENE_TRANSITIONS, LIFT_NOTES_HZ):
        add(track, lift_tone(freq, dur=2.2), tr - 0.8, gain=0.34)
    add(track, felted_piano(n('C5'), dur=2.8), GATE_FIRST_HIT, gain=0.55)
    add(track, felted_piano(n('G4'), dur=2.8), GATE_FIRST_HIT + 0.06, gain=0.32)
    add(track, felted_piano(n('C5'), dur=3.0), CLOSE_HIT_1, gain=0.5)
    add(track, felted_piano(n('E5'), dur=3.0), CLOSE_HIT_1 + 0.03, gain=0.3)
    add(track, felted_piano(n('G5'), dur=3.0), CLOSE_HIT_2, gain=0.44)
    return master(track)


def build_track(variant):
    if variant == "ambient":
        return build_track_ambient()
    if variant == "minimal":
        return build_track_minimal()
    if variant == "warm":
        return build_track_warm()
    raise ValueError(f"unknown audio variant: {variant!r}, expected one of {VARIANTS}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="Path to write WAV file")
    parser.add_argument("--audio-variant", choices=VARIANTS, default="ambient",
                        help="which audio score to render (default: ambient)")
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    audio = build_track(args.audio_variant)
    wavfile.write(str(out_path), SR, audio)
    print(f"wrote {out_path} ({args.audio_variant}, {audio.shape[0]/SR:.2f}s)")


if __name__ == "__main__":
    main()
