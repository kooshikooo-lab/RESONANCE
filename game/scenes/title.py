# RESONANCE - title scene

import pygame
import time

from .. import config
from ..app import Scene
from ..graphics import Background, ParticleField, draw_text, draw_glow
from ..audio import star_pulse


class TitleScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.bg = Background(config.WIDTH, config.HEIGHT)
        self.particles = ParticleField(config.WIDTH, config.HEIGHT, 60)
        self.t = 0.0
        self._played_pulse = False

    def on_enter(self):
        self.t = 0.0
        self._played_pulse = False

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.app.fade_to("hub")
            if event.key == pygame.K_g:
                self.app.fade_to("garden")
            if event.key == pygame.K_ESCAPE:
                self.app.running = False

    def update(self, dt):
        self.t += dt
        self.bg.update()
        if not self._played_pulse and self.t > 1.0:
            self._played_pulse = True
            self.app.audio.play_music(star_pulse(110.0, 2.5), volume=0.4)

    def draw(self):
        self.bg.draw(self.screen, pulse_energy=0.5 + 0.5 * (0.5 + 0.5 * __import__("math").sin(self.t * 0.5)))
        self.particles.draw(self.screen, dt=0.016)

        # title
        draw_text(self.screen, "R E S O N A N C E", 76, config.WIDTH // 2,
                  config.HEIGHT // 2 - 100, config.COLOR_PULSE, align="center")
        draw_text(self.screen, "a first-contact game about singing", 26, config.WIDTH // 2,
                  config.HEIGHT // 2 - 40, config.COLOR_UI_DIM, align="center")

        # subtitle: the premise
        premise = (
            "They have no words. Only tone.\n"
            "Every word is a melody. Emotion is pitch contour.\n"
            "To speak to them, you must sing."
        )
        yy = config.HEIGHT // 2 + 10
        for ln in premise.split("\n"):
            draw_text(self.screen, ln, 24, config.WIDTH // 2, yy, config.COLOR_UI,
                      align="center")
            yy += 34

        # blinking prompt
        if int(self.t * 2) % 2 == 0:
            draw_text(self.screen, "press ENTER to begin", 30, config.WIDTH // 2,
                      config.HEIGHT - 80, config.COLOR_GOLD, align="center")

        draw_text(self.screen, "press G to visit the outpost",
                  20, config.WIDTH // 2, config.HEIGHT - 50, config.COLOR_UI_DIM,
                  align="center")

        draw_text(self.screen, "a voice is the most vulnerable thing you can offer",
                  18, config.WIDTH // 2, config.HEIGHT - 28, config.COLOR_UI_DIM,
                  align="center")
