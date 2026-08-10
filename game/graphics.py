# RESONANCE - graphics
# Vector-drawn alien forms, particle field, the waveform "ribbon" UI, and glow helpers.
# No image assets - everything is drawn live so the game stays self-contained.

import pygame
import math
import numpy as np
import random

from . import config

# ---------------------------------------------------------------- helpers

glow_cache = {}


def make_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    return surf


def glow(radius, color, alpha):
    """Pre-render a soft radial glow sprite for cheap blitting."""
    radius = int(radius)
    s = make_surface(radius * 2, radius * 2)
    cx = cy = radius
    if len(color) == 4:
        color = color[:3]
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


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


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

    def update(self):
        pass

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


# ---------------------------------------------------------------- the diplomatic outpost (OutpostValley)

class OutpostValley:
    """The frontier world under Proxima: a brand-new diplomatic outpost.

    Not an ancient civilization - a young one. A cluster of prefab hab-domes and
    a landing field have just been set down on the twilight valley floor. Emissary
    crews from many species are arriving; there are string lights strung between
    the buildings, shuttles blinking on their pads, and native flora planted in
    beds between the habs. It is a campus. It smells like fresh paint and curiosity.
    """

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.rng = random.Random(31415)
        self.t = 0.0
        self.sun_x = w * 0.8
        self.sun_y = h * 0.32
        self._sky = self._make_sky()
        self._ridges = self._make_ridges()
        self._habs = self._make_habs()
        self._shuttles = self._make_shuttles()
        self._flora = self._make_flora()
        self._lights = self._make_string_lights()
        self._spores = [
            [self.rng.uniform(0, w), self.rng.uniform(h * 0.3, h * 0.95),
             self.rng.uniform(-4, 4), self.rng.uniform(-14, -6),
             self.rng.uniform(1.0, 2.6)]
            for _ in range(50)
        ]

    def _make_sky(self):
        """Vertical gradient: deep violet zenith -> warm rust horizon glow near the sun."""
        surf = make_surface(self.w, self.h)
        zenith = (22, 12, 46)
        horizon = (96, 40, 58)
        suncol = (198, 96, 62)
        for y in range(self.h):
            t = y / self.h
            col = lerp_color(zenith, horizon, min(1.0, t * 1.3))
            dy = (y - self.sun_y) / (self.h * 0.8)
            warm = 1.0 / (1.0 + (dy * dy) * 2.2)
            if warm > 0.03:
                col = lerp_color(col, suncol, min(1.0, warm * 0.5))
            pygame.draw.line(surf, col, (0, y), (self.w, y))
        return surf

    def _make_ridges(self):
        """Layered silhouettes rimming the valley."""
        layers = []
        for layer in range(3):
            base = 0.42 + layer * 0.16
            amp = 46 + layer * 22
            color = lerp_color((70, 30, 56), (30, 14, 34), layer / 3.0)
            pts = []
            n = 14
            for i in range(n + 1):
                xx = self.w * i / n
                yy = self.h * (base + 0.05 * math.sin(i * 2.1 + layer))
                yy += self.rng.uniform(-amp, amp) * 0.5
                pts.append((xx, yy))
            layers.append((color, pts))
        return layers

    def _make_habs(self):
        """A freshly-landed cluster of hab-domes and prefab modules, warm with windows."""
        habs = []
        # domes on the right ridge
        for i in range(4):
            x = self.w * (0.62 + i * 0.09) + self.rng.uniform(-10, 10)
            r = self.rng.uniform(40, 70)
            ground = self.h * (0.68 - 0.04 * i)
            phase = self.rng.uniform(0, 6.28)
            habs.append(("dome", x, ground, r, phase))
        # a row of prefab modules on the left
        for i in range(3):
            x = self.w * (0.10 + i * 0.09) + self.rng.uniform(-8, 8)
            w = self.rng.uniform(60, 90)
            hgt = self.rng.uniform(26, 38)
            ground = self.h * (0.76 + 0.02 * i)
            phase = self.rng.uniform(0, 6.28)
            habs.append(("module", x, ground, w, hgt, phase))
        return habs

    def _make_shuttles(self):
        """Small emissary shuttles on their landing pads."""
        shuttles = []
        for i in range(3):
            x = self.w * (0.24 + i * 0.18) + self.rng.uniform(-14, 14)
            ground = self.h * (0.84 + (i % 2) * 0.02)
            scale = self.rng.uniform(0.8, 1.15)
            phase = self.rng.uniform(0, 6.28)
            hue = self.rng.choice([(120, 180, 255), (220, 160, 120), (150, 220, 190)])
            shuttles.append([x, ground, scale, phase, hue])
        return shuttles

    def _make_flora(self):
        """Native bioluminescent flora planted between the habs."""
        flora = []
        for _ in range(34):
            x = self.rng.uniform(0, self.w)
            depth = self.rng.uniform(0.15, 0.9)
            ground = self.h * (0.66 + depth * 0.3)
            height = (40 + depth * 110) * (0.7 + 0.6 * self.rng.random())
            hue = self.rng.choice([
                (60, 220, 190), (40, 200, 230), (120, 190, 255),
                (200, 170, 120), (110, 230, 180),
            ])
            phase = self.rng.uniform(0, 6.28)
            curve = self.rng.uniform(-24, 24)
            flora.append([x, ground, height, hue, phase, curve, depth])
        return flora

    def _make_string_lights(self):
        """Festive lights strung between poles across the plaza - someone's first decoration."""
        # two poles
        poles = [
            (self.w * 0.42, self.h * 0.80),
            (self.w * 0.62, self.h * 0.78),
        ]
        bulbs = []
        n = 11
        for i in range(n + 1):
            u = i / n
            x = poles[0][0] + (poles[1][0] - poles[0][0]) * u
            y = poles[0][1] + (poles[1][1] - poles[0][1]) * u - math.sin(math.pi * u) * 34
            bulbs.append((x, y, self.rng.uniform(0, 6.28)))
        return poles, bulbs

    def update(self):
        self.t += 0.016

    # ------------------------------------------------------------ draw

    def draw(self, screen, energy=1.0):
        self.update()
        t = self.t
        w, h = self.w, self.h

        # sky + Proxima
        screen.blit(self._sky, (0, 0))
        sx, sy = self.sun_x, self.sun_y
        breathe = 0.5 + 0.5 * math.sin(t * 0.35)
        for rr, col, a in (
            (300, (120, 40, 60), 14),
            (190, (170, 62, 66), 20),
            (120, (210, 90, 72), 26),
        ):
            draw_glow(screen, sx, sy, col, int(rr * (0.85 + 0.15 * breathe)), a)
        pygame.draw.circle(screen, (255, 150, 120), (int(sx), int(sy)),
                           int(34 + 5 * breathe))
        pygame.draw.circle(screen, (255, 220, 190), (int(sx), int(sy)),
                           int(20 + 3 * breathe))

        # ridges
        for color, pts in self._ridges:
            poly = pts + [(w, h), (0, h)]
            pygame.draw.polygon(screen, color, poly)

        # valley floor
        pygame.draw.rect(screen, (24, 12, 30), (0, int(h * 0.9), w, int(h * 0.1)))

        # hab-domes (right)
        for hab in self._habs:
            if hab[0] == "dome":
                _, x, ground, r, phase = hab
                pygame.draw.arc(screen, (52, 26, 54), (int(x - r), int(ground - r), int(2 * r), int(2 * r)),
                                math.pi, 2 * math.pi, 2)
                pygame.draw.arc(screen, (84, 40, 60), (int(x - r), int(ground - r), int(2 * r), int(2 * r)),
                                math.pi, 2 * math.pi, 1)
                # warm windows breathing
                for k in range(3):
                    a = math.pi + (k + 0.5) * (math.pi / 3)
                    wx = x + math.cos(a) * r * 0.6
                    wy = ground - math.sin(a) * r * 0.6
                    on = 0.5 + 0.5 * math.sin(t * 0.7 + phase + k * 2.1)
                    draw_glow(screen, wx, wy, (255, 190, 120), int(5 + 3 * on), int(50 + 60 * on))
            else:
                _, x, ground, ww, hgt, phase = hab
                pygame.draw.rect(screen, (46, 24, 50), (int(x - ww / 2), int(ground - hgt), int(ww), int(hgt)))
                pygame.draw.rect(screen, (76, 38, 58), (int(x - ww / 2), int(ground - hgt), int(ww), int(hgt)), 1)
                for k in range(3):
                    wx = x - ww / 2 + ww * (0.25 + k * 0.25)
                    on = 0.5 + 0.5 * math.sin(t * 0.9 + phase + k)
                    draw_glow(screen, wx, ground - hgt * 0.5, (255, 200, 150), 4, int(30 + 50 * on))

        # shuttles on pads
        for x, ground, scale, phase, hue in self._shuttles:
            self._draw_shuttle(screen, x, ground, scale, phase, hue, t)

        # string lights across the plaza
        poles, bulbs = self._lights
        for px, py in poles:
            pygame.draw.rect(screen, (70, 40, 60), (int(px - 3), int(py - 34), 6, 34))
        for i, (bx, by, ph) in enumerate(bulbs):
            on = 0.5 + 0.5 * math.sin(t * 1.6 + ph)
            col = (255, 210, 150) if i % 3 != 0 else (150, 220, 255)
            draw_glow(screen, bx, by, col, int(4 + 3 * on), int(40 + 70 * on))

        # native flora in planted beds
        for x, ground, height, hue, phase, curve, depth in self._flora:
            pulse = 0.5 + 0.5 * math.sin(t * 1.6 + phase)
            sway = math.sin(t * 0.9 + phase) * (6 + depth * 10)
            base = (x, ground)
            tip = (x + curve * 0.4 + sway, ground - height)
            ctrl = (x + curve + sway * 1.6, ground - height * 0.55)
            pts = self._quad(base, ctrl, tip, 8)
            pygame.draw.lines(screen, (*hue, 80), False, pts, 2)
            bx, by = tip
            br = int(6 + 5 * pulse)
            draw_glow(screen, bx, by, hue, int(br * 3), 50 + int(45 * pulse))
            pygame.draw.circle(screen, (*hue, 255), (int(bx), int(by)), br)

        # spores of light
        for p in self._spores:
            p[0] += p[2] * 0.016
            p[1] += p[3] * 0.016
            if p[1] < 0:
                p[1] = h
            twinkle = 0.5 + 0.5 * math.sin(t * 2.2 + p[0] * 0.01)
            a = int(30 + 70 * twinkle)
            draw_glow(screen, int(p[0]), int(p[1]), (230, 210, 170), int(p[4] * 2.0), a)

    def _draw_shuttle(self, screen, x, ground, scale, phase, hue, t):
        """A small emissary shuttle resting on its pad, nav-light blinking."""
        bobbing = math.sin(t * 0.8 + phase) * 2
        yy = ground + bobbing
        # pad ring
        pygame.draw.ellipse(screen, (50, 30, 50), (int(x - 34 * scale), int(ground + 2), int(68 * scale), 8))
        # body (a rounded saucer)
        pygame.draw.ellipse(screen, hue, (int(x - 30 * scale), int(yy - 12 * scale), int(60 * scale), int(16 * scale)))
        pygame.draw.ellipse(screen, (*hue, 200), (int(x - 22 * scale), int(yy - 16 * scale), int(30 * scale), int(8 * scale)))
        # struts
        for s in (-1, 1):
            pygame.draw.line(screen, (120, 120, 140), (int(x + s * 20 * scale), int(yy + 4 * scale)),
                             (int(x + s * 24 * scale), int(ground + 4)), 2)
        # blinking nav light
        on = 0.5 + 0.5 * math.sin(t * 3.0 + phase)
        draw_glow(screen, x, int(yy - 18 * scale), (255, 90, 90) if on > 0.5 else (120, 160, 255),
                  int(6 + 4 * on), int(40 + 60 * on))

    @staticmethod
    def _quad(p0, p1, p2, steps):
        pts = []
        for i in range(steps + 1):
            u = i / steps
            inv = 1 - u
            x = inv * inv * p0[0] + 2 * inv * u * p1[0] + u * u * p2[0]
            y = inv * inv * p0[1] + 2 * inv * u * p1[1] + u * u * p2[1]
            pts.append((x, y))
        return pts


