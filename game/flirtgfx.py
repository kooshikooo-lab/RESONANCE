# RESONANCE - FlirtLearn graphics
# The language cafe at the terminator: a window onto the copper dusk, the phrase
# wall covered in tiny love letters, warm lamp light, and a partner worth learning
# a language for. Everything is vector-drawn live - no image assets.

import math
import random

import numpy as np
import pygame

from .graphics import make_surface, draw_glow, lerp_color


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def glow_sprite(radius, color, alpha):
    s = make_surface(int(radius * 2), int(radius * 2))
    cx = cy = radius
    for i in range(int(radius), 0, -1):
        a = int(alpha * (1 - i / radius) ** 2)
        pygame.draw.circle(s, (*color, a), (int(cx), int(cy)), i)
    return s


def _vignette(w, h, strength=210.0):
    sw, sh = 160, 90
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    u = xx / (sw - 1) * 2.0 - 1.0
    v = yy / (sh - 1) * 2.0 - 1.0
    dist = np.sqrt(u ** 2 + v ** 2)
    a = np.clip((dist - 0.55) * strength, 0, 255).astype(np.uint8)
    small = pygame.Surface((sw, sh), pygame.SRCALPHA)
    alpha = pygame.surfarray.pixels_alpha(small)
    alpha[:] = a.T
    del alpha
    return pygame.transform.smoothscale(small, (w, h))


# ---------------------------------------------------------------- the cafe

