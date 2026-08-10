# RESONANCE - game configuration and constants

import os

GAME_TITLE = "RESONANCE"
VERSION = "0.1.0"

# Window
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Audio
SAMPLE_RATE = 44100
MASTER_VOLUME = 0.8
MUSIC_VOLUME = 0.35
VOICE_VOLUME = 0.9

# Pitch detection / scoring
A4 = 440.0
CONFIDENCE_THRESHOLD = 0.03
NOTE_MATCH_TOLERANCE_CENTS = 45     # within 45 cents of target = "in tune"
CLOSE_TOLERANCE_CENTS = 120         # within 120 cents = partial credit
PERFECT_TOLERANCE_CENTS = 12        # within 12 cents = perfect

# Phrase / recording
DEFAULT_RECORD_SECONDS = 4.0
MIN_NOTE_SECONDS = 0.18             # minimum sustained pitch for a note segment
MAX_NOTE_HZ = 1500.0
MIN_NOTE_HZ = 60.0

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

# Color palette (deep space, aurora)
COLOR_BG_TOP = (10, 6, 28)
COLOR_BG_BOTTOM = (28, 12, 48)
COLOR_STAR_DIM = (160, 180, 255)
COLOR_PULSE = (120, 220, 255)
COLOR_ALIEN_A = (140, 240, 190)     # Seravak - sage
COLOR_ALIEN_B = (255, 180, 90)      # Ilyan - gold
COLOR_ALIEN_C = (190, 120, 255)     # Thrael - violet
COLOR_ALIEN_D = (110, 200, 255)     # The Pulse - deep blue
COLOR_PLAYER = (255, 255, 255)
COLOR_UI = (220, 230, 255)
COLOR_UI_DIM = (130, 140, 180)
COLOR_GOOD = (120, 255, 170)
COLOR_BAD = (255, 110, 120)
COLOR_GOLD = (255, 210, 120)

# Trust / mood bounds
TRUST_MAX = 100.0

def cents_between(f1, f2):
    """Cents difference between two frequencies (signed)."""
    import math
    return 1200.0 * math.log2(f2 / f1) if f1 > 0 and f2 > 0 else float("inf")

def hz_to_note_name(f):
    """Convert a frequency to an approximate note name + cents deviation."""
    import math
    if f <= 0:
        return "---"
    midi = 69 + 12 * math.log2(f / A4)
    note_idx = int(round(midi)) % 12
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = int(round(midi)) // 12 - 1
    return f"{names[note_idx]}{octave}"
