# RESONANCE - the Dialogue mini-game (Mini-game 2)
#
# MVP STUB: reuses the Echo loop (listen -> record -> score). The full
# grammar-based "respond appropriately" version is built after Echo is solid.
# This file exists so the app scene registry and the movement flow run end-to-end.

import pygame
import threading

from .. import config
from ..app import Scene
from ..audio import get_voice, ui_accept, ui_decline
from ..graphics import (
    Background, AlienForm, Ribbon, ParticleField, draw_text, wrap_text, draw_glow,
)
from .. import pitch
from .. import story

RECORD_SECONDS = 5.0


class DialogueScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.bg = Background(config.WIDTH, config.HEIGHT)
        self.particles = ParticleField(config.WIDTH, config.HEIGHT, 50)
        self.ribbon = Ribbon(140, 320, config.WIDTH - 280, 220)
        self.phase = "intro"
        self.phase_timer = 0.0
        self.beat = None
        self.question_data = None
        self.phrase_data = None
        self.alien = None
        self.voice = None
        self.analysis = None
        self.audio_capture = None
        self.result = None
        self._thread = None
        self.record_progress = 0.0
        self.record_level = 0.0

    def on_enter(self):
        beat = self.app.state.current_beat()
        if beat is None:
            self.app.fade_to("ending")
            return
        self.beat = beat
        self.phase = "intro"
        self.phase_timer = 0.0
        who = beat.get("who", "thrael")
        self.alien = AlienForm(who, 220, 420, 170, 140)
        self.voice = get_voice(story.CHARACTERS[who]["voice"])
        self.intro_card = False
        if who not in self.app.state.seen_intros:
            self.app.state.seen_intros.add(who)
            self.intro_card = True
        # Dialogue: the player must answer with the response phrase, not echo the question
        question_id = beat.get("phrase", "")
        response_id = beat.get("response_ok", "")
        self.question_data = story.PHRASES.get(question_id)
        self.phrase_data = story.PHRASES.get(response_id)

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.phase == "intro":
                if self.intro_card:
                    self.intro_card = False
                    self.phase_timer = 0.0
                    return
                self.phase = "listen"
                self.phase_timer = 0.0
                if self.question_data:
                    notes = [(pitch.midi_to_hz(n[0]), n[1], 0.02) for n in self.question_data["notes"]]
                    self.app.audio.play_voice(self.voice.render_phrase(notes))
            elif self.phase == "listen" and self.phase_timer > 1.2:
                self.phase = "record"
                self.phase_timer = 0.0
                self._record()
            elif self.phase == "result":
                self.app.state.advance_beat()
                self.app.fade_to("hub")
                self.phase = "done"

    def _record(self):
        def worker():
            audio = self.app.mic.record_blocking(
                RECORD_SECONDS,
                on_tick=lambda l, p: (setattr(self, "record_level", l),
                                      setattr(self, "record_progress", p)),
            )
            self.audio_capture = audio
            try:
                self.analysis = pitch.analyze_audio(audio, config.SAMPLE_RATE)
            except Exception:
                self.analysis = []
            self.phase = "analyze"

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def update(self, dt):
        self.bg.update()
        if self.alien:
            self.alien.update(dt, intensity=0.8)
        self.phase_timer += dt
        if self.phase == "analyze" and self._thread is not None and not self._thread.is_alive():
            self._thread = None
            self._compute_result()
            self.phase = "result"

    def _compute_result(self):
        beat = self.beat
        if beat is None:
            return
        expected = [n for n in self.phrase_data["notes"]] if self.phrase_data else []
        detected = pitch.contour_to_notes(self.analysis or [])
        res = pitch.score_echo(expected, detected)
        self.result = res
        self.app.state.record_attempt(res.fidelity)
        who = beat["who"]
        if res.fidelity >= 0.6:
            self.app.audio.play_sfx(ui_accept())
            self.app.state.add_trust(who, 14)
            if self.phrase_data:
                self.app.state.learn(beat.get("phrase", ""))
        else:
            self.app.audio.play_sfx(ui_decline())
            self.app.state.add_trust(who, 0)

    def draw(self):
        self.bg.draw(self.screen, pulse_energy=0.6)
        self.particles.draw(self.screen, dt=0.016)
        if self.alien:
            self.alien.draw(self.screen)

        beat = self.beat
        if not beat:
            return
        cdata = story.CHARACTERS[beat["who"]]

        if self.phase == "intro":
            if self.intro_card:
                self._draw_character_intro(cdata)
                return
            box = pygame.Rect(80, 500, config.WIDTH - 160, 160)
            pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
            pygame.draw.rect(self.screen, cdata["color"], box, 2, border_radius=12)
            draw_text(self.screen, cdata["name"], 30, box.x + 20, box.y + 10, cdata["color"])
            lines = wrap_text(beat["line"], 24, box.w - 40)
            yy = box.y + 48
            for ln in lines[:4]:
                draw_text(self.screen, ln, 24, box.x + 20, yy, config.COLOR_UI)
                yy += 30
            draw_text(self.screen, "press ENTER to listen", 26, config.WIDTH // 2,
                      config.HEIGHT - 30, config.COLOR_GOLD, align="center")
        elif self.phase == "listen":
            draw_text(self.screen, "LISTEN", 34, config.WIDTH // 2, 200,
                      config.COLOR_UI, align="center")
            if self.question_data:
                self.ribbon.draw_phrase(self.screen, self.question_data["notes"],
                                        cdata["color"], progress=1.0)
                draw_text(self.screen, f'"{self.question_data["meaning"]}"', 20,
                          config.WIDTH // 2, 300, config.COLOR_UI_DIM, align="center")
            if self.phase_timer > 1.2:
                draw_text(self.screen, "press ENTER to respond", 26, config.WIDTH // 2,
                          config.HEIGHT - 40, config.COLOR_GOLD, align="center")
        elif self.phase == "record":
            draw_text(self.screen, "NOW YOU", 40, config.WIDTH // 2, 190,
                      config.COLOR_PLAYER, align="center")
            draw_text(self.screen, "answer the question", 22, config.WIDTH // 2, 240,
                      config.COLOR_UI_DIM, align="center")
            bar_w = config.WIDTH - 300
            bx, by = 150, 330
            pygame.draw.rect(self.screen, (50, 50, 80), (bx, by, bar_w, 26), border_radius=8)
            lvl = min(1.0, self.record_level * 3.0)
            pygame.draw.rect(self.screen, config.COLOR_GOOD if lvl > 0.05 else config.COLOR_UI_DIM,
                             (bx, by, int(bar_w * lvl), 26), border_radius=8)
            draw_text(self.screen, f"{int(self.record_progress * 100)}%", 22,
                      bx + bar_w + 40, by - 4, config.COLOR_UI)
        elif self.phase == "analyze":
            draw_text(self.screen, "the response is heard...", 34, config.WIDTH // 2,
                      config.HEIGHT // 2, config.COLOR_UI, align="center")
        elif self.phase == "result":
            if self.result:
                fid = self.result.fidelity
                hcol = config.COLOR_GOOD if fid >= 0.5 else config.COLOR_BAD
                draw_text(self.screen, "DIALOGUE" if fid >= 0.5 else "MISUNDERSTANDING",
                          44, config.WIDTH // 2, 150, hcol, align="center")
                draw_text(self.screen, f"fidelity {fid*100:.0f}%", 22, config.WIDTH // 2,
                          200, config.COLOR_UI, align="center")
                box = pygame.Rect(80, 470, config.WIDTH - 160, 130)
                pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
                pygame.draw.rect(self.screen, cdata["color"], box, 2, border_radius=12)
                line = beat["result_ok"] if fid >= 0.5 else beat["result_bad"]
                lines = wrap_text(line, 24, box.w - 40)
                yy = box.y + 14
                for ln in lines[:4]:
                    draw_text(self.screen, ln, 24, box.x + 20, yy, config.COLOR_UI)
                    yy += 30
                draw_text(self.screen, "press ENTER to continue", 24, config.WIDTH // 2,
                          config.HEIGHT - 34, config.COLOR_GOLD, align="center")

    def _draw_character_intro(self, cdata):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 6, 20, 235))
        self.screen.blit(overlay, (0, 0))
        draw_glow(self.screen, config.WIDTH // 2, 210, cdata["color"], 160, 40)
        pygame.draw.circle(self.screen, cdata["color"],
                           (config.WIDTH // 2, 210), 60)
        draw_text(self.screen, cdata["name"], 52, config.WIDTH // 2, 300,
                  cdata["color"], align="center")
        draw_text(self.screen, cdata["role"], 24, config.WIDTH // 2, 350,
                  config.COLOR_UI_DIM, align="center")
        intro_lines = wrap_text(cdata["intro"], 24, config.WIDTH - 300)
        yy = 410
        for ln in intro_lines[:6]:
            draw_text(self.screen, ln, 24, config.WIDTH // 2, yy,
                      config.COLOR_UI, align="center")
            yy += 32
        draw_text(self.screen, "press ENTER to approach", 24, config.WIDTH // 2,
                  config.HEIGHT - 50, config.COLOR_GOLD, align="center")
