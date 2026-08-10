# RESONANCE - graphics
# Vector-drawn alien forms, particle field, the waveform "ribbon" UI, and glow helpers.
# No image assets - everything is drawn live so the game stays self-contained.

import pygame
import math
import numpy as np
import random

from . import config

# ---------------------------------------------------------------- helpers

def make_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    return surf


def glow(circle_surface, radius, color, alpha):
    """Pre-render a soft radial glow sprite for cheap blitting."""
    s = make_surface(radius * 2, radius * 2)
    cx = cy = radius
    for i in range(radius, 0, -1):
        a = int(alpha * (1 - i / radius) ** 2)
        pygame.draw.circle(s, (*color, a), (cx, cy), i)
    return s


def draw_glow(screen, x, y, color, radius, alpha):
    g = glow_cache.get((radius, color, alpha))
    if g is None:
        g = glow(radius, color, alpha)
        glow_cache[(radius, color, alpha)] = g
    screen.blit(g, (x - radius, y - radius), special_flags=pygame.BLEND_PREMULTIPLIED)


glow_cache = {}


# ---------------------------------------------------------------- background

class Background:
    """Deep space + the pulse: a star that breathes, a nebula, drifting stars."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.rng = random.Random(42)
        self.stars = [
            (self.rng.uniform(0, w), self.rng.uniform(0, h),
             self.rng.uniform(0.5, 1.8), self.rng.choice([80, 110, 140]))
            for _ in range(140)
        ]
        self.nebula = self._make_nebula()
        self.t = 0.0

    def _make_nebula(self):
        surf = make_surface(self.w, self.h)
        rng = random.Random(7)
        for _ in range(60):
            x = rng.uniform(0, self.w)
            y = rng.uniform(0, self.h * 0.7)
            r = rng.uniform(60, 220)
            col = rng.choice([(40, 30, 80), (60, 20, 90), (30, 50, 90)])
            g = glow(r, col, rng.uniform(12, 30))
            surf.blit(g, (x - r, y - r))
        return surf

    def draw(self, screen, pulse_energy=1.0):
        screen.fill(config.COLOR_BG_TOP)
        screen.blit(self.nebula, (0, 0))
        self.t += 0.016
        # drifting stars
        for i, (x, y, r, a) in enumerate(self.stars):
            tw = 0.5 + 0.5 * math.sin(self.t * (0.5 + i % 5 * 0.13) + i)
            col = (int(a * (0.4 + 0.6 * tw)),) * 3
            pygame.draw.circle(screen, col, (int(x), int(y)), max(1, int(r)))
        # the pulse - a slow breathing star in the upper background
        px, py = self.w * 0.78, self.h * 0.22
        breathe = 0.5 + 0.5 * math.sin(self.t * 0.4)
        radius = int(30 + 26 * breathe * pulse_energy)
        draw_glow(screen, px, py, config.COLOR_PULSE, radius * 4, 40)
        pygame.draw.circle(screen, (255, 255, 255), (px, py), max(2, radius // 6))
        draw_glow(screen, px, py, (255, 255, 255), radius, 90)


# ---------------------------------------------------------------- alien forms

class AlienForm:
    """A vector-drawn Havari: a flowing 'choir body' whose shape follows its voice."""

    def __init__(self, character_id, w, h, x, y):
        self.cid = character_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = story_color(character_id)
        self.t = random.uniform(0, 10)
        self.mantle_pulse = 0.0
        self.intensity = 1.0
        self.bass_hum = False

    def update(self, dt, singing=0.0, intensity=1.0):
        self.t += dt
        self.intensity = intensity
        # the body breathes with the phrase
        self.mantle_pulse = 0.5 + 0.5 * math.sin(self.t * 1.8)

    def draw(self, screen):
        c = self.color
        # silhouette: a tall, flowing body
        x, y = self.x, self.y
        sway = math.sin(self.t * 0.9) * 14
        base = int(self.h * 0.5)
        # main trunk (tapered)
        body = make_surface(self.w, self.h)
        n = 26
        pts = []
        for i in range(n + 1):
            t = i / n
            yy = y + t * base
            width = int(self.w * (0.35 + 0.5 * (1 - t) * (1 - t)))
            pts.append((x + sway * (t + 0.2) - width, yy))
        for i in range(n, -1, -1):
            t = i / n
            yy = y + t * base
            width = int(self.w * (0.35 + 0.5 * (1 - t) * (1 - t)))
            pts.append((x + sway * (t + 0.2) + width, yy))
        pygame.draw.polygon(body, c, pts)
        # resonant bladders - rows that glow per note
        rng = random.Random(hash(self.cid) & 0xffff)
        for row in range(5):
            for col in range(3):
                bx = x + sway * (0.2 + row * 0.12) + (col - 1) * 18
                by = y + row * 22 + 14
                blink = 0.5 + 0.5 * math.sin(self.t * 2.2 + row * 1.3 + col * 0.7)
                r = 5 + int(3 * blink * self.mantle_pulse)
                pygame.draw.circle(body, (*c, int(120 + 100 * blink)), (int(bx), int(by)), r)
        screen.blit(body, (0, 0))
        # a soft outer glow
        draw_glow(screen, x, y + base // 2, c, self.w * 2, 18)


def story_color(cid):
    return story.CHARACTERS[cid]["color"]


from .story import CHARACTERS as story


# ---------------------------------------------------------------- ribbon (waveform UI)

class Ribbon:
    """The diegetic 'word': a glowing ribbon drawn as the contour of a phrase.
    When the player sings, their voice becomes the same ribbon language."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw_phrase(self, screen, notes, color, progress=1.0, label=None):
        """notes: list of (midi, dur). Draws a smooth contour ribbon left->right."""
        if not notes:
            return
        midis = [n[0] for n in notes]
        lo, hi = min(midis) - 2, max(midis) + 2
        span = max(1.0, hi - lo)
        # cumulative time
        xs = []
        t = 0.0
        total = sum(n[1] for n in notes)
        for n in notes:
            xs.append(t / total)
            t += n[1]
        pts = []
        for i, n in enumerate(notes):
            px = self.x + xs[i] * self.w
            py = self.y + (1 - (n[0] - lo) / span) * self.h
            pts.append((px, py))
        # draw as a smooth polyline with glow
        if len(pts) >= 2:
            draw_glow(screen, self.x, self.y + self.h / 2, color, self.w // 2, 12)
            pygame.draw.lines(screen, color, False, pts, 3)
            # progress cap
            cap = int(self.w * progress)
            for px, py in pts:
                if px - self.x <= cap:
                    pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), 3)
        if label:
            font = pygame.font.Font(None, 26)
            text = font.render(label, True, config.COLOR_UI_DIM)
            screen.blit(text, (self.x, self.y + self.h + 6))


