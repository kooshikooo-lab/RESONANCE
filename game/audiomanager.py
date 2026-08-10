# RESONANCE - audio playback manager
# Converts synthesized numpy buffers into pygame Sounds and plays them.

import pygame
import numpy as np

from . import config
from .audio import SR


def _to_sound(wav):
    """float32 mono [-1,1] -> pygame.Sound (16-bit stereo)."""
    wav = np.asarray(wav, dtype=np.float32)
    if wav.ndim == 1:
        wav = wav.reshape(-1, 1)
    # to int16 stereo
    left = (wav[:, 0] * 32767).clip(-32768, 32767).astype(np.int16)
    right = (wav[:, 0] * 32767).clip(-32768, 32767).astype(np.int16)
    inter = np.empty((len(left), 2), dtype=np.int16)
    inter[:, 0] = left
    inter[:, 1] = right
    s = pygame.sndarray.make_sound(inter)
    s.set_volume(config.MASTER_VOLUME)
    return s


class AudioManager:
    def __init__(self):
        self.channels = {
            "music": pygame.mixer.Channel(0),
            "voice": pygame.mixer.Channel(1),
            "sfx": pygame.mixer.Channel(2),
            "mic": pygame.mixer.Channel(3),
        }
        self.playing_voice = None

    def play_voice(self, wav, volume=None):
        """Play an alien voice phrase on the voice channel."""
        s = _to_sound(wav)
        if volume is not None:
            s.set_volume(config.MASTER_VOLUME * volume)
        self.channels["voice"].play(s)
        self.playing_voice = s
        return s

    def play_sfx(self, wav, volume=None):
        s = _to_sound(wav)
        if volume is not None:
            s.set_volume(config.MASTER_VOLUME * volume)
        self.channels["sfx"].play(s)
        return s

    def play_music(self, wav, volume=None):
        s = _to_sound(wav)
        v = config.MUSIC_VOLUME if volume is None else volume
        s.set_volume(config.MASTER_VOLUME * v)
        self.channels["music"].play(s)
        return s

    def voice_busy(self):
        return self.channels["voice"].get_busy()

    def stop_voice(self):
        self.channels["voice"].stop()

    def stop_music(self):
        self.channels["music"].stop()

    def stop_all(self):
        for ch in self.channels.values():
            ch.stop()
