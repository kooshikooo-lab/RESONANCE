# RESONANCE

A first-contact game about singing.

You are the Speaker, a linguist aboard the *Aria*, and you have just made contact with
the **Havari** — a civilization that evolved around a dying pulsar and that has no
language except tone. Every word is a melody. Emotion is pitch contour. Memory is song.
To speak to them, you must **sing.**

## The core idea

> **Imperfection is the source of meaning.**

The Havari are the most perfect singers in the galaxy — and that perfection is slowly
killing their star. Your broken, human, feeling-soaked voice turns out to be the only
one that can save them.

## How you play

You don't learn alien phonemes. You learn a **musical grammar**:

- **The Echo** — an NPC sings a phrase; you sing it back. The game analyzes your voice
  (via RMVPE pitch detection) and scores fidelity. Trust is accuracy.
- **The Dialogue** — an NPC sings a *form* (question, statement, challenge); you respond
  with the *right* learned phrase, judged on grammar, not rote. Trust is understanding.

Because a Havari cannot lie, the game quietly measures the **NPC's** fidelity to its own
canonical phrase. Thrael, the negotiator, is always sung 14 cents flat. The lie-detection
mechanic is the heart of the game — the player can *hear* a wound before any character
admits it.

## Characters

- **Seravak** — the Teacher. Not a Yoda. A connoisseur of imperfection who loves you for
  your flaws.
- **Ilyan** — the Young. A revolutionary who refuses to grow in tune. The child is the
  bravest being in the game.
- **Thrael** — the Negotiator. Afraid of hope, not of you. Her weapon is ritualized,
  heartbreaking faith.
- **The Pulse** — the Star. A symbiote, lonely as a mountain, starving for a voice that
  disagrees with it.
- **Commander Voss** — the human anchor. The one who must learn to hear again.

## Design references

The alien-meets-human side is guided by the craft of **Ursula K. Le Guin** (translation
as a moral act; the alien is a full person) and **Becky Chambers** (depth lives in the
small, patient, everyday; no evil, only mismatched needs). See `DESIGN*.md`.

## Status

Design bible complete. Engine complete. **Both mini-games are playable end-to-end** across
all six movements: The Echo (fidelity -> trust), The Dialogue (grammar-graded responses,
mirror-echoing is a social error), the Movement VI duet, and three endings resolved by
trust + skill. Lie-detection reveal and Commander Voss's arc are wired in.

## Controls

- `ENTER` / `SPACE` — advance (approach, listen, answer, continue)
- `R` — replay the phrase or Form during LISTEN
- `H` — toggle the phrase note-name hint
- `ESC` — quit

## Tech

- Python 3.12, pygame-ce, numpy, rmvpe-onnx, sounddevice
- All audio (alien voices, soundtrack, SFX) is procedurally synthesized — no asset files
- Pitch detection: RMVPE (Apache-2.0) via `rmvpe-onnx`

## Run

```bash
pip install pygame-ce sounddevice numpy
pip install "rmvpe-onnx[cli]"
python main.py
```
