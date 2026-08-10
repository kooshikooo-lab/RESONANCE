# RESONANCE - procedural audio engine
# Every alien voice, the soundtrack, and the SFX are synthesized from the same
# harmonic language the Havari sing. No asset files.

import numpy as np
import math
import random

from . import config

SR = config.SAMPLE_RATE


# ---------------------------------------------------------------- synthesis primitives

def _t(length, sr=SR):
    return np.linspace(0.0, length, int(length * sr), endpoint=False, dtype=np.float32)


def sine(freq, length, sr=SR):
    t = _t(length, sr)
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def adsr(n, a=0.05, r=0.25):
    """Attack / decay / sustain / release envelope over n samples."""
    env = np.ones(n, dtype=np.float32)
    a_n = max(1, int(a * SR))
    r_n = max(1, int(r * SR))
    if a_n < n:
        env[:a_n] = np.linspace(0, 1, a_n)
    if r_n < n:
        env[-r_n:] *= np.linspace(1, 0, r_n)
    return env


def normalize(x, peak=0.9):
    m = np.max(np.abs(x)) if len(x) else 1.0
    if m < 1e-6:
        return x
    return (x / m * peak).astype(np.float32)


# ---------------------------------------------------------------- alien voices

class Voice:
    """A synthesized alien voice: timbre profile + phrase renderer."""

    def __init__(self, name, base_ratio=1.0, partials=((1, 1.0),), am_rate=3.0, am_depth=0.2,
                 detune=0.0, noise=0.0, reverb=0.0, attack=0.06, release=0.2, vibrato=4.5, vib_depth=0.006):
        self.name = name
        self.base_ratio = base_ratio        # transposition relative to written pitch
        self.partials = partials            # list of (multiplier, amplitude)
        self.am_rate = am_rate              # amplitude-modulation rate (mantle pulse)
        self.am_depth = am_depth
        self.detune = detune                # cents of systemic detune (Thrael's "perfect lie")
        self.noise = noise
        self.reverb = reverb
        self.attack = attack
        self.release = release
        self.vibrato = vibrato
        self.vib_depth = vib_depth
        self._rng = np.random.default_rng(hash(name) & 0xFFFFFFFF)

    def _partials_wave(self, freq, length):
        t = _t(length)
        w = np.zeros_like(t, dtype=np.float32)
        for mult, amp in self.partials:
            w += amp * np.sin(2 * np.pi * freq * mult * t)
        return w

    def render_note(self, freq, length):
        """Render a single note with the alien's timbre."""
        freq *= self.base_ratio
        # apply the systemic detune (Thrael's lie)
        freq *= 2.0 ** (self.detune / 1200.0)
        n = int(length * SR)
        w = self._partials_wave(freq, length)
        # vibrato on the fundamental + partials
        t = _t(length)
        vib = 1.0 + self.vib_depth * np.sin(2 * np.pi * self.vibrato * t)
        # rebuild with vibrato by phase modulation
        phase = 2 * np.pi * freq * np.cumsum(vib) / SR
        w = np.zeros(n, dtype=np.float32)
        for mult, amp in self.partials:
            w += amp * np.sin(phase * mult)
        # amplitude modulation - the body pulse
        am = 1.0 + self.am_depth * np.sin(2 * np.pi * self.am_rate * t)
        w *= am
        env = adsr(n, self.attack, self.release)
        w *= env
        if self.noise > 0:
            w += (self._rng.random(n).astype(np.float32) * 2.0 - 1.0) * self.noise * env
        return w.astype(np.float32)

    def render_phrase(self, notes):
        """notes: list of (freq, dur, [gap]). Returns a single waveform."""
        parts = []
        for item in notes:
            freq, dur = item[0], item[1]
            gap = item[2] if len(item) > 2 else 0.0
            w = self.render_note(freq, dur)
            parts.append(w)
            if gap > 0:
                parts.append(np.zeros(int(gap * SR), dtype=np.float32))
        if not parts:
            return np.zeros(int(1 * SR), dtype=np.float32)
        out = np.concatenate(parts)
        # light synthetic reverb (comb)
        if self.reverb > 0:
            d = int(0.19 * SR)
            wet = np.zeros_like(out)
            wet[d:] = out[:-d]
            out = out * (1 - self.reverb) + wet * self.reverb
        return normalize(out)


# ---- the four voices, tuned to the design bible

