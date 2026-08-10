# RESONANCE - microphone recording via sounddevice

import numpy as np
import sounddevice as sd

from . import config


class MicRecorder:
    def __init__(self, sr=config.SAMPLE_RATE):
        self.sr = sr
        self._device = None
        self._list_inputs()

    def _list_inputs(self):
        try:
            devs = sd.query_devices()
            inputs = [i for i, d in enumerate(devs) if d["max_input_channels"] > 0]
            # prefer the default input
            try:
                self._device = sd.default.device[0]
            except Exception:
                self._device = inputs[0] if inputs else None
        except Exception:
            self._device = None

    def available(self):
        return self._device is not None

    def list_inputs(self):
        devs = sd.query_devices()
        return [(i, d["name"]) for i, d in enumerate(devs) if d["max_input_channels"] > 0]

    def record(self, seconds, gain=2.0):
        """Record `seconds` of mono audio. Returns float32 array [-1,1] at self.sr."""
        if not self.available():
            return np.zeros(int(seconds * self.sr), dtype=np.float32)
        n = int(seconds * self.sr)
        try:
            raw = sd.rec(n, samplerate=self.sr, channels=1, dtype="float32", device=self._device)
            sd.wait()
            x = raw[:, 0]
        except Exception:
            return np.zeros(n, dtype=np.float32)
        # high-pass-ish: remove DC
        x = x - np.mean(x)
        x = x * gain
        # soft clip
        x = np.tanh(x * 1.2) / 1.2
        return x.astype(np.float32)

    def record_blocking(self, seconds, on_tick=None):
        """Record with a live level callback. Returns audio."""
        n = int(seconds * self.sr)
        if not self.available():
            return np.zeros(n, dtype=np.float32)
        frames = []
        stream = sd.InputStream(
            samplerate=self.sr, channels=1, dtype="float32", device=self._device,
            blocksize=1024,
        )
        with stream:
            total_blocks = int(seconds * self.sr / 1024)
            for b in range(total_blocks):
                data, _ = stream.read(1024)
                frames.append(data[:, 0])
                if on_tick:
                    level = float(np.sqrt(np.mean(data[:, 0] ** 2))) if len(data) else 0.0
                    on_tick(level, (b + 1) / total_blocks)
        x = np.concatenate(frames) if frames else np.zeros(n, dtype=np.float32)
        x = x - np.mean(x)
        x = np.tanh(x * 1.2 * 2.0) / 1.2
        return x.astype(np.float32)
