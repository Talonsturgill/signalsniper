#!/usr/bin/env python3
"""
brand-video audio synthesizer with palettes.

Three palettes:
- ambient:     Cmaj9 pad + sub drone + swells + mallets (default, editorial register)
- electronic:  arpeggiated synth + sub pulse + glitch hits + harder mallets (mono register)
- acoustic:    felt piano clusters + soft strings + paper foley + wood mallets (refined register)

A foley layer rides on top of every palette:
- whoosh 200ms before each scene boundary
- thud on impact at the boundary
- typewriter ticks at UI moments
- stamp on emphasize beats

Usage:
    python synth_audio.py --bv-meta '<json>' --output out.wav

bv-meta is a JSON string like:
  {
    "total_s": 22.0,
    "timeline": [{"start": 0, ...}, {"start": 3, ...}, ...],
    "emphases": [12.0, 21.0],
    "audio_palette": "electronic"
  }
"""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy import signal as sig

SR = 44100

NOTES = {
    'C2': 65.41, 'G2': 98.00, 'C3': 130.81, 'E3': 164.81, 'G3': 196.00,
    'B3': 246.94, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.00,
    'A4': 440.00, 'B4': 493.88, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25,
    'G5': 783.99, 'A5': 880.00,
}


def sec(t):
    return int(t * SR)


def n(name):
    return NOTES[name]


# ============ ENVELOPES & MIX ============
def add(track, sample, t_start, gain=1.0):
    start = sec(t_start)
    if start >= len(track) or start < 0:
        return
    end = min(start + len(sample), len(track))
    track[start:end] += sample[:end - start] * gain


def env_attack_release(length, attack_s, release_s):
    env = np.ones(length)
    a = sec(attack_s)
    r = sec(release_s)
    if length > a:
        env[:a] = np.linspace(0, 1, a)
    if length > r:
        env[-r:] = np.linspace(1, 0, r)
    return env


# ============ AMBIENT PALETTE ============
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
    return wave * env_attack_release(n_samp, attack, release)


def sub_drone(freq, dur, attack=2.0, release=2.0):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    wave += np.sin(2 * np.pi * freq * 2 * t) * 0.2
    wave = np.tanh(wave * 1.1) * 0.9
    trem = 1 + 0.04 * np.sin(2 * np.pi * 0.13 * t)
    wave = wave * trem
    return wave * env_attack_release(n_samp, attack, release)


def transition_swell(seed, dur=1.2, peak_at=0.85, depth_freq=8000):
    n_samp = sec(dur)
    np.random.seed(seed)
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
    att = sec(0.02)
    if n_samp > att:
        env[:att] *= np.linspace(0, 1, att)
    return body * env * 0.55


