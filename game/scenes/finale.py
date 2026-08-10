# RESONANCE - finale scene (Movement VI: The Duet)
#
# The last Dialogue: The Pulse sings its vast unanswered question, and you
# must answer it. Reuses the Dialogue grammar mechanics with the star's voice,
# then the story completes and the ending resolves by trust + skill.

import pygame

from .. import config
from ..graphics import draw_text
from ..audio import star_pulse
from ..scenes.dialogue import DialogueScene


class FinaleScene(DialogueScene):
    def __init__(self, app):
        super().__init__(app)
        self._played_pulse = False

    def on_enter(self):
        super().on_enter()
        self._played_pulse = False
        self.app.soundtrack.mood = "dawn"

    def update(self, dt):
        super().update(dt)
        if not self._played_pulse and self.phase == "listen" and self.phase_timer > 0.5:
            self._played_pulse = True
            self.app.audio.play_music(star_pulse(98.0, 3.0), volume=0.5)

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.phase == "result":
                # the duet is complete - the story ends here
                self.app.state.advance_beat()
                self.app.fade_to("ending")
                self.phase = "done"
                return
        super().handle(event)

    def _draw_listen(self, beat, cdata):
        draw_text(self.screen, "THE DUET", 40, config.WIDTH // 2, 170,
                  config.COLOR_PULSE, align="center")
        if self.question_data:
            self.ribbon.draw_phrase(self.screen, self.question_data["notes"],
                                    cdata["color"], progress=1.0)
            draw_text(self.screen, f'"{self.question_data["meaning"]}"', 20,
                      config.WIDTH // 2, 290, config.COLOR_UI_DIM, align="center")
        draw_text(self.screen, "the whole choir holds still", 18, config.WIDTH // 2,
                  330, config.COLOR_UI_DIM, align="center")
        if self.phase_timer > 1.4:
            draw_text(self.screen, "press ENTER to answer", 26, config.WIDTH // 2,
                      config.HEIGHT - 40, config.COLOR_GOLD, align="center")