SERAVAK = Voice(
    "seravak", base_ratio=0.5,
    partials=((1, 1.0), (1.5, 0.6), (2.0, 0.4), (2.5, 0.35), (3.0, 0.18)),
    am_rate=2.2, am_depth=0.30, noise=0.012,
    attack=0.10, release=0.32, vibrato=3.2, vib_depth=0.004,
)
ILYAN = Voice(
    "ilyan", base_ratio=1.0,
    partials=((1, 1.0), (2.0, 0.55), (3.0, 0.30), (4.0, 0.12)),
    am_rate=5.5, am_depth=0.18, noise=0.02, detune=6.0,   # slightly sharp, young
    attack=0.03, release=0.12, vibrato=6.0, vib_depth=0.010,
)
THRAEL = Voice(
    "thrael", base_ratio=0.75,
    partials=((1, 1.0), (2.0, 0.7), (3.0, 0.5), (4.0, 0.35), (5.0, 0.2)),
    am_rate=1.2, am_depth=0.10, noise=0.005, detune=-14.0,  # THE PERFECT LIE
    attack=0.04, release=0.18, vibrato=2.0, vib_depth=0.002,
)
PULSE = Voice(
    "pulse", base_ratio=0.3,
    partials=((1, 1.0), (1.05, 0.4), (1.5, 0.25), (2.0, 0.1)),
    am_rate=0.35, am_depth=0.55, noise=0.02, reverb=0.5,
    attack=0.4, release=0.8, vibrato=0.5, vib_depth=0.012,
)

VOICES = {"seravak": SERAVAK, "ilyan": ILYAN, "thrael": THRAEL, "pulse": PULSE}


def get_voice(name):
    return VOICES.get(name, SERAVAK)


# ---------------------------------------------------------------- soundtrack

class Soundtrack:
    """A slowly-evolving ambient bed built from the same chords the Havari sing.

    The star's 'pulse' is the heartbeat; the choir pads are its children. As trust
    rises, the chord opens up (darker root -> brighter), and a counter-melody joins.
    """

    CHORDS = {
        # (root_freq, chord_ratios)  - just intonation, no equal-temperment grit
        "grief":   (110.0, (1.0, 1.5, 2.0)),          # Am  (sad, resolved)
        "unease":  (110.0, (1.0, 1.4, 1.9)),          # dim-ish, anxious
        "hope":    (146.8, (1.0, 1.25, 1.5)),         # D   (open, bright-ish)
        "dawn":    (174.6, (1.0, 1.25, 1.5, 2.0)),    # F   (full, warm)
        "choir":   (196.0, (1.0, 1.2, 1.5, 1.8)),     # G add9-ish, the communion
    }

    def __init__(self):
        self.mood = "grief"
        self._phase = 0.0

    def render(self, length):
        """Render `length` seconds of ambient bed. Returns float32 mono array."""
        chord = self.CHORDS.get(self.mood, self.CHORDS["grief"])
        root, ratios = chord
        n = int(length * SR)
        t = _t(length)
        out = np.zeros(n, dtype=np.float32)
        # pulse (the star's heartbeat) - slow AM sine at the root's sub-octave
        pulse_freq = root / 2.0
        pulse = np.sin(2 * np.pi * pulse_freq * t + self._phase)
        pulse_env = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)  # slow swell
        out += 0.22 * pulse * pulse_env
        # choir pads
        for ratio, amp in zip(ratios, np.linspace(0.12, 0.30, len(ratios))):
            f = root * ratio
            # very slow beating between slightly detuned partials = "breathing"
            for d in (0, 0.004):
                out += amp * np.sin(2 * np.pi * f * (1 + d) * t)
        # gentle high shimmer (stars)
        out += 0.03 * np.sin(2 * np.pi * (root * 4.0) * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t))
        # sub rolloff via simple one-pole
        out = np.convolve(out, np.ones(16) / 16, mode="same")
        self._phase = (self._phase + 2 * np.pi * pulse_freq * length) % (2 * np.pi)
        return normalize(out, peak=0.5)


# ---------------------------------------------------------------- UI sound effects

def ui_blip(freq=660.0, length=0.06):
    w = sine(freq, length)
    return normalize(w * adsr(len(w), 0.005, 0.08), 0.5)


def ui_accept():
    a = sine(523.25, 0.09)
    b = sine(659.25, 0.14)
    out = np.concatenate([a, np.zeros(int(0.02 * SR)), b])
    return normalize(out, 0.55)


def ui_decline():
    a = sine(440.0, 0.08)
    b = sine(415.3, 0.16)
    out = np.concatenate([a, np.zeros(int(0.02 * SR)), b])
    return normalize(out, 0.45)


def ui_harmony(notes=((523.25, 0.3), (659.25, 0.3), (783.99, 0.5))):
    """A little major arpeggio played when the player's echo matches."""
    parts = []
    for f, d in notes:
        parts.append(sine(f, d))
    return normalize(np.concatenate(parts), 0.6)


def ui_dissonance():
    """The sound of being heard wrongly - a deliberately ugly interval."""
    a = sine(440.0, 0.25)
    b = sine(587.33 * 0.97, 0.25)   # a hair flat = audible pain
    out = a + b
    return normalize(out, 0.4)


def star_pulse(freq=220.0, length=1.2):
    """The star's slow answering pulse - used at key story moments."""
    t = _t(length)
    env = np.exp(-3.0 * t)
    w = np.sin(2 * np.pi * freq * t) * env
    w += 0.4 * np.sin(2 * np.pi * freq * 1.5 * t) * env
    return normalize(w, 0.7)
