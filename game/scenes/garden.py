# RESONANCE - the outpost showcase scene
# A quiet diorama of the diplomatic outpost: the frontier valley under Proxima,
# the main characters standing among the habs, and young emissary crews drifting
# across the plaza. Pure visual - no scoring, no plot - so the world can be seen
# and felt before any story hangs on it.

import pygame

from .. import config
from ..app import Scene
from ..graphics import (
    OutpostValley, AlienForm, EmissaryNPC, draw_text, wrap_text, draw_glow,
)
from .. import story

# (character_id, x, y, form_w, form_h)
CAST_STANDS = [
    ("seravak", 320, 150, 190, 400),
    ("ilyan", 640, 320, 110, 220),
    ("thrael", 980, 170, 150, 380),
]

CAST_NOTES = {
    "seravak": "teacher, collector of the new",
    "ilyan": "came with the youth delegation",
    "thrael": "the one actually here to negotiate",
}


class GardenScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.valley = OutpostValley(config.WIDTH, config.HEIGHT)
        self.t = 0.0
        self.forms = {}
        self.npcs = self._make_npcs()
        self.focus = 0

    def _make_npcs(self):
        # a small crowd: a diplomat pair, a tech with a toolkit, a family, wanderers
        npcs = []
        for i, (x, y) in enumerate([
            (430, 560), (520, 585), (700, 610), (830, 555),
            (240, 640), (1110, 600), (380, 630), (900, 650),
        ]):
            npcs.append(EmissaryNPC(x, y, 1000 + i * 7))
        return npcs

    def on_enter(self):
        self.t = 0.0
        self.focus = 0
        self.forms = {}
        for cid, x, y, w, h in CAST_STANDS:
            self.forms[cid] = AlienForm(cid, w, h, x, y)
        self.app.soundtrack.mood = "hope"

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.focus = (self.focus - 1) % len(CAST_STANDS)
            elif event.key == pygame.K_RIGHT:
                self.focus = (self.focus + 1) % len(CAST_STANDS)
            elif event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.app.fade_to("title")

    def update(self, dt):
        self.t += dt
        self.valley.update()
        for f in self.forms.values():
            f.update(dt, intensity=0.9)
        for n in self.npcs:
            n.update(dt)

    def draw(self):
        self.valley.draw(self.screen, energy=0.9)

        # NPC crowd drifting across the plaza
        for n in self.npcs:
            n.draw(self.screen, (80, config.WIDTH - 80))

        # the main characters
        for i, (cid, x, y, w, h) in enumerate(CAST_STANDS):
            f = self.forms[cid]
            focused = i == self.focus
            if focused:
                draw_glow(self.screen, x, y + h * 0.45, f.color, 150, 22)
            f.draw(self.screen)

        # names + roles
        for i, (cid, x, y, w, h) in enumerate(CAST_STANDS):
            cdata = story.CHARACTERS[cid]
            focused = i == self.focus
            col = cdata["color"] if focused else config.COLOR_UI_DIM
            draw_text(self.screen, cdata["name"], 22, x, y + h + 26, col, align="center")
            if focused:
                note = CAST_NOTES.get(cid, "")
                draw_text(self.screen, note, 17, x, y + h + 52,
                          config.COLOR_UI_DIM, align="center")

        # header
        draw_text(self.screen, "the outpost", 40, config.WIDTH // 2, 40,
                  (255, 200, 150), align="center")
        draw_text(self.screen,
                  "a brand-new diplomatic outpost on the frontier world - a campus, "
                  "not a capital", 20, config.WIDTH // 2, 84,
                  config.COLOR_UI_DIM, align="center")

        # footer controls
        if int(self.t * 2) % 2 == 0:
            draw_text(self.screen, "[LEFT/RIGHT] look around   [ESC] return to title",
                      20, config.WIDTH // 2, config.HEIGHT - 26,
                      config.COLOR_GOLD, align="center")
