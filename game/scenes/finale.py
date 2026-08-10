# RESONANCE - finale scene (Movement VI: The Duet)
# MVP: placeholder that shows the star and routes to the ending. The full
# two-voice duet mechanic is built after the Dialogue mini-game.

import pygame

from .. import config
from ..app import Scene
from ..graphics import Background, ParticleField, draw_text, draw_glow


class FinaleScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.bg = Background(config.WIDTH, config.HEIGHT)
        self.particles = ParticleField(config.WIDTH, config.HEIGHT, 60)
        self.t = 0.0
        self._played = False

    def on_enter(self):
        self.t = 0.0
        self._played = False
        self.app.soundtrack.mood = "dawn"

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.app.fade_to("ending")

    def update(self, dt):
        self.t += dt
        self.bg.update()
        from ..audio import star_pulse
        if not self._played and self.t > 1.0:
            self._played = True
            self.app.audio.play_voice(star_pulse(98.0, 3.0), volume=0.8)

    def draw(self):
        self.bg.draw(self.screen, pulse_energy=0.9 + 0.1 * __import__("math").sin(self.t))
        self.particles.draw(self.screen, dt=0.016)
        draw_text(self.screen, "THE DUET", 48, config.WIDTH // 2, 140,
                  config.COLOR_PULSE, align="center")
        draw_text(self.screen, "(the full duet mechanic arrives with the Dialogue mini-game)",
                  22, config.WIDTH // 2, 190, config.COLOR_UI_DIM, align="center")
        px, py = config.WIDTH // 2, config.HEIGHT // 2 - 40
        draw_glow(self.screen, px, py, config.COLOR_PULSE, 220, 50)
        draw_glow(self.screen, px, py, (255, 255, 255), 40, 120)
        pygame.draw.circle(self.screen, (255, 255, 255), (px, py), 22)
        if int(self.t * 2) % 2 == 0:
            draw_text(self.screen, "press ENTER", 24, config.WIDTH // 2,
                      config.HEIGHT - 50, config.COLOR_GOLD, align="center")
