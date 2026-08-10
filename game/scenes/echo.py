# RESONANCE - the Echo mini-game (Mini-game 1)
#
# Loop: INTRO card -> LISTEN (alien sings) -> RECORD (you sing) -> ANALYZE ->
#       RESULT (score + reaction) -> next round / next movement.
#
# The NPC's phrase is rendered with their voice; the player records; RMVPE analyzes;
# the player's contour is compared note-by-note. Fidelity -> trust -> story.

import pygame
import numpy as np
import threading
import time

from .. import config
from ..app import Scene
from ..audio import get_voice, ui_accept, ui_decline, ui_dissonance
from ..graphics import (
    Background, AlienForm, Ribbon, ParticleField, draw_text, wrap_text, draw_glow,
)
from .. import pitch
from .. import story

RECORD_SECONDS = 5.0


class EchoScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.bg = Background(config.WIDTH, config.HEIGHT)
        self.particles = ParticleField(config.WIDTH, config.HEIGHT, 50)
        self.ribbon = Ribbon(140, 320, config.WIDTH - 280, 220)
        self.state_phase = "intro"      # intro | listen | record | analyze | result | round_end
        self.phase_timer = 0.0
        self.beat = None
        self.phrase_data = None
        self.phrase_midis = []
        self.voice = None
        self.alien = None
        self.audio_capture = None
        self.analysis = None
        self.result = None
        self.record_level = 0.0
        self.record_progress = 0.0
        self.silence_frames = []
        self._thread = None
        self.show_hint = False
        self.hint_timer = 0.0
        self.round_number = 0

    # ---------------------------------------------------------------- lifecycle
    def on_enter(self):
        self._load_beat()

    def _load_beat(self):
        beat = self.app.state.current_beat()
        if beat is None:
            self.app.fade_to("ending")
            return
        self.beat = beat
        self.state_phase = "intro"
        self.phase_timer = 0.0
        self.audio_capture = None
        self.analysis = None
        self.result = None
        self.record_level = 0.0
        self.record_progress = 0.0
        self.show_hint = False

        # build the alien form for this beat's speaker
        who = beat.get("who", "seravak")
        cdata = story.CHARACTERS[who]
        self.alien = AlienForm(who, 220, 420, 170, 140)
        self.voice = get_voice(cdata["voice"])

        # phrase setup
        phrase_id = beat.get("phrase")
        if phrase_id:
            pdata = story.PHRASES[phrase_id]
            self.phrase_data = pdata
            self.phrase_midis = [n[0] for n in pdata["notes"]]
            self.learned_ok = False
        else:
            self.phrase_data = None
            self.phrase_midis = []
        # set soundtrack mood by character
        mood = "grief"
        if who == "ilyan":
            mood = "hope"
        elif who == "thrael":
            mood = "unease"
        elif who == "pulse":
            mood = "dawn"
        self.app.soundtrack.mood = mood

    # ---------------------------------------------------------------- phases
    def _advance(self):
        if self.state_phase == "intro":
            self.state_phase = "listen"
            self.phase_timer = 0.0
            self._play_phrase()
        elif self.state_phase == "listen":
            self.state_phase = "record"
            self.phase_timer = 0.0
            self._start_record()
        elif self.state_phase == "record":
            # record completed (thread sets audio_capture)
            pass
        elif self.state_phase == "analyze":
            self.state_phase = "result"
            self.phase_timer = 0.0
        elif self.state_phase == "result":
            self._next_round()

    def _next_round(self):
        # record trust changes, then return to the observation deck to choose the next approach
        self.app.state.advance_beat()
        self.round_number += 1
        self.app.fade_to("hub")

    # ---------------------------------------------------------------- recording / analysis
    def _start_record(self):
        seconds = RECORD_SECONDS

        def worker():
            try:
                audio = self.app.mic.record_blocking(
                    seconds,
                    on_tick=lambda lvl, prog: (setattr(self, "record_level", lvl),
                                               setattr(self, "record_progress", prog)),
                )
            except Exception:
                audio = np.zeros(int(seconds * config.SAMPLE_RATE), dtype=np.float32)
            self.audio_capture = audio
            # analyze in a thread too (RMVPE loads model first time)
            self._thread = threading.Thread(target=self._analyze, daemon=True)
            self._thread.start()

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def _analyze(self):
        audio = self.audio_capture
        if audio is None or len(audio) == 0:
            self.analysis = []
            self.state_phase = "analyze"
            return
        # light envelope: keep the loudest window (avoid dead lead-in)
        try:
            frames = pitch.analyze_audio(audio, config.SAMPLE_RATE)
        except Exception as e:
            print("analysis error:", e)
            frames = []
        self.analysis = frames
        self.state_phase = "analyze"

    def _compute_result(self):
        if self.beat is None:
            return
        detected = pitch.contour_to_notes(self.analysis or [])
        expected = [n for n in self.phrase_data["notes"]] if self.phrase_data else []
        if self.beat.get("kind") == "silence":
            # Movement IV: no phrase to echo - the player just needs to stay.
            # If they stayed silent-ish or hummed something, trust grows either way.
            self.result = None
            self.app.state.add_trust(self.beat["who"], 12)
            self.app.state.record_attempt(0.5)
            return
        res = pitch.score_echo(expected, detected)
        self.result = res
        # trust change by fidelity
        fid = res.fidelity
        self.app.state.record_attempt(fid)
        who = self.beat["who"]
        gain = 0.0
        if fid >= 0.85:
            gain = 22
            self.app.audio.play_sfx(ui_accept())
        elif fid >= 0.6:
            gain = 12
            self.app.audio.play_sfx(ui_accept())
        elif fid >= 0.35:
            gain = 2
            self.app.audio.play_sfx(ui_decline())
        else:
            gain = -4
            self.app.audio.play_sfx(ui_dissonance())
        self.app.state.add_trust(who, gain)
        # learn the phrase (Echo demonstrates you can reproduce it)
        if self.phrase_data and fid >= 0.5:
            phrase_id = self.beat.get("phrase")
            if phrase_id:
                self.app.state.learn(phrase_id)

    # ---------------------------------------------------------------- input
    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.state_phase == "intro":
                    self._advance()
                elif self.state_phase == "result":
                    self._advance()
            if event.key == pygame.K_h:
                self.show_hint = not self.show_hint

    # ---------------------------------------------------------------- update
    def update(self, dt):
        self.bg.update()
        if self.alien:
            self.alien.update(dt, intensity=0.8)
        self.phase_timer += dt

        # if recording finished, advance
        if self.state_phase == "record" and self._thread is not None and not self._thread.is_alive():
            self._thread = None
            self.state_phase = "analyze"

        if self.state_phase == "analyze" and self.analysis is not None:
            # analysis done (RMVPE returned) - only when thread fully finished
            if self._thread is None:
                self._compute_result()
                self.state_phase = "result"
                self.phase_timer = 0.0

    # ---------------------------------------------------------------- draw
    def draw(self):
        self.bg.draw(self.screen, pulse_energy=0.6 + 0.2 * self.app.state.avg_fidelity)

        # draw drifting particles
        self.particles.draw(self.screen, dt=0.016)

        # header
        mv = self.app.state.current_movement()
        draw_text(self.screen, config.GAME_TITLE, 22, 20, 14, config.COLOR_UI_DIM)
        if mv:
            draw_text(self.screen, f"{mv['title']}", 22, config.WIDTH - 20, 14,
                      config.COLOR_UI_DIM, align="right")
        # trust bar
        self._draw_trust()

        # alien
        if self.alien:
            self.alien.draw(self.screen)

        # phase content
        if self.state_phase == "intro":
            self._draw_intro()
        elif self.state_phase == "listen":
            self._draw_listen()
        elif self.state_phase == "record":
            self._draw_record()
        elif self.state_phase == "analyze":
            self._draw_analyze()
        elif self.state_phase == "result":
            self._draw_result()

    def _draw_trust(self):
        # small per-character trust dots in the corner
        y = 40
        draw_text(self.screen, "TRUST", 16, 20, y, config.COLOR_UI_DIM)
        for cid, cdata in story.CHARACTERS.items():
            y += 22
            val = self.app.state.trust_of(cid)
            color = cdata["color"]
            pygame.draw.rect(self.screen, (60, 60, 80), (20, y, 90, 8))
            pygame.draw.rect(self.screen, color, (20, y, int(90 * val / 100), 8))
            draw_text(self.screen, cdata["name"], 16, 116, y - 5, config.COLOR_UI_DIM)

    def _draw_intro(self):
        beat = self.beat
        if not beat:
            return
        who = beat["who"]
        cdata = story.CHARACTERS[who]
        # dialogue box at bottom
        box = pygame.Rect(80, 500, config.WIDTH - 160, 160)
        pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
        pygame.draw.rect(self.screen, cdata["color"], box, 2, border_radius=12)
        # character name in their color
        draw_text(self.screen, cdata["name"], 30, box.x + 20, box.y + 10, cdata["color"])
        lines = wrap_text(beat["line"], 24, box.w - 40)
        yy = box.y + 48
        for ln in lines[:4]:
            draw_text(self.screen, ln, 24, box.x + 20, yy, config.COLOR_UI)
            yy += 30
        if self.phrase_data:
            # phrase meaning + ribbon preview
            draw_text(self.screen, f'"{self.phrase_data["meaning"]}"', 22,
                      box.x + 20, yy + 6, config.COLOR_UI_DIM)
        draw_text(self.screen, "press ENTER to listen", 26, config.WIDTH // 2,
                  config.HEIGHT - 30, config.COLOR_GOLD, align="center")
        # pulse hint for the movement
        self.hint_timer += 1 / 60.0
        if int(self.hint_timer * 2) % 2 == 0:
            draw_text(self.screen, "[H] hint", 16, box.x + 20, box.y + box.h - 26,
                      config.COLOR_UI_DIM)

    def _draw_listen(self):
        beat = self.beat
        if not beat:
            return
        cdata = story.CHARACTERS[beat["who"]]
        # ribbon showing the phrase (progressively revealed)
        dur = sum(n[1] for n in self.phrase_data["notes"]) if self.phrase_data else 1.0
        prog = min(1.0, self.phase_timer / dur)
        if self.phrase_data:
            self.ribbon.draw_phrase(self.screen, self.phrase_data["notes"],
                                    cdata["color"], progress=prog)
        draw_text(self.screen, "LISTEN", 34, config.WIDTH // 2, 200,
                  config.COLOR_UI, align="center")
        if self.phase_timer > dur + 0.4:
            draw_text(self.screen, "press ENTER to sing", 26, config.WIDTH // 2,
                      config.HEIGHT - 40, config.COLOR_GOLD, align="center")

    def _play_phrase(self):
        if not self.phrase_data:
            return
        notes = [(pitch.midi_to_hz(n[0]), n[1], 0.02) for n in self.phrase_data["notes"]]
        wav = self.voice.render_phrase(notes)
        self.app.audio.play_voice(wav, volume=0.9)

    def _draw_record(self):
        # recording UI: big level bar + progress
        draw_text(self.screen, "NOW YOU", 40, config.WIDTH // 2, 190,
                  config.COLOR_PLAYER, align="center")
        draw_text(self.screen, "sing the phrase back", 22, config.WIDTH // 2, 240,
                  config.COLOR_UI_DIM, align="center")
        # level meter
        bar_w = config.WIDTH - 300
        bx, by = 150, 330
        pygame.draw.rect(self.screen, (50, 50, 80), (bx, by, bar_w, 26), border_radius=8)
        lvl = min(1.0, self.record_level * 3.0)
        pygame.draw.rect(self.screen, config.COLOR_GOOD if lvl > 0.05 else config.COLOR_UI_DIM,
                         (bx, by, int(bar_w * lvl), 26), border_radius=8)
        # progress ring
        prog = min(1.0, self.record_progress)
        draw_text(self.screen, f"{int(prog * 100)}%", 22, bx + bar_w + 40, by - 4,
                  config.COLOR_UI)
        # countdown
        remaining = int(RECORD_SECONDS * (1 - prog))
        draw_text(self.screen, str(remaining), 60, config.WIDTH // 2, 400,
                  config.COLOR_UI, align="center")
        # target ribbon faintly
        if self.phrase_data:
            self.ribbon.draw_phrase(self.screen, self.phrase_data["notes"],
                                    (*config.COLOR_UI_DIM, 120), progress=1.0)

    def _draw_analyze(self):
        draw_text(self.screen, "the echo is heard...", 34, config.WIDTH // 2,
                  config.HEIGHT // 2 - 30, config.COLOR_UI, align="center")
        t = time.time()
        dots = "." * (int(t * 3) % 4)
        draw_text(self.screen, dots, 30, config.WIDTH // 2, config.HEIGHT // 2 + 20,
                  config.COLOR_UI_DIM, align="center")

    def _draw_result(self):
        beat = self.beat
        if not beat:
            return
        cdata = story.CHARACTERS[beat["who"]]
        if self.beat.get("kind") == "silence":
            self._draw_silence_result(cdata)
            return
        if self.result is None:
            return
        res = self.result
        # headline
        headline = {"perfect": "PERFECT ECHO", "good": "GOOD ECHO", "weak": "WEAK ECHO",
                    "lost": "THE ECHO IS LOST"}[res.summary]
        hcol = {"perfect": config.COLOR_GOOD, "good": config.COLOR_GOOD,
                "weak": config.COLOR_GOLD, "lost": config.COLOR_BAD}[res.summary]
        draw_text(self.screen, headline, 44, config.WIDTH // 2, 150, hcol, align="center")
        draw_text(self.screen, f"fidelity {res.fidelity*100:.0f}%  ·  {res.perfect}/{res.total} perfect",
                  22, config.WIDTH // 2, 200, config.COLOR_UI, align="center")
        # draw both ribbons: expected (dim) + detected (bright, if any)
        if self.phrase_data:
            self.ribbon.draw_phrase(self.screen, self.phrase_data["notes"],
                                    (*cdata["color"], 120), progress=1.0)
        detected = self.result.detected_notes
        if detected:
            as_phrase = [(d[0], max(0.1, d[2] - d[1])) for d in detected]
            self.ribbon.draw_phrase(self.screen, as_phrase, config.COLOR_PLAYER, progress=1.0)
        # reaction line
        line = beat["result_ok"] if res.fidelity >= 0.5 else beat["result_bad"]
        box = pygame.Rect(80, 470, config.WIDTH - 160, 130)
        pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
        pygame.draw.rect(self.screen, cdata["color"], box, 2, border_radius=12)
        lines = wrap_text(line, 24, box.w - 40)
        yy = box.y + 14
        for ln in lines[:4]:
            draw_text(self.screen, ln, 24, box.x + 20, yy, config.COLOR_UI)
            yy += 30
        draw_text(self.screen, "press ENTER to continue", 24, config.WIDTH // 2,
                  config.HEIGHT - 34, config.COLOR_GOLD, align="center")

    def _draw_silence_result(self, cdata):
        draw_text(self.screen, "YOU STAYED", 44, config.WIDTH // 2, 150,
                  config.COLOR_GOOD, align="center")
        box = pygame.Rect(80, 220, config.WIDTH - 160, 260)
        pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
        pygame.draw.rect(self.screen, cdata["color"], box, 2, border_radius=12)
        lines = wrap_text(self.beat["result_ok"] if True else "", 24, box.w - 40)
        yy = box.y + 20
        for ln in lines[:7]:
            draw_text(self.screen, ln, 24, box.x + 20, yy, config.COLOR_UI)
            yy += 32
        draw_text(self.screen, "press ENTER to continue", 24, config.WIDTH // 2,
                  config.HEIGHT - 34, config.COLOR_GOLD, align="center")