class EmissaryNPC:
    """A young emissary from one of the many delegations now at the outpost.

    Background figures, small, each a different species silhouette, wandering the
    plaza the way students wander a quad. The outpost is crowded and brand-new and
    everyone is a little bit thrilled to be here.
    """

    TYPES = ("slim", "round", "quad", "float")

    def __init__(self, x, y, seed):
        rng = random.Random(seed)
        self.x, self.y = x, y
        self.kind = rng.choice(self.TYPES)
        self.hue = rng.choice([
            (150, 190, 255), (200, 170, 255), (150, 230, 190),
            (255, 190, 130), (255, 230, 170), (170, 220, 255),
        ])
        self.phase = rng.uniform(0, 6.28)
        self.speed = rng.uniform(10, 22)
        self.dir = rng.choice((-1, 1))
        self.t = rng.uniform(0, 10)

    def update(self, dt):
        self.t += dt
        self.x += self.dir * self.speed * dt

    def draw(self, screen, bounds):
        # reverse direction at the walk bounds
        if self.x < bounds[0] or self.x > bounds[1]:
            self.dir *= -1
        t = self.t
        y = self.y + math.sin(t * 1.7 + self.phase) * 2
        c = self.hue
        k = self.kind
        if k == "slim":
            # tall thin figure
            hgt = 34
            pygame.draw.line(screen, c, (int(self.x), int(y - hgt)), (int(self.x), int(y)), 3)
            pygame.draw.circle(screen, c, (int(self.x), int(y - hgt - 4)), 4)
        elif k == "round":
            # a wobbling sphere with two eye-stalks
            pygame.draw.circle(screen, c, (int(self.x), int(y - 10)), 8)
            pygame.draw.line(screen, c, (int(self.x - 4), int(y - 16)), (int(self.x - 5), int(y - 22)), 2)
            pygame.draw.line(screen, c, (int(self.x + 4), int(y - 16)), (int(self.x + 5), int(y - 22)), 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x - 5), int(y - 23)), 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 5), int(y - 23)), 2)
        elif k == "quad":
            # a low many-legged figure
            pygame.draw.ellipse(screen, c, (int(self.x - 10), int(y - 10), 20, 10))
            pygame.draw.circle(screen, c, (int(self.x + 10), int(y - 12)), 4)
            for s in (-7, -2, 2, 7):
                pygame.draw.line(screen, c, (int(self.x + s), int(y - 4)), (int(self.x + s), int(y + 4)), 2)
        else:
            # a floating bell drifting like a jellyfish
            pygame.draw.polygon(screen, c, [
                (int(self.x), int(y - 14)), (int(self.x - 8), int(y)), (int(self.x + 8), int(y)),
            ])
            for s in (-1, 1):
                pygame.draw.line(screen, c, (int(self.x + s * 4), int(y)), (int(self.x + s * 6), int(y + 8)), 2)
            draw_glow(screen, self.x, y - 12, c, 10, 30)


