# Quick self-check: render each voice, check validity, dump stats.
# Run: python -m game.check_audio
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.audio import SERAVAK, ILYAN, THRAEL, PULSE, Soundtrack, ui_accept, ui_decline, star_pulse
from game.pitch import midi_to_hz

def check(name, wav):
    wav = np.asarray(wav, dtype=np.float32)
    peak = float(np.max(np.abs(wav))) if len(wav) else 0.0
    rms = float(np.sqrt(np.mean(wav**2))) if len(wav) else 0.0
    n_nan = int(np.isnan(wav).sum()) if len(wav) else 0
    ok = len(wav) > 0 and peak > 0.01 and n_nan == 0
    print(f"{name:12s} dur={len(wav)/44100:5.2f}s peak={peak:6.3f} rms={rms:5.3f} nan={n_nan} {'OK' if ok else 'FAIL'}")
    return ok

# A little phrase: C4 E4 G4 (the greeting shape)
notes = [(midi_to_hz(60), 0.45, 0.02), (midi_to_hz(64), 0.45, 0.02), (midi_to_hz(67), 0.6, 0.0)]

all_ok = True
for voice, name in ((SERAVAK, "seravak"), (ILYAN, "ilyan"), (THRAEL, "thrael"), (PULSE, "pulse")):
    all_ok &= check(name, voice.render_phrase(notes))

all_ok &= check("soundtrack", Soundtrack().render(4.0))
all_ok &= check("ui_accept", ui_accept())
all_ok &= check("ui_decline", ui_decline())
all_ok &= check("star_pulse", star_pulse())

print("\nRESULT:", "ALL OK" if all_ok else "PROBLEMS FOUND")
sys.exit(0 if all_ok else 1)