# ---------------------------------------------------------------- particle field

class ParticleField:
    """Drifting motes of light - the feeling of being inside the alien sky."""

    def __init__(self, w, h, n=60):
        self.w = w
        self.h = h
        self.rng = random.Random(1)
        self.p = [
            [self.rng.uniform(0, w), self.rng.uniform(0, h),
             self.rng.uniform(-8, 8), self.rng.uniform(-4, 4),
             self.rng.uniform(0.5, 2.0)]
            for _ in range(n)
        ]

    def draw(self, screen, color=(150, 170, 230), dt=0.016):
        for p in self.p:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            if p[0] < 0 or p[0] > self.w:
                p[2] = -p[2]
            if p[1] < 0 or p[1] > self.h:
                p[3] = -p[3]
            a = int(40 + 40 * (0.5 + 0.5 * math.sin(p[0] * 0.01)))
            pygame.draw.circle(screen, (*color, a), (int(p[0]), int(p[1])), int(p[4]))


# ---------------------------------------------------------------- text helpers

def draw_text(screen, text, size, x, y, color=config.COLOR_UI, align="left", font_path=None):
    font = pygame.font.Font(font_path, size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    if align == "center":
        rect.center = (x, y)
    elif align == "right":
        rect.topright = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)
    return rect


def wrap_text(text, size, max_w):
    font = pygame.font.Font(None, size)
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = cur + " " + w if cur else w
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