# ---------------------------------------------------------------- alien forms

class AlienForm:
    """A vector-drawn Havari: a flowing 'choir body' whose shape follows its voice.

    Each character has a distinct silhouette (morphology), so the player can tell
    them apart at a glance:
      * seravak - tall and flowing, a great drooping trunk with hanging fringe
      * ilyan   - small and sprightly, round, with a bright crown of crests
      * thrael  - geometric, metallic, precise: a faceted obelisk
      * pulse   - vast and low, the horizon itself breathing
    """

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
        self.morph = CHARACTERS.get(character_id, {}).get("morph", "seravak")

    def update(self, dt, singing=0.0, intensity=1.0):
        self.t += dt
        self.intensity = intensity
        # the body breathes with the phrase
        self.mantle_pulse = 0.5 + 0.5 * math.sin(self.t * 1.8)

    def draw(self, screen):
        morph = self.morph
        if morph == "ilyan":
            self._draw_ilyan(screen)
        elif morph == "thrael":
            self._draw_thrael(screen)
        elif morph == "pulse":
            self._draw_pulse(screen)
        else:
            self._draw_seravak(screen)

    # ------------------------------------------------------------ seravak: tall, flowing
    def _draw_seravak(self, screen):
        c = self.color
        x, y = self.x, self.y
        t = self.t
        sway = math.sin(t * 0.9) * 16
        base = int(self.h * 0.55)
        body = make_surface(self.w + 80, self.h)
        ox, oy = 40, 0
        # main trunk (tapered) - taller and narrower than before
        n = 26
        pts = []
        for i in range(n + 1):
            u = i / n
            yy = oy + y + u * base
            width = int(self.w * (0.22 + 0.42 * (1 - u) * (1 - u)))
            pts.append((ox + x + sway * (u + 0.3) - width, yy))
        for i in range(n, -1, -1):
            u = i / n
            yy = oy + y + u * base
            width = int(self.w * (0.22 + 0.42 * (1 - u) * (1 - u)))
            pts.append((ox + x + sway * (u + 0.3) + width, yy))
        pygame.draw.polygon(body, c, pts)
        # hanging fringe: long drooping fronds that sway slowly (the 'choir robe')
        for k in range(7):
            fx = ox + x + sway * 0.6 + (k - 3) * 18
            fy = oy + y + 18 + (k % 2) * 14
            hang = int(self.h * (0.30 + 0.06 * ((k * 7) % 4)))
            wav = math.sin(t * 1.2 + k) * 8
            fpts = [(fx, fy)]
            for s in range(1, 5):
                fpts.append((fx + wav * (s / 4) * (s / 4), fy + hang * s / 4))
            pygame.draw.lines(body, (*c, 210), False, fpts, max(2, 7 - k))
        # resonant bladders - small, clustered low
        rng = random.Random(hash(self.cid) & 0xffff)
        for row in range(5):
            for col in range(3):
                bx = ox + x + sway * (0.2 + row * 0.12) + (col - 1) * 16
                by = oy + y + row * 24 + 26
                blink = 0.5 + 0.5 * math.sin(t * 2.2 + row * 1.3 + col * 0.7)
                r = 5 + int(3 * blink * self.mantle_pulse)
                pygame.draw.circle(body, (*c, int(120 + 100 * blink)),
                                   (int(bx), int(by)), r)
        screen.blit(body, (0, 0))
        draw_glow(screen, x, y + base // 2, c, self.w * 2, 18)

    # ------------------------------------------------------------ ilyan: small, sprightly
    def _draw_ilyan(self, screen):
        c = self.color
        x, y = self.x, self.y
        t = self.t
        bob = math.sin(t * 3.1) * 7
        sway = math.sin(t * 2.4) * 10
        body = make_surface(self.w + 80, self.h)
        ox, oy = 40, 0
        # round compact body
        r = int(self.w * 0.42)
        cy = oy + y + self.h * 0.5 + bob
        pygame.draw.circle(body, c, (ox + x, int(cy)), r)
        # a crown of crests (bright, playful) - like a feathered headdress
        for k in range(5):
            a = -math.pi * 0.85 + k * (math.pi * 0.85 / 4)
            lx = ox + x + math.cos(a) * r * 1.25 + sway * 0.3
            ly = cy + math.sin(a) * r * 1.1
            l = 8 + 6 * math.sin(t * 5 + k * 1.7)
            lx2 = lx + math.cos(a + 0.7) * l
            ly2 = ly + math.sin(a + 0.7) * l
            pygame.draw.line(body, (*c, 230), (int(lx), int(ly)), (int(lx2), int(ly2)),
                             max(2, 5 - k))
            draw_glow(body, lx2, ly2, c, 8, 160)
        # one bright 'eye' bladder
        blink = 0.5 + 0.5 * math.sin(t * 4.4)
        pygame.draw.circle(body, (255, 255, 255), (int(ox + x), int(cy - r * 0.25)),
                           int(5 + 3 * blink))
        pygame.draw.circle(body, (*c, 220), (int(ox + x), int(cy - r * 0.25)),
                           int(8 + 4 * blink))
        screen.blit(body, (0, 0))
        draw_glow(screen, x, int(y + self.h * 0.5), c, self.w * 2, 20)

    # ------------------------------------------------------------ thrael: geometric, metallic
    def _draw_thrael(self, screen):
        c = self.color
        x, y = self.x, self.y
        t = self.t
        sway = math.sin(t * 0.4) * 3   # barely moves - rigid, exact
        body = make_surface(self.w + 80, self.h)
        ox, oy = 40, 0
        base = int(self.h * 0.5)
        n = 10
        # a faceted obelisk of stacked quadrilaterals
        for i in range(n):
            u0 = i / n
            u1 = (i + 1) / n
            yy0 = oy + y + u0 * base
            yy1 = oy + y + u1 * base
            w0 = int(self.w * (0.34 - u0 * 0.14))
            w1 = int(self.w * (0.34 - u1 * 0.14))
            shade = 1.0 - 0.35 * ((i * 2654435761) % 5) / 5
            col = tuple(int(v * shade) for v in c)
            quad = [
                (ox + x + sway - w0, yy0), (ox + x + sway + w0, yy0),
                (ox + x + sway + w1, yy1), (ox + x + sway - w1, yy1),
            ]
            pygame.draw.polygon(body, col, quad)
            # a hairline seam between facets
            pygame.draw.line(body, (*c, 90), (ox + x + sway - w0, yy0),
                             (ox + x + sway + w0, yy0), 1)
        # apex
        w0 = int(self.w * 0.20)
        apex = (ox + x + sway, oy + y - int(self.h * 0.08))
        pygame.draw.polygon(body, c, [
            (ox + x + sway - w0, oy + y), apex, (ox + x + sway + w0, oy + y),
        ])
        # precise, small resonators along the seam
        for i in range(6):
            by = oy + y + 8 + i * (base - 16) / 6
            on = 0.5 + 0.5 * math.sin(t * 3.0 + i)
            r = 3 + int(2 * on)
            pygame.draw.circle(body, (255, 255, 255), (ox + x + sway, int(by)), r)
            pygame.draw.circle(body, (*c, 200), (ox + x + sway, int(by)), int(r * 2.2))
        screen.blit(body, (0, 0))
        draw_glow(screen, x, y + base // 2, c, self.w * 2, 16)

    # ------------------------------------------------------------ pulse: vast, low, the horizon
    def _draw_pulse(self, screen):
        c = self.color
        x, y = self.x, self.y
        t = self.t
        body = make_surface(self.w + 200, int(self.h * 0.6))
        ox, oy = 100, 0
        breathe = 0.5 + 0.5 * math.sin(t * 0.6)
        hw = int(self.w * 0.6 * (0.7 + 0.3 * breathe))
        # a low, wide ridge that swells - the star condensing into a body
        pts = []
        n = 30
        for i in range(n + 1):
            u = i / n
            xx = ox + x - hw + 2 * hw * u
            yy = oy + y + self.h * 0.45 - int(self.h * 0.3 * math.sin(math.pi * u) * (0.6 + 0.4 * breathe))
            pts.append((xx, yy))
        pts += [(ox + x + hw, oy + y + self.h * 0.6), (ox + x - hw, oy + y + self.h * 0.6)]
        pygame.draw.polygon(body, c, pts)
        # a bright seam along the crown
        pygame.draw.lines(body, (255, 255, 255), False, pts[:n + 1], 3)
        # slow resonators
        for i in range(8):
            u = i / 7
            bx = ox + x - hw + 2 * hw * u
            by = oy + y + self.h * 0.45 - int(self.h * 0.28 * math.sin(math.pi * u))
            on = 0.5 + 0.5 * math.sin(t * 0.9 + i * 1.2)
            r = 4 + int(5 * on)
            pygame.draw.circle(body, (*c, 200), (int(bx), int(by)), r)
        screen.blit(body, (0, 0))
        draw_glow(screen, x, y + self.h * 0.3, c, self.w * 2, 22)


from .story import CHARACTERS


def story_color(cid):
    return CHARACTERS[cid]["color"]


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