def mallet(freq, dur=2.0, brightness=1.0):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t) * 1.0
    wave += np.sin(2 * np.pi * freq * 2.0 * t) * 0.35 * np.exp(-t * 2.5)
    wave += np.sin(2 * np.pi * freq * 3.01 * t) * 0.18 * brightness * np.exp(-t * 4.5)
    wave += np.sin(2 * np.pi * freq * 4.7 * t) * 0.08 * brightness * np.exp(-t * 7)
    b, a = sig.butter(2, 5000, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    att = sec(0.005)
    env = np.ones_like(wave)
    env[:att] = np.linspace(0, 1, att)
    env *= np.exp(-t * 1.5)
    return wave * env * 0.45


def build_ambient(total_s, transitions, emphases):
    track = np.zeros(int(SR * total_s))
    pad_freqs = [n('C4'), n('E4'), n('G4'), n('B4'), n('D4')]
    add(track, evolving_pad(pad_freqs, total_s, attack=3.0, release=4.0, lfo_rate=0.12), 0, gain=0.65)
    add(track, evolving_pad([n('C3'), n('G3')], total_s, attack=4.0, release=4.0, lfo_rate=0.09), 0, gain=0.5)
    add(track, sub_drone(n('C2'), total_s, attack=3.5, release=3.5), 0, gain=0.45)
    for em in emphases:
        if em < 0 or em >= total_s:
            continue
        add(track, mallet(n('C5'), dur=2.5), em, gain=0.85)
        add(track, mallet(n('G4'), dur=2.5), em + 0.05, gain=0.4)
    return track


# ============ ELECTRONIC PALETTE ============
def arp_synth(freqs, dur, rate_hz=4.0, attack=1.5, release=2.0):
    """Arpeggiated saw-like synth that cycles through freqs at rate_hz."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    period = 1.0 / rate_hz
    note_idx = (np.floor(t / period).astype(int)) % len(freqs)
    note_t = t - np.floor(t / period) * period
    wave = np.zeros_like(t)
    for i, f in enumerate(freqs):
        mask = note_idx == i
        # saw approximation via 7 harmonics
        w = np.zeros_like(t)
        for h in range(1, 8):
            w += np.sin(2 * np.pi * f * h * t) / h
        w *= mask
        # quick decay each note
        decay = np.exp(-note_t * 6.0) * mask
        wave += w * decay * 0.12
    b, a = sig.butter(3, 4500, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    return wave * env_attack_release(n_samp, attack, release)


def sub_pulse(freq, dur, rate_hz=2.0, attack=1.5, release=2.0):
    """Pulsing sub bass that ducks rhythmically."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    wave += np.sin(2 * np.pi * freq * 2 * t) * 0.18
    pulse = 0.5 + 0.5 * np.sin(2 * np.pi * rate_hz * t - np.pi / 2) ** 4
    wave = wave * pulse * 0.85
    return wave * env_attack_release(n_samp, attack, release)


def glitch_hit(seed, dur=0.18):
    n_samp = sec(dur)
    np.random.seed(seed)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(4, [1500, 9000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    t = np.linspace(0, dur, n_samp, False)
    env = np.exp(-t * 14.0)
    return noise * env * 0.5


def hard_mallet(freq, dur=1.4):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.5 * np.exp(-t * 3.0)
    wave += np.sin(2 * np.pi * freq * 2.78 * t) * 0.3 * np.exp(-t * 5.0)
    wave = np.tanh(wave * 1.4) * 0.7
    env = np.ones_like(wave)
    a_n = sec(0.003)
    env[:a_n] = np.linspace(0, 1, a_n)
    env *= np.exp(-t * 2.4)
    return wave * env * 0.55


def build_electronic(total_s, transitions, emphases):
    track = np.zeros(int(SR * total_s))
    arp_freqs = [n('C4'), n('E4'), n('G4'), n('B4'), n('A4'), n('G4')]
    add(track, arp_synth(arp_freqs, total_s, rate_hz=3.6, attack=1.5, release=3.0), 0, gain=0.55)
    add(track, sub_pulse(n('C2'), total_s, rate_hz=1.8, attack=2.0, release=3.0), 0, gain=0.50)
    # glitch texture every ~0.6s lightly
    for tt in np.arange(0.6, total_s - 0.5, 0.62):
        add(track, glitch_hit(int(tt * 1000) % 9999, dur=0.14), tt, gain=0.18)
    for em in emphases:
        if em < 0 or em >= total_s:
            continue
        add(track, hard_mallet(n('C5'), dur=1.2), em, gain=0.8)
        add(track, hard_mallet(n('G5'), dur=1.0), em + 0.04, gain=0.35)
    return track


# ============ ACOUSTIC PALETTE ============
def piano_cluster(freqs, dur, attack=1.6, release=2.4):
    """Soft felt-piano cluster, multiple notes held with slight detune."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.zeros_like(t)
    for i, f in enumerate(freqs):
        # piano-like: fundamental + a few harmonics with quick decay on highs
        w = np.sin(2 * np.pi * f * t)
        w += np.sin(2 * np.pi * f * 2.0 * t) * 0.4 * np.exp(-t * 0.8)
        w += np.sin(2 * np.pi * f * 3.0 * t) * 0.15 * np.exp(-t * 1.6)
        w += np.sin(2 * np.pi * f * 4.0 * t) * 0.08 * np.exp(-t * 2.4)
        # gentle vibrato
        vib = 1 + 0.0008 * np.sin(2 * np.pi * 4.5 * t + i * 0.3)
        phase = np.cumsum(2 * np.pi * f * vib / SR)
        w += 0.3 * np.sin(phase) * np.exp(-t * 0.6)
        wave += w * 0.18
    b, a = sig.butter(2, 4200, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    return wave * env_attack_release(n_samp, attack, release)


def soft_strings(freqs, dur, attack=3.0, release=3.0):
    """Bowed-string-style sustained notes."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.zeros_like(t)
    for f in freqs:
        # narrow saw via 5 harmonics with slight detune
        for i, h in enumerate(range(1, 6)):
            wave += np.sin(2 * np.pi * f * h * t * (1 + 0.0006 * (i - 2))) * (1.0 / h)
    wave /= len(freqs) * 5
    b, a = sig.butter(3, 3000, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    # slow swell
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t - 1.0)
    wave *= swell
    return wave * env_attack_release(n_samp, attack, release) * 0.4


def wood_mallet(freq, dur=1.6):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.sin(2 * np.pi * freq * t)
    wave += np.sin(2 * np.pi * freq * 2.0 * t) * 0.22 * np.exp(-t * 3.0)
    wave += np.sin(2 * np.pi * freq * 5.4 * t) * 0.06 * np.exp(-t * 9.0)
    b, a = sig.butter(2, 3500, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    env = np.ones_like(wave)
    a_n = sec(0.008)
    env[:a_n] = np.linspace(0, 1, a_n)
    env *= np.exp(-t * 1.8)
    return wave * env * 0.42


def paper_rustle(seed, dur=0.32):
    n_samp = sec(dur)
    np.random.seed(seed)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(4, [3500, 9000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    t = np.linspace(0, dur, n_samp, False)
    env = np.exp(-t * 10.0)
    # add a small attack ramp
    a_n = sec(0.02)
    if n_samp > a_n:
        env[:a_n] *= np.linspace(0, 1, a_n)
    return noise * env * 0.35


def build_acoustic(total_s, transitions, emphases):
    track = np.zeros(int(SR * total_s))
    piano_freqs = [n('C4'), n('E4'), n('G4'), n('B4')]
    add(track, piano_cluster(piano_freqs, total_s, attack=2.5, release=4.0), 0, gain=0.55)
    add(track, soft_strings([n('C3'), n('G3')], total_s, attack=4.0, release=4.0), 0, gain=0.50)
    add(track, sub_drone(n('C2'), total_s, attack=3.5, release=3.5), 0, gain=0.30)
    for em in emphases:
        if em < 0 or em >= total_s:
            continue
        add(track, wood_mallet(n('C5'), dur=1.6), em, gain=0.78)
        add(track, wood_mallet(n('E5'), dur=1.2), em + 0.06, gain=0.40)
    return track


# ============ FOLEY (rides every palette) ============
def whoosh(seed, dur=0.45):
    n_samp = sec(dur)
    np.random.seed(seed)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(3, [400, 5000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    t = np.linspace(0, dur, n_samp, False)
    # rising-then-falling envelope
    env = np.zeros_like(t)
    peak = int(0.7 * n_samp)
    env[:peak] = (np.linspace(0, 1, peak)) ** 1.5
    env[peak:] = np.linspace(1, 0, n_samp - peak) ** 1.6
    return noise * env * 0.30


def thud(dur=0.4):
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    f = 60 * np.exp(-t * 5) + 30
    phase = np.cumsum(2 * np.pi * f / SR)
    body = np.sin(phase) + 0.5 * np.sin(phase * 2)
    env = np.exp(-t * 4.5)
    a_n = sec(0.005)
    if n_samp > a_n:
        env[:a_n] *= np.linspace(0, 1, a_n)
    return body * env * 0.55


def typewriter_tick(seed, dur=0.06):
    n_samp = sec(dur)
    np.random.seed(seed)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(4, [2500, 8000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    t = np.linspace(0, dur, n_samp, False)
    env = np.exp(-t * 80)
    return noise * env * 0.10


def riser(seed, dur=0.85):
    """Rising-pitch noise+tone that ratchets tension into a hit (trailer grammar:
    the whoosh/riser is the build-up, the braam is the payoff)."""
    n_samp = sec(dur)
    np.random.seed(seed)
    t = np.linspace(0, dur, n_samp, False)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(3, [300, 9000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    tone_f = 190 * np.exp(t / dur * 1.7)
    tone = np.sin(np.cumsum(2 * np.pi * tone_f / SR))
    env = (t / dur) ** 2.0
    return (noise * 0.5 + tone * 0.4) * env * 0.28


def braam(freq=70, dur=1.1):
    """Big brassy detuned cinematic hit -- the ubiquitous trailer 'braam'."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    wave = np.zeros_like(t)
    for f in (freq, freq * 1.5, freq * 2.01, freq * 3.0):
        for h in range(1, 6):
            wave += np.sin(2 * np.pi * f * h * t * 1.001) / (h * 1.2)
    wave = np.tanh(wave * 0.8)
    b, a = sig.butter(3, 2200, btype='low', fs=SR)
    wave = sig.lfilter(b, a, wave)
    env = np.ones_like(t)
    att = sec(0.02)
    env[:att] = np.linspace(0, 1, att)
    env *= np.exp(-t * 1.6)
    return wave * env * 0.5


def tape_stop(seed, dur=0.5):
    """Pitch-plummeting tape-stop into a cut (modern/electronic transition)."""
    n_samp = sec(dur)
    np.random.seed(seed)
    t = np.linspace(0, dur, n_samp, False)
    f = 380 * np.exp(-t * 7) + 30
    tone = np.sin(np.cumsum(2 * np.pi * f / SR))
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(3, [200, 4000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    env = np.exp(-t * 3.5)
    return (tone * 0.6 + noise * 0.3) * env * 0.4


def soft_click(seed, dur=0.05):
    """A discreet UI click for restrained cuts (the research: do not overdo it)."""
    n_samp = sec(dur)
    np.random.seed(seed)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(2, [1200, 4500], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    t = np.linspace(0, dur, n_samp, False)
    env = np.exp(-t * 90)
    return noise * env * 0.18


def sub_boom(freq=44, dur=0.7):
    """Deep sub impact/'drop' -- releases tension, a beat to soak it in."""
    n_samp = sec(dur)
    t = np.linspace(0, dur, n_samp, False)
    f = freq * np.exp(-t * 3) + 28
    body = np.tanh(np.sin(np.cumsum(2 * np.pi * f / SR)) * 1.2)
    env = np.exp(-t * 3.2)
    att = sec(0.004)
    env[:att] *= np.linspace(0, 1, att)
    return body * env * 0.7


def reverse_swell(seed, dur=0.7):
    """Reverse-cymbal-style swell that crescendos INTO the cut."""
    n_samp = sec(dur)
    np.random.seed(seed)
    t = np.linspace(0, dur, n_samp, False)
    noise = np.random.uniform(-1, 1, n_samp)
    b, a = sig.butter(4, [800, 8000], btype='band', fs=SR)
    noise = sig.lfilter(b, a, noise)
    env = (t / dur) ** 2.2
    return noise * env * 0.30


# Foley families. Each video is assigned ONE (non-repeating via variety_check)
# so the transient grammar -- the "swipe" the viewer hears -- differs every day.
# Grounded in trailer/motion sound grammar: whoosh+hit is a build-up/payoff pair;
# risers pair with braams; a drop is a dead-stop; and not every cut needs a swipe.
FOLEY_STYLES = ("whoosh_thud", "riser_braam", "tapestop_drop",
                "click_minimal", "sub_impact", "reverse_swell")


def build_foley(total_s, transitions, emphases, rich=False,
                style="whoosh_thud", seed_base=1000):
    """Foley bus. rich=False keeps the legacy minimal preview bed. rich=True is
    the shipping stem layered OVER the music by the finishing mux, ducked by the
    mixer. `style` selects the transient family (FOLEY_STYLES); `seed_base` is
    date-derived so even a recurring family is never byte-identical."""
    track = np.zeros(int(SR * total_s))
    if not rich:
        for em in emphases:
            if 0 <= em < total_s:
                add(track, thud(dur=0.45), em, gain=0.22)
        return track
    if style not in FOLEY_STYLES:
        style = "whoosh_thud"
    em_set = set(round(e, 2) for e in emphases)
    S = seed_base
    for i, tt in enumerate(transitions):
        if tt <= 0.1 or tt >= total_s - 0.1:
            continue
        is_em = round(tt, 2) in em_set
        if style == "whoosh_thud":
            add(track, whoosh(S + i, 0.42), tt - 0.24, gain=0.55)
            if not is_em:
                add(track, thud(0.34), tt - 0.01, gain=0.38)
        elif style == "riser_braam":
            add(track, whoosh(S + i, 0.28), tt - 0.14, gain=0.26)
            if not is_em:
                add(track, soft_click(S + i, 0.05), tt, gain=0.5)
        elif style == "tapestop_drop":
            if i % 2 == 0:
                add(track, tape_stop(S + i, 0.5), tt - 0.26, gain=0.5)
            if not is_em:
                add(track, soft_click(S + i, 0.05), tt, gain=0.42)
        elif style == "click_minimal":
            add(track, soft_click(S + i, 0.05), tt, gain=0.6)
        elif style == "sub_impact":
            add(track, transition_swell(S + i, 0.9, 0.92), tt - 0.72, gain=0.5)
            if not is_em:
                add(track, soft_click(S + i, 0.05), tt, gain=0.34)
        elif style == "reverse_swell":
            add(track, reverse_swell(S + i, 0.68), tt - 0.66, gain=0.5)
            if not is_em:
                add(track, thud(0.3), tt - 0.01, gain=0.30)
    for j, em in enumerate(emphases):
        if not (0 <= em < total_s):
            continue
        if style == "whoosh_thud":
            add(track, thud(0.5), em - 0.01, gain=0.62)
            add(track, glitch_hit(S + 2000 + j, 0.12), em, gain=0.30)
        elif style == "riser_braam":
            add(track, riser(S + 3000 + j, 0.8), em - 0.8, gain=0.5)
            add(track, braam(70, 1.1), em, gain=0.55)
        elif style == "tapestop_drop":
            add(track, sub_boom(46, 0.7), em, gain=0.62)
        elif style == "click_minimal":
            add(track, sub_boom(44, 0.5), em, gain=0.42)
        elif style == "sub_impact":
            add(track, sub_boom(42, 0.8), em, gain=0.7)
            add(track, thud(0.4), em, gain=0.3)
        elif style == "reverse_swell":
            add(track, thud(0.5), em, gain=0.5)
            add(track, sub_boom(48, 0.5), em, gain=0.35)
    return track


# ============ MASTER ============
PALETTES = {
    "ambient": build_ambient,
    "electronic": build_electronic,
    "acoustic": build_acoustic,
}


def master_chain(track, total_s):
    track = np.tanh(track * 0.95) * 0.95
    b, a = sig.butter(2, 13000, btype='low', fs=SR)
    track = sig.lfilter(b, a, track)
    np.random.seed(5)
    air = np.random.normal(0, 0.0015, len(track))
    b, a = sig.butter(2, [400, 6000], btype='band', fs=SR)
    air = sig.lfilter(b, a, air)
    track = track + air
    fade_n = sec(min(2.5, total_s * 0.12))
    if fade_n > 0:
        track[-fade_n:] *= np.linspace(1, 0, fade_n)
    peak = np.max(np.abs(track))
    if peak > 0:
        track = track / peak * 0.6
    width_delay = sec(0.008)
    left = track.copy()
    right = track.copy()
    if len(right) > width_delay:
        right[width_delay:] = right[:-width_delay]
    return np.column_stack([left, right])


def build_track(palette, total_s, transitions, emphases):
    builder = PALETTES.get(palette, PALETTES["ambient"])
    music = builder(total_s, transitions, emphases)
    foley = build_foley(total_s, transitions, emphases)
    return master_chain(music + foley, total_s)


def build_foley_track(total_s, transitions, emphases,
                      style="whoosh_thud", seed_base=1000):
    """Foley-only stem for the finishing mux (no pad, no normalization frenzy)."""
    foley = build_foley(total_s, transitions, emphases, rich=True,
                        style=style, seed_base=seed_base)
    peak = np.max(np.abs(foley))
    if peak > 0:
        foley = foley / peak * 0.7
    return np.column_stack([foley, foley])


def parse_floats(s):
    if not s:
        return []
    return [float(x) for x in s.split(",") if x.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total", type=float)
    parser.add_argument("--transitions", default="")
    parser.add_argument("--emphases", default="")
    parser.add_argument("--palette", default="ambient", choices=list(PALETTES))
    parser.add_argument("--bv-meta", help="Inline JSON {total_s, timeline:[{start}], emphases:[], audio_palette:'..'}")
    parser.add_argument("--foley-only", action="store_true",
                        help="Emit only the rich foley stem (transient grammar at cuts, hit on emphases) for the finishing mux")
    parser.add_argument("--foley-style", default=None, choices=list(FOLEY_STYLES),
                        help="Transient family for the shipping foley (defaults to bv-meta.foley_style or whoosh_thud)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Date-derived seed so a recurring foley family is never byte-identical")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    foley_style = args.foley_style
    seed_base = 1000 if args.seed is None else 1000 + (args.seed % 90000)
    if args.bv_meta:
        meta = json.loads(args.bv_meta)
        total = float(meta["total_s"])
        transitions = [float(s["start"]) for s in meta["timeline"][1:]]
        emphases = [float(x) for x in meta.get("emphases", [])]
        palette = meta.get("audio_palette") or "ambient"
        if foley_style is None:
            foley_style = meta.get("foley_style")
    else:
        if args.total is None:
            raise SystemExit("Provide --total or --bv-meta")
        total = float(args.total)
        transitions = parse_floats(args.transitions)
        emphases = parse_floats(args.emphases)
        palette = args.palette

    if palette not in PALETTES:
        print(f"Unknown palette {palette!r}, falling back to ambient")
        palette = "ambient"

    if args.foley_only:
        audio = build_foley_track(total, transitions, emphases,
                                  style=(foley_style or "whoosh_thud"),
                                  seed_base=seed_base)
    else:
        audio = build_track(palette, total, transitions, emphases)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out), SR, (audio * 32767).astype(np.int16))
    kind = "foley stem" if args.foley_only else f"palette={palette}"
    print(f"wrote {out}, {audio.shape[0]/SR:.2f}s, {kind}")


if __name__ == "__main__":
    main()
