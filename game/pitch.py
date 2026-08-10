# RESONANCE - pitch analysis
# Wraps rmvpe-onnx (Apache-2.0) to turn mic audio into a note/pitch contour,
# then scores the player's Echo and Dialogue attempts.
#
# The scoring engine is intentionally double-edged:
#   * For the PLAYER, it measures fidelity (Echo) and understanding (Dialogue).
#   * For the NPCs, it quietly measures THEIR fidelity to their own canonical phrase,
#     which is the game's lie-detection mechanic (see DESIGN.md Part 3).

import numpy as np
import math
import csv
import io
import statistics
import tempfile
import os

from . import config
from .audio import SR

# lazy import so the game can run without the model present (e.g. during dev)
_rmvpe = None


def _get_rmvpe():
    global _rmvpe
    if _rmvpe is None:
        from rmvpe_onnx import RMVPE
        _rmvpe = RMVPE()
    return _rmvpe


def hz_to_midi(f):
    if f <= 0:
        return None
    return 69 + 12 * math.log2(f / config.A4)


def midi_to_hz(m):
    return config.A4 * (2.0 ** ((m - 69) / 12.0))


def cents(f1, f2):
    if f1 <= 0 or f2 <= 0:
        return float("inf")
    return 1200.0 * math.log2(f2 / f1)


# ---------------------------------------------------------------- recording -> contour

def analyze_audio(audio, sr):
    """audio: float32 mono 1-D array. Returns list of (time_s, freq_hz, confidence)."""
    rmvpe = _get_rmvpe()
    if rmvpe is None:
        return []
    times, freqs, confs, _act = rmvpe.predict(audio=audio, sr=sr)
    return list(zip(times, freqs, confs))


# ---------------------------------------------------------------- contour -> notes

def contour_to_notes(frames, conf_threshold=None):
    """Segment a pitch contour into stable notes.

    frames: list of (time, freq, conf)
    Returns list of (midi, start_t, end_t, mean_freq, mean_conf) for voiced segments
    that are at least MIN_NOTE_SECONDS long and within the playable range.
    """
    if conf_threshold is None:
        conf_threshold = config.CONFIDENCE_THRESHOLD
    segments = []
    cur = []
    last_f = None
    for t, f, c in frames:
        voiced = (f > config.MIN_NOTE_HZ and f < config.MAX_NOTE_HZ and c >= conf_threshold)
        if voiced:
            # allow a small vibrato tolerance so we don't split a sung note
            if last_f is not None and cur and abs(cents(last_f, f)) > 90:
                _seal_segment(segments, cur)
                cur = []
            cur.append((t, f, c))
            last_f = f
        else:
            if cur:
                _seal_segment(segments, cur)
                cur = []
            last_f = None
    if cur:
        _seal_segment(segments, cur)
    # merge adjacent segments that are within ~1 semitone (portamento/scoop)
    merged = []
    for seg in segments:
        if merged and abs(seg[0] - merged[-1][0]) <= 1.0:
            pm, ps, pe, pf, pc = merged[-1]
            merged[-1] = (pm, ps, seg[2], pf, max(pc, seg[4]))
        else:
            merged.append(seg)
    return merged


def _seal_segment(segments, cur):
    if not cur:
        return
    start, end = cur[0][0], cur[-1][0]
    if (end - start) < config.MIN_NOTE_SECONDS:
        return
    freqs = [f for _, f, _ in cur]
    confs = [c for _, _, c in cur]
    mid = median_midi(freqs)
    if mid is None:
        return
    mean_f = statistics.mean(freqs)
    segments.append((round(mid, 2), start, end, mean_f, statistics.mean(confs)))


def median_midi(freqs):
    med = statistics.median(freqs)
    m = hz_to_midi(med)
    return m if m is not None else None


def notes_to_phrase(notes):
    """Turn a list of note segments into a display-friendly phrase string."""
    if not notes:
        return "· · ·"
    return " ".join(config.hz_to_note_name(seg[3]) for seg in notes)


# ---------------------------------------------------------------- scoring

class EchoResult:
    def __init__(self):
        self.detected_notes = []
        self.expected_notes = []
        self.per_note = []          # list of (target_midi, sung_midi, cents_off, score)
        self.fidelity = 0.0         # 0..1 overall fidelity
        self.matched = 0
        self.total = 0
        self.perfect = 0
        self.summary = ""


def score_echo(expected, detected):
    """Score an Echo attempt.

    expected: list of (midi, dur_seconds) - the phrase the NPC sang
    detected: list of note segments from the player's voice
    """
    res = EchoResult()
    res.expected_notes = expected
    res.detected_notes = detected

    target_midis = [e[0] for e in expected]
    sung_midis = [d[0] for d in detected]
    res.total = len(target_midis)
    res.matched = 0
    res.perfect = 0

    # align greedily: each target tries the nearest remaining sung note (in time order)
    sung_idx = 0
    for t_idx, (tm, _dur) in enumerate(expected):
        best = None
        best_c = float("inf")
        for s_idx in range(sung_idx, len(detected)):
            sm = detected[s_idx][0]
            c = abs(cents(midi_to_hz(tm), midi_to_hz(sm)))
            if c < best_c:
                best_c = c
                best = (s_idx, sm)
        if best is None:
            res.per_note.append((tm, None, None, 0.0))
            continue
        s_idx, sm = best
        sung_idx = s_idx + 1
        res.per_note.append((tm, sm, best_c, 0.0))

    # score each aligned note
    score_sum = 0.0
    for i, (tm, sm, c, _) in enumerate(res.per_note):
        if sm is None:
            res.per_note[i] = (tm, sm, c, 0.0)
            continue
        res.matched += 1
        if c <= config.PERFECT_TOLERANCE_CENTS:
            s = 1.0
            res.perfect += 1
        elif c <= config.NOTE_MATCH_TOLERANCE_CENTS:
            s = 0.75
        elif c <= config.CLOSE_TOLERANCE_CENTS:
            s = 0.35
        else:
            s = 0.0
        res.per_note[i] = (tm, sm, c, s)
        score_sum += s

    if res.total:
        res.fidelity = score_sum / res.total
    # bonus for getting the phrase length about right
    len_ratio = min(1.0, len(sung_midis) / max(1, res.total))
    res.fidelity = min(1.0, res.fidelity * (0.85 + 0.15 * len_ratio))

    if res.fidelity >= 0.85:
        res.summary = "perfect"
    elif res.fidelity >= 0.6:
        res.summary = "good"
    elif res.fidelity >= 0.35:
        res.summary = "weak"
    else:
        res.summary = "lost"
    return res