class CafeInterior:
    """The language cafe. Static layers are baked once; the live parts (lamp
    glow, steam, sun flare, bokeh) are drawn each frame."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.t = 0.0
        self.rng = random.Random(2026)
        self.window_rect = pygame.Rect(60, 70, 640, 380)
        self.sun_pos = (180, 300)
        self.sky = self._make_sky(self.window_rect.w, self.window_rect.h)
        self.interior = self._make_interior()
        self.table = self._make_table()
        self.vignette = _vignette(w, h)
        self.bokeh = []
        for i in range(5):
            r = [36, 48, 60, 80, 110][i]
            self.bokeh.append([
                glow_sprite(r, (255, 190, 120), 90),
                self.rng.uniform(0, w), self.rng.uniform(h * 0.82, h),
                self.rng.uniform(4, 9), self.rng.uniform(0, 6.28),
            ])
        self.stars = []
        for _ in range(46):
            self.stars.append([
                self.rng.uniform(0.35, 1.0), self.rng.uniform(0.05, 0.7),
                self.rng.uniform(0.5, 1.6), self.rng.uniform(0, 6.28),
            ])

    # ---- sky: the terminator, copper sun on the left, dusk fading to night
    def _make_sky(self, w, h):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        u = xx / (w - 1)
        v = yy / (h - 1)
        top_left = np.array([118, 76, 120])
        top_right = np.array([16, 15, 44])
        bot_left = np.array([248, 158, 100])
        bot_right = np.array([92, 50, 92])
        c = (
            top_left * (1 - u)[..., None] * (1 - v)[..., None]
            + top_right * u[..., None] * (1 - v)[..., None]
            + bot_left * (1 - u)[..., None] * v[..., None]
            + bot_right * u[..., None] * v[..., None]
        )
        surf = pygame.Surface((w, h))
        pygame.surfarray.blit_array(
            surf, np.clip(c, 0, 255).astype(np.uint8).transpose(1, 0, 2))
        # distant Meridian skyline on the horizon
        rng = random.Random(5)
        skyline_y = int(h * 0.82)
        for i in range(26):
            bx = int(i * w / 26)
            bw = int(w / 26) + 2
            bh = int(rng.uniform(h * 0.06, h * 0.24))
            pygame.draw.rect(surf, (22, 18, 40), (bx, skyline_y - bh, bw, bh))
            if i % 5 == 0:
                px = bx + bw // 2
                pygame.draw.polygon(surf, (22, 18, 40), [
                    (px - 6, skyline_y - bh), (px, skyline_y - bh - 16),
                    (px + 6, skyline_y - bh),
                ])
            if i < 14:
                for _ in range(rng.randint(1, 3)):
                    wx = bx + rng.randint(2, bw - 4)
                    wy = skyline_y - rng.randint(4, max(5, bh - 2))
                    pygame.draw.rect(surf, (255, 180, 120), (wx, wy, 2, 3))
        return surf

    def _make_interior(self):
        s = make_surface(self.w, self.h)
        rng = self.rng
        # back wall: warm panel, slightly lighter toward the window
        for y in range(self.h):
            t = y / self.h
            c = lerp_color((84, 52, 50), (44, 30, 40), t)
            pygame.draw.line(s, c, (0, y), (self.w, y))
        # the window: sky shows through
        s.blit(self.sky, self.window_rect.topleft)
        wr = self.window_rect
        # frame + mullions
        frame = (34, 22, 30)
        pygame.draw.rect(s, frame,
                         (wr.x - 12, wr.y - 12, wr.w + 24, wr.h + 24),
                         border_radius=6)
        mw = 10
        pygame.draw.rect(s, frame,
                         (wr.x + wr.w // 3 - mw // 2, wr.y, mw, wr.h))
        pygame.draw.rect(s, frame,
                         (wr.x + 2 * wr.w // 3 - mw // 2, wr.y, mw, wr.h))
        pygame.draw.rect(s, frame,
                         (wr.x, wr.y + wr.h * 2 // 3 - mw // 2, wr.w, mw))
        # window sill
        pygame.draw.rect(s, (58, 38, 40),
                         (wr.x - 18, wr.y + wr.h, wr.w + 36, 14),
                         border_radius=3)
        pygame.draw.rect(s, (86, 56, 50),
                         (wr.x - 18, wr.y + wr.h, wr.w + 36, 4),
                         border_radius=2)
        # the phrase wall: a cork board covered in tiny love letters
        board = pygame.Rect(790, 100, 430, 500)
        pygame.draw.rect(s, (112, 86, 62), board, border_radius=10)
        pygame.draw.rect(s, (74, 54, 44), board, 4, border_radius=10)
        for _ in range(150):
            x = board.x + rng.uniform(14, board.w - 34)
            y = board.y + rng.uniform(14, board.h - 30)
            w = rng.uniform(18, 42)
            h = rng.uniform(13, 24)
            skew = rng.uniform(-4, 4)
            col = tuple(int(v) for v in rng.choices([
                (245, 226, 198), (220, 196, 232), (196, 226, 216),
                (226, 210, 180), (232, 200, 188), (206, 224, 236),
            ], k=1)[0])
            pts = [
                (x, y), (x + w, y), (x + w + skew, y + h), (x + skew, y + h),
            ]
            pygame.draw.polygon(s, col, pts)
            sc = tuple(int(v * 0.72) for v in col)
            nx = x + w * 0.12
            for i in range(3):
                lx = nx + rng.uniform(0, w * 0.7)
                ly = y + h * (0.3 + i * 0.25) + rng.uniform(-2, 2)
                pygame.draw.line(s, sc, (lx, ly), (lx + w * 0.28, ly - h * 0.14), 2)
            pygame.draw.circle(s, (60, 44, 52), (int(x + w // 2), int(y + 2)), 3)
        # a low shelf on the left with glowing bottles
        sh_y = 560
        pygame.draw.rect(s, (58, 38, 44), (30, sh_y, 420, 12), border_radius=3)
        for i in range(9):
            bx = 46 + i * 46
            bh = rng.randint(30, 58)
            bottle_col = rng.choice([
                (120, 80, 60), (70, 110, 90), (150, 110, 80), (80, 90, 130)])
            pygame.draw.rect(s, tuple(int(v * 0.6) for v in bottle_col),
                             (bx, sh_y - bh, 24, bh - 8), border_radius=4)
            pygame.draw.rect(s, bottle_col,
                             (bx, sh_y - bh, 24, bh - 8), 2, border_radius=4)
        # warm wash of lamp light on the wall
        draw_glow(s, 620, 250, (255, 190, 130), 260, 26)
        # string lights along the top
        for i in range(12):
            lx = 40 + i * (self.w - 80) / 11
            ly = 34 + 6 * math.sin(i * 1.7)
            pygame.draw.circle(s, (70, 52, 60), (int(lx), int(ly + 2)), 4)
            draw_glow(s, lx, ly, (255, 200, 140), 16, 120)
        return s

    def _make_table(self):
        s = make_surface(self.w, self.h)
        rng = self.rng
        top_y = 520
        for y in range(top_y, top_y + 130):
            t = (y - top_y) / 130
            c = lerp_color((108, 72, 56), (66, 44, 40), t)
            pygame.draw.line(s, c, (0, y), (self.w, y))
        for i in range(1, 7):
            px = int(i * self.w / 7) + rng.randint(-6, 6)
            pygame.draw.line(s, (40, 26, 30), (px, top_y + 4), (px, top_y + 126), 2)
        pygame.draw.rect(s, (44, 28, 32), (0, top_y + 130, self.w, 30))
        for i in range(3):
            lx = 120 + i * 520
            pygame.draw.rect(s, (34, 22, 28), (lx, top_y + 130, 60, 70),
                             border_radius=4)
        draw_glow(s, 640, top_y + 40, (255, 196, 140), 330, 34)
        return s

    def update(self):
        self.t += 1 / 60

    # ---- live drawing
    def draw(self, screen):
        screen.blit(self.interior, (0, 0))
        wr = self.window_rect
        # sun flare, softly breathing
        sx, sy = self.sun_pos
        breath = 0.5 + 0.5 * math.sin(self.t * 0.7)
        draw_glow(screen, wr.x + sx, wr.y + sy, (255, 190, 120),
                  90 + int(14 * breath), 60)
        draw_glow(screen, wr.x + sx, wr.y + sy, (255, 236, 200), 26, 150)
        pygame.draw.circle(screen, (255, 240, 214), (wr.x + sx, wr.y + sy), 10)
        # twinkling stars through the window (night side)
        for ux, uy, r, ph in self.stars:
            tw = 0.5 + 0.5 * math.sin(self.t * 2.2 + ph)
            px = wr.x + int(ux * wr.w)
            py = wr.y + int(uy * wr.h)
            a = int(60 + 140 * tw)
            pygame.draw.circle(screen, (200, 210, 255), (px, py), max(1, int(r)))
            draw_glow(screen, px, py, (180, 200, 255), 8, int(a * 0.35))
        # hanging lamp: shade + warm cone + glow
        lamp_x, lamp_y = 640, 30
        pygame.draw.line(screen, (40, 28, 34), (lamp_x, 0),
                         (lamp_x, lamp_y + 18), 4)
        pygame.draw.arc(screen, (60, 42, 46),
                        (lamp_x - 34, lamp_y - 6, 68, 46), 0, math.pi, 7)
        cone = make_surface(360, 400)
        cone.set_colorkey((0, 0, 0))
        pygame.draw.polygon(cone, (255, 214, 160), [
            (180, 40), (52, 400), (308, 400),
        ])
        cone.set_alpha(26)
        screen.blit(cone, (lamp_x - 180, lamp_y + 40))
        flick = 0.92 + 0.08 * math.sin(self.t * 9.0)
        draw_glow(screen, lamp_x, lamp_y + 22, (255, 200, 140),
                  46, int(180 * flick))
        pygame.draw.circle(screen, (255, 240, 210), (lamp_x, lamp_y + 22), 7)

        # the table
        screen.blit(self.table, (0, 0))

        # candle on the table
        cx, cy = 700, 516
        pygame.draw.rect(screen, (210, 200, 190),
                         (cx - 3, cy - 16, 6, 14), border_radius=2)
        fl = 0.85 + 0.15 * math.sin(self.t * 11.0)
        pygame.draw.polygon(screen, (255, 170, 80), [
            (cx, cy - 24), (cx - 3, cy - 16), (cx + 3, cy - 16),
        ])
        pygame.draw.polygon(screen, (255, 230, 170), [
            (cx, cy - 21), (cx - 1.5, cy - 16), (cx + 1.5, cy - 16),
        ])
        draw_glow(screen, cx, cy - 18, (255, 170, 90), 34, int(120 * fl))

        # steam rising from the two cups
        self._steam(screen, 320, 566)
        self._steam(screen, 976, 560, phase=2.2)

        # foreground bokeh - out of focus lamp light
        for i, b in enumerate(self.bokeh):
            spr, x, y, vx, ph = b
            x = (x + vx * 0.016) % (self.w + 200) - 100
            y = y + 3 * math.sin(self.t * 0.5 + ph)
            self.bokeh[i][1] = x
            self.bokeh[i][2] = y
            screen.blit(spr, (x - spr.get_width() / 2, y - spr.get_height() / 2))

        # depth
        screen.blit(self.vignette, (0, 0))

    def _steam(self, screen, x, y, phase=0.0):
        for i in range(3):
            tt = (self.t * 0.9 + phase + i * 0.6) % 2.6
            sy = y - tt * 34
            if sy < y - 90:
                continue
            sw = 2 + tt * 2.2
            wob = math.sin(tt * 3.1 + phase + i) * 5
            a = int(120 * (1 - tt / 2.6))
            draw_glow(screen, x + wob, sy, (230, 220, 210), int(sw), a)


# ---------------------------------------------------------------- the partner

class PartnerFigure:
    """A human partner, seated across the table - the reason you are learning.
    Waist-up, warm rim light from the window, breathing, blinking, and a face
    that reacts to what you say."""

    EXPRESSIONS = ("neutral", "smile", "laugh", "thoughtful", "warm")

    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        self.scale = scale
        self.t = 0.0
        self.expression = "smile"
        self.talking = False
        self._blink_next = 2.2
        self._blink = 0.0
        self.skin = (224, 178, 146)
        self.skin_shade = (188, 140, 116)
        self.hair = (62, 44, 38)
        self.hair_hi = (92, 68, 56)
        self.sweater = (60, 84, 100)
        self.sweater_dark = (44, 62, 78)
        self.collar = (224, 224, 214)

    def set_expression(self, expr):
        if expr in self.EXPRESSIONS:
            self.expression = expr

    def update(self, dt):
        self.t += dt
        self._blink_next -= dt
        if self._blink_next <= 0:
            self._blink = 0.14
            self._blink_next = 2.0 + random.uniform(0, 3.0)
        if self._blink > 0:
            self._blink -= dt

    # ---- drawing -------------------------------------------------------
    def draw(self, screen):
        sc = self.scale
        cx, base = self.x, self.y
        fw, fh = int(420 * sc), int(460 * sc)
        fig = make_surface(fw, fh)
        ox, oy = fw // 2, fh

        breath = math.sin(self.t * 1.9) * 3
        sway = math.sin(self.t * 0.7) * 2
        sh = lambda v: int(v * sc)

        # torso: shoulders + sweater
        shw = sh(150)                     # shoulder half-width
        tr = pygame.Rect(ox - shw, oy - sh(300), shw * 2, sh(300))
        pygame.draw.ellipse(fig, self.sweater, tr)
        # shading on the right side (away from the window)
        shd = pygame.Surface((tr.w, tr.h), pygame.SRCALPHA)
        pygame.draw.ellipse(shd, self.sweater_dark, (shd.get_width() * 0.45, 0,
                                                     shd.get_width() * 0.55,
                                                     shd.get_height()))
        fig.blit(shd, tr.topleft)
        # rim light on the left (window side)
        rim = pygame.Surface((tr.w, tr.h), pygame.SRCALPHA)
        pygame.draw.ellipse(rim, (120, 150, 168), (0, 0, shd.get_width() * 0.30,
                                                   shd.get_height()))
        rim.set_alpha(90)
        fig.blit(rim, tr.topleft)
        # a few soft wrinkle strokes on the sweater
        for i in range(3):
            wx = ox - sh(70) + i * sh(50)
            wy = oy - sh(230) + i * sh(14)
            pygame.draw.arc(fig, self.sweater_dark,
                            (wx, wy, sh(60), sh(40)), 0.2, 1.6, 2)

        # neck
        nw = sh(34)
        neck_rect = pygame.Rect(ox - nw // 2, oy - sh(348), nw, sh(56))
        pygame.draw.rect(fig, self.skin_shade, neck_rect, border_radius=sh(12))
        pygame.draw.rect(fig, self.skin, (neck_rect.x + sh(3),
                                          neck_rect.y + sh(2),
                                          neck_rect.w - sh(6), neck_rect.h - sh(3)),
                         border_radius=sh(10))

        # head
        hy = oy - sh(355) + breath * 0.6 + sway * 0.3
        hw, hh = sh(58), sh(64)
        head = pygame.Rect(int(ox - hw + sway), int(hy - hh), hw * 2, hh * 2)
        pygame.draw.ellipse(fig, self.skin_shade, head.move(sh(4), sh(4)))
        pygame.draw.ellipse(fig, self.skin, head)
        # warm cheek shading on the far side
        cheek = pygame.Surface((head.w, head.h), pygame.SRCALPHA)
        pygame.draw.ellipse(cheek, (198, 120, 96), (head.w * 0.5, head.h * 0.35,
                                                    head.w * 0.5, head.h * 0.6))
        cheek.set_alpha(70)
        fig.blit(cheek, head.topleft)

        # hair: a soft cap over the top of the head, slightly wavy
        hx = head.x
        pygame.draw.ellipse(fig, self.hair,
                            (head.x - sh(8), head.y - sh(14),
                             head.w + sh(16), head.h * 0.85),
                            )
        # hair flick / bangs
        bangs = [(head.x + sh(6), head.y + sh(20)),
                 (head.x + sh(30), head.y + sh(2)),
                 (head.x + sh(58), head.y + sh(14)),
                 (head.x + sh(84), head.y + sh(4)),
                 (head.x + sh(104), head.y + sh(24))]
        pygame.draw.lines(fig, self.hair, False, bangs, sh(8))
        # hair highlight
        pygame.draw.lines(fig, self.hair_hi, False,
                          [(head.x + sh(18), head.y + sh(8)),
                           (head.x + sh(70), head.y + sh(0))], sh(3))

        # face features (only if head not blushed away)
        eye_y = head.y + hh * 0.72
        blink_amt = 1.0 if self._blink > 0 else 0.0
        # eyes - almond shapes with a warm iris
        for ex in (head.x + hw - sh(6), head.x + hw + sh(26)):
            ebox = pygame.Rect(ex, int(eye_y - hh * 0.16), sh(20), sh(22))
            if blink_amt > 0.5:
                pygame.draw.line(fig, self.hair,
                                 (ebox.x, ebox.centery + sh(2)),
                                 (ebox.right, ebox.centery + sh(2)), sh(2))
                continue
            # lower lid shadow
            pygame.draw.ellipse(fig, self.skin_shade, ebox)
            # white
            pygame.draw.ellipse(fig, (245, 240, 232),
                                (ebox.x + sh(2), ebox.y + sh(3),
                                 sh(16), sh(13)))
            # iris
            pygame.draw.circle(fig, (96, 70, 44), (ebox.x + sh(9), ebox.y + sh(9)),
                               sh(5))
            pygame.draw.circle(fig, (20, 16, 14), (ebox.x + sh(9), ebox.y + sh(9)),
                               sh(2))
            # catchlight
            pygame.draw.circle(fig, (255, 255, 255),
                               (ebox.x + sh(6), ebox.y + sh(6)), sh(2))
            # upper lid
            pygame.draw.line(fig, self.skin, (ebox.x, ebox.y + sh(2)),
                             (ebox.right, ebox.y + sh(2)), sh(2))

        # brows
        for ex in (head.x + hw - sh(6), head.x + hw + sh(26)):
            pygame.draw.line(fig, self.hair, (ex + sh(1), eye_y - hh * 0.40),
                             (ex + sh(16), eye_y - hh * 0.46), sh(3))

        # nose - a soft suggestion
        nx = head.x + hw + sh(10)
        pygame.draw.line(fig, self.skin_shade, (nx, eye_y - hh * 0.20),
                         (nx + sh(2), eye_y + hh * 0.04), sh(2))

        # mouth, driven by expression + talking
        mx = head.x + hw + sh(10)
        my = eye_y + hh * 0.28
        if self.talking and self.expression in ("laugh", "smile"):
            pygame.draw.ellipse(fig, (140, 66, 60),
                                (mx - sh(4), my - sh(2), sh(16), sh(10)))
        else:
            if self.expression == "laugh":
                pygame.draw.arc(fig, (140, 66, 60),
                                (mx - sh(6), my - sh(6), sh(20), sh(14)),
                                0.4, 2.6, sh(3))
            elif self.expression == "warm":
                pygame.draw.arc(fig, (140, 66, 60),
                                (mx - sh(5), my - sh(4), sh(18), sh(12)),
                                0.3, 2.8, sh(2))
            else:
                pygame.draw.line(fig, (140, 66, 60), (mx - sh(2), my),
                                 (mx + sh(12), my), sh(2))

        # blush
        blush = pygame.Surface((head.w, head.h), pygame.SRCALPHA)
        pygame.draw.circle(blush, (224, 120, 100),
                           (int(head.w * 0.38), int(head.h * 0.78)), sh(10))
        pygame.draw.circle(blush, (224, 120, 100),
                           (int(head.w * 0.68), int(head.h * 0.78)), sh(10))
        blush.set_alpha(80)
        fig.blit(blush, head.topleft)

        # earrings catch the lamp light
        pygame.draw.circle(fig, (255, 214, 130), (head.x + sh(4), head.y + hh * 0.9),
                           sh(2))
        pygame.draw.circle(fig, (255, 214, 130), (head.right - sh(4), head.y + hh * 0.9),
                           sh(2))

        # blit the figure onto the screen
        screen.blit(fig, (int(cx - fw / 2), int(base - fh)))

        # soft halo behind the partner so she reads against the dark wall
        draw_glow(screen, cx, base - fh * 0.55, (255, 200, 150), fw, 26)
