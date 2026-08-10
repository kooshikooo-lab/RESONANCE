# RESONANCE - hub scene (observation deck)
# Between beats: the player chooses who to approach. MVP: shows the movement
# and the next character; pressing ENTER starts the next beat (Echo or Dialogue).

import pygame

from .. import config
from ..app import Scene
from ..graphics import Background, ParticleField, draw_text, draw_glow
from .. import story


class HubScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.bg = Background(config.WIDTH, config.HEIGHT)
        self.particles = ParticleField(config.WIDTH, config.HEIGHT, 50)
        self.t = 0.0

    def on_enter(self):
        self.t = 0.0

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                beat = self.app.state.current_beat()
                if beat is None:
                    self.app.fade_to("ending")
                    return
                mv = self.app.state.current_movement()
                if mv and mv["id"] == "m6":
                    self.app.fade_to("finale")
                    return
                kind = beat.get("kind")
                if kind in ("echo", "silence"):
                    self.app.fade_to("echo")
                else:
                    self.app.fade_to("dialogue")

    def update(self, dt):
        self.t += dt
        self.bg.update()

    def draw(self):
        self.bg.draw(self.screen, pulse_energy=0.6)
        self.particles.draw(self.screen, dt=0.016)

        mv = self.app.state.current_movement()
        if mv is None:
            draw_text(self.screen, "The story is complete.", 36, config.WIDTH // 2,
                      config.HEIGHT // 2, config.COLOR_UI, align="center")
            draw_text(self.screen, "press ENTER to see the ending", 24, config.WIDTH // 2,
                      config.HEIGHT // 2 + 50, config.COLOR_GOLD, align="center")
            return

        draw_text(self.screen, config.GAME_TITLE, 22, 20, 14, config.COLOR_UI_DIM)
        draw_text(self.screen, f"MOVEMENT — {mv['title']}", 40, config.WIDTH // 2, 120,
                  config.COLOR_PULSE, align="center")
        draw_text(self.screen, mv["summary"], 24, config.WIDTH // 2, 170,
                  config.COLOR_UI_DIM, align="center")

        # the observation deck: show the next character to approach
        beat = self.app.state.current_beat()
        if beat:
            who = beat["who"]
            cdata = story.CHARACTERS[who]
            draw_text(self.screen, cdata["name"], 32, config.WIDTH // 2, 260,
                      cdata["color"], align="center")
            draw_text(self.screen, cdata["role"], 22, config.WIDTH // 2, 300,
                      config.COLOR_UI_DIM, align="center")
            draw_glow(self.screen, config.WIDTH // 2, 400, cdata["color"], 90, 30)
            pygame.draw.circle(self.screen, cdata["color"], (config.WIDTH // 2, 400), 40)
            draw_text(self.screen, cdata["name"], 18, config.WIDTH // 2, 410,
                      config.COLOR_UI, align="center")

        if int(self.t * 2) % 2 == 0:
            draw_text(self.screen, "press ENTER to approach", 26, config.WIDTH // 2,
                      config.HEIGHT - 60, config.COLOR_GOLD, align="center")

        # trust readout
        draw_text(self.screen, "TRUST", 18, 30, 90, config.COLOR_UI_DIM)
        y = 120
        for cid, cdata in story.CHARACTERS.items():
            pygame.draw.rect(self.screen, (60, 60, 80), (30, y, 120, 10))
            v = self.app.state.trust_of(cid)
            pygame.draw.rect(self.screen, cdata["color"], (30, y, int(120 * v / 100), 10))
            draw_text(self.screen, cdata["name"], 16, 160, y - 6, config.COLOR_UI_DIM)
            y += 26
