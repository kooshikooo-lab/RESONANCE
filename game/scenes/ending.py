# RESONANCE - ending scene (placeholder until hub + full movement flow)

import pygame

from .. import config
from ..app import Scene
from ..graphics import Background, ParticleField, draw_text, wrap_text
from .. import story


class EndingScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.bg = Background(config.WIDTH, config.HEIGHT)
        self.particles = ParticleField(config.WIDTH, config.HEIGHT, 40)
        self.t = 0.0

    def on_enter(self):
        self.t = 0.0
        # pick ending by trust
        trust_sum = sum(self.app.state.trust.values())
        if trust_sum >= 120:
            ending_id = "chorus"
        elif trust_sum >= 60:
            ending_id = "voyage"
        else:
            ending_id = "silence"
        self.app.state.ending = ending_id
        self.ending = story.ENDINGS[ending_id]

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.app.running = False

    def update(self, dt):
        self.t += dt
        self.bg.update()

    def draw(self):
        self.bg.draw(self.screen, pulse_energy=0.8)
        self.particles.draw(self.screen, dt=0.016)
        if self.app.state.ending:
            end = self.app.state.ending
            title = story.ENDINGS[end]["title"]
            text = story.ENDINGS[end]["text"]
            draw_text(self.screen, f"ENDING — {title}", 44, config.WIDTH // 2, 140,
                      config.COLOR_GOLD, align="center")
            box = pygame.Rect(140, 200, config.WIDTH - 280, 280)
            pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
            lines = wrap_text(text, 26, box.w - 40)
            yy = box.y + 24
            for ln in lines[:9]:
                draw_text(self.screen, ln, 26, box.x + 20, yy, config.COLOR_UI)
                yy += 34
            if int(self.t * 2) % 2 == 0:
                draw_text(self.screen, "press ENTER to close", 24, config.WIDTH // 2,
                          config.HEIGHT - 50, config.COLOR_GOLD, align="center")