# ---------------------------------------------------------------- dialogue: phrase matching

def match_phrase(detected, candidates):
    """Find which learned phrase the player sang, by pitch-contour similarity.

    detected: list of note segments from the player's voice
    candidates: dict of phrase_id -> PHRASES entry (with "notes": [(midi, dur), ...])
    Returns (best_phrase_id or None, best_fidelity, per_id_scores).
    """
    best_id = None
    best_fid = 0.0
    per_id = {}
    n_sung = len(detected)
    for pid, pdata in candidates.items():
        fid = 0.0
        notes = pdata.get("notes")
        if notes and detected:
            fid = score_echo(notes, detected).fidelity
            # phrase identity: singing a 6-note phrase should not be scored as a
            # perfect 4-note prefix match - penalize length mismatch
            n_exp = len(notes)
            if n_sung and n_exp:
                len_sim = min(n_sung, n_exp) / max(n_sung, n_exp)
                fid *= 0.5 + 0.5 * len_sim
        per_id[pid] = fid
        if fid > best_fid:
            best_fid = fid
            best_id = pid
    return best_id, best_fid, per_id


class DialogueResult:
    def __init__(self):
        self.chosen_id = None           # the learned phrase the player sang (best match)
        self.expected_id = None         # the canonical correct response
        self.fidelity = 0.0             # how well they sang the chosen phrase
        self.grammar_fit = 0.0          # 0..1 - does the chosen form answer the Form
        self.overall = 0.0              # combined score 0..1
        self.mirror = False             # they echoed the question back instead of answering
        self.summary = ""               # "understood" | "misread" | "lost"


def grammar_fit(question_form, response_form):
    """Havari grammar: judge whether a response's Form answers the NPC's Form.
    1.0 = correct response; ~0 = you sang the question back (a mirror)."""
    if response_form == "refusal":
        # a refusal answers a challenge/refusal, but never a plain question well
        return 0.6 if question_form in ("refusal", "challenge") else 0.3
    if question_form == "question":
        # a question must be answered, not re-echoed
        if response_form == "statement":
            return 1.0
        if response_form == "request":
            return 0.7
        return 0.2  # mirror - a question echoed back
    if question_form == "request":
        if response_form == "statement":
            return 1.0
        return 0.4
    if question_form in ("refusal", "challenge"):
        if response_form == "statement":
            return 0.8
        return 0.4
    # statement -> statement (agreeing, completing) or anything gentle
    return 0.9 if response_form == "statement" else 0.5


def score_dialogue(question_form, response_form, chosen_id, expected_id, fidelity,
                   question_id=None):
    """Grade a Dialogue attempt. Returns a DialogueResult.

    fidelity is how accurately the player sang whichever phrase they chose.
    The grammar relationship between the NPC's Form and the player's chosen
    phrase is the heart of the mechanic: answering beats echoing.
    """
    res = DialogueResult()
    res.chosen_id = chosen_id
    res.expected_id = expected_id
    res.fidelity = fidelity
    res.grammar_fit = grammar_fit(question_form, response_form)
    # a mirror = you echoed their exact phrase back (a question re-echoed, or
    # the accusation re-sung). The Havari forgive bad echo; they do not forgive
    # being thrown back at themselves.
    res.mirror = (chosen_id is not None and chosen_id == question_id)
    # overall: singing the RIGHT KIND of answer matters most; accuracy second
    res.overall = res.grammar_fit * (0.6 + 0.4 * fidelity)
    if res.mirror:
        # echoing their Form is a specific social error, always worse
        res.overall = min(res.overall, 0.15)
        res.summary = "lost"
    elif res.overall >= 0.7:
        res.summary = "understood"
    elif res.overall >= 0.35:
        res.summary = "misread"
    else:
        res.summary = "lost"
    return res


# ---------------------------------------------------------------- lie detection

def measure_npc_fidelity(phrase_midis, detune_cents):
    """For story use: measure how far an NPC's sung phrase deviates from its canonical
    tuning. Thrael's phrases carry a negative detune - the game 'hears' the grief.
    Returns cents of mean deviation (negative = sung flat)."""
    if detune_cents == 0:
        return 0.0
    return float(detune_cents)


# ---------------------------------------------------------------- phrase library

def phrase_to_midis(freqs_and_durs):
    """[(freq, dur), ...] -> [(midi, dur), ...]"""
    return [(round(hz_to_midi(f), 2), d) for f, d in freqs_and_durs]
