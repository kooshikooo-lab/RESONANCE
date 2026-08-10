# RESONANCE - FlirtLearn scene
# The visual-novel core: you and a partner in the language cafe. Your dialogue
# options ARE your phrasebook - you can only say what you have learned. A wrong
# option is not a game over; it is a correction, and the correction is a lesson.
#
# Demo script: the first date as a lesson. Elena teaches you Spanish by making
# you want to say one true thing.

import pygame

from .. import config
from ..app import Scene
from ..graphics import draw_text, wrap_text
from ..flirtgfx import CafeInterior, PartnerFigure

# ---------------------------------------------------------------- phrasebook

# phrase_id -> (es, en, learned_at)
FRASES = {
    "hola": ("hola", "hello", "your first word"),
    "buenas_noches": ("buenas noches", "good night", "Elena, the cafe"),
    "me_llamo": ("me llamo...", "my name is...", "the name game"),
    "como_estas": ("¿cómo estás?", "how are you?", "Elena asked you this"),
    "encantada": ("encantada", "delighted / pleased to meet you", "Elena taught you"),
    "otra_vez": ("otra vez", "again", "Elena, softly"),
    "me_gusta": ("me gusta", "I like", "Elena's correction"),
    "te_quiero": ("te quiero", "I love you / I care for you", "the hard one"),
}

# the player starts knowing exactly two words
START_PHRASES = ["hola", "me_llamo"]

# ---------------------------------------------------------------- the script
# Each beat: partner line (es) with a soft gloss (en), then either auto-advance
# or a set of choices from the phrasebook. "learn" adds a phrase after the beat.

BEATS = [
    {
        "speaker": "elena",
        "es": "Buenas noches. Siéntate.",
        "en": "Good evening. Sit down.",
        "learn": "buenas_noches",
    },
    {
        "speaker": "elena",
        "es": "So you want to learn Spanish. ¿Por qué?",
        "en": "...why?",
        "choices": ["hola", "me_llamo"],
    },
    {
        "speaker": "elena",
        "es": "¿Me llamo? Dímelo.",
        "en": "\"My name is...\"? Tell me.",
        "choices": ["hola", "me_llamo"],
    },
    {
        "speaker": "elena",
        "es": "Encantada. Yo soy Elena.",
        "en": "Delighted. I'm Elena.",
        "learn": "encantada",
    },
    {
        "speaker": "elena",
        "es": "¿Y cómo estás?",
        "en": "And how are you?",
        "learn": "como_estas",
        "choices": ["hola", "buenas_noches", "encantada"],
    },
    {
        "speaker": "elena",
        "es": "Bien. You see - you already know more than you think. Try again.",
        "en": "Good. Now you say something back.",
        "choices": ["como_estas", "hola", "encantada"],
    },
    {
        "speaker": "elena",
        "es": "Me gusta cómo dices eso. Te gusta el café, ¿no?",
        "en": "I like how you say that. You like the cafe, don't you?",
        "learn": "me_gusta",
        "choices": ["como_estas", "me_llamo", "encantada"],
    },
    {
        "speaker": "elena",
        "es": "Otra vez.",
        "en": "Again.",
        "learn": "otra_vez",
        "choices": ["me_gusta", "como_estas", "hola"],
    },
    {
        "speaker": "elena",
        "es": "Eso es. Otra vez, otra vez, hasta que suene tuyo.",
        "en": "That's it. Again and again until it sounds like yours.",
        "choices": ["otra_vez", "me_gusta", "como_estas"],
    },
    {
        "speaker": "elena",
        "es": "Te quiero... es una palabra grande. No la digas todavía.",
        "en": "\"Te quiero\"... is a big word. Don't say it yet.",
        "learn": "te_quiero",
        "choices": ["otra_vez", "me_gusta", "buenas_noches"],
    },
    {
        "speaker": "elena",
        "es": "Buenas noches, estudiante.",
        "en": "Good night, student.",
        "final": True,
        "choices": ["te_quiero", "buenas_noches", "otra_vez"],
    },
]

SPECIAL_REACTIONS = {
    "te_quiero": {
        "es": "Te quiero... tú también.",
        "en": "\"Te quiero\"... I care for you too.",
    },
}


class FlirtScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.cafe = CafeInterior(config.WIDTH, config.HEIGHT)
        self.partner = PartnerFigure(930, 560, scale=1.15)
        self.t = 0.0
        self.beat = 0
        self.phase = "typing"          # typing -> choices -> reaction
        self.type_t = 0.0
        self.choice = 0
        self.choices = []
        self.learned = set(START_PHRASES)
        self.new_phrase = None
        self._learn_timer = 0.0
        self.reaction = None
        self.final = False
        self._ending_t = 0.0
        self._pulse_played = False

    # ---- helpers ---------------------------------------------------------
    def _current(self):
        return BEATS[self.beat]

    def _build_choices(self, beat):
        c = beat.get("choices") or []
        c = [p for p in c if p in self.learned]
        # keep at least one option if the beat demands a choice
        if not c and beat.get("choices"):
            c = [beat["choices"][0]]
        return c

    # ---- lifecycle --------------------------------------------------------
    def on_enter(self):
        self.t = 0.0
        self.beat = 0
        self.phase = "typing"
        self.type_t = 0.0
        self.choice = 0
        self.learned = set(START_PHRASES)
        self.new_phrase = None
        self.reaction = None
        self.final = False
        self._ending_t = 0.0
        self.app.soundtrack.mood = "hope"
        b = self._current()
        self.choices = self._build_choices(b)
        if not b.get("choices"):
            self.phase = "typing"
        else:
            self.phase = "choices"

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.fade_to("title")
                return
            if self.final:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.app.fade_to("title")
                return
            if self.phase == "choices":
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.choice = (self.choice - 1) % max(1, len(self.choices))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.choice = (self.choice + 1) % max(1, len(self.choices))
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self._pick(self.choices[self.choice])
            elif self.phase in ("typing", "reaction"):
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self._advance()

    def update(self, dt):
        self.t += dt
        self.cafe.update()
        self.partner.update(dt)
        if not self._pulse_played and self.t > 0.8:
            self._pulse_played = True
            self.app.audio.play_music(self.app.soundtrack.render(6.0), volume=0.5)
        # typewriter clock
        if self.phase == "typing":
            self.type_t += dt * 34
        elif self.phase == "reaction":
            self.type_t += dt * 34
        if self.new_phrase and not self.final:
            self._learn_timer += dt
            if self._learn_timer > 2.2:
                self.new_phrase = None
                self._learn_timer = 0.0
        if self.final:
            self._ending_t += dt

    # ---- state transitions ------------------------------------------------
    def _advance(self):
        b = self._current()
        if b.get("final"):
            self.final = True
            self._ending_t = 0.0
            return
        if b.get("learn"):
            self.learned.add(b["learn"])
            self.new_phrase = b["learn"]
            self._learn_timer = 0.0
            self.app.audio.play_music(self.app.soundtrack.render(4.0), volume=0.4)
        self.beat += 1
        if self.beat >= len(BEATS):
            self.final = True
            return
        nb = self._current()
        self.choices = self._build_choices(nb)
        self.choice = 0
        if nb.get("choices"):
            self.phase = "choices"
        else:
            self.phase = "typing"
        self.type_t = 0.0

    def _pick(self, phrase_id):
        self.app.audio.play_music(self.app.soundtrack.render(2.0), volume=0.3)
        # a special reaction overrides the generic one
        self.reaction = SPECIAL_REACTIONS.get(
            phrase_id,
            {
                "es": f"«{FRASES[phrase_id][0]}»... Sí.",
                "en": f"\"{FRASES[phrase_id][1]}\"... yes.",
            },
        )
        self.phase = "reaction"
        self.type_t = 0.0
        self.partner.set_expression("warm")

    # ---- drawing ----------------------------------------------------------
    def _type_slice(self, text):
        n = min(len(text), int(self.type_t))
        return text[:n]

    def draw(self):
        self.cafe.draw(self.screen)
        self.partner.draw(self.screen)
        self._draw_dialogue()
        if self.new_phrase and not self.final:
            self._draw_learn_toast()
        if self.final:
            self._draw_ending()

    def _draw_dialogue(self):
        b = self._current()
        sp = b["speaker"]
        # the partner's words
        es = b["es"]
        en = b.get("en", "")
        if self.phase == "reaction" and self.reaction:
            es = self.reaction["es"]
            en = self.reaction["en"]
        shown = self._type_slice(es)

        # dialogue box
        box = pygame.Rect(40, 560, config.WIDTH - 80, 140)
        panel = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 0))
        pygame.draw.rect(panel, (16, 12, 22, 190), panel.get_rect(),
                         border_radius=18)
        self.screen.blit(panel, box.topleft)
        pygame.draw.rect(self.screen, (255, 210, 120), box, 2, border_radius=18)

        # speaker nameplate
        if sp == "elena":
            name = "Elena"
            col = config.COLOR_GOLD
        else:
            name = "you"
            col = config.COLOR_UI
        draw_text(self.screen, name, 22, box.x + 22, box.y + 10, col)

        # the line, wrapped
        lines = wrap_text(shown, 30, box.w - 60)
        y = box.y + 44
        for ln in lines[:3]:
            draw_text(self.screen, ln, 30, box.x + 24, y, (245, 240, 235))
            y += 34
        # gloss (the language is the point, the gloss is the crutch)
        if en:
            draw_text(self.screen, f"— {en}", 20, box.x + 24, box.y + box.h - 28,
                      config.COLOR_UI_DIM)

        # choices above the box, on the right side
        if self.phase == "choices" and self.choices:
            bx = config.WIDTH - 360
            y = box.y - 26 - len(self.choices) * 52
            for i, pid in enumerate(self.choices):
                es_w, en_w, _src = FRASES[pid]
                sel = i == self.choice
                r = pygame.Rect(bx, y, 330, 44)
                col = (255, 210, 120) if sel else (90, 80, 120)
                pygame.draw.rect(self.screen, (20, 14, 26), r,
                                 border_radius=10)
                pygame.draw.rect(self.screen, col, r, 2 if sel else 1,
                                 border_radius=10)
                draw_text(self.screen, es_w, 24, bx + 14, y + 4,
                          (255, 240, 230) if sel else (200, 195, 215))
                draw_text(self.screen, en_w, 17, bx + 16, y + 28,
                          config.COLOR_UI_DIM)
                y += 52

    def _draw_learn_toast(self):
        pid = self.new_phrase
        es, en, _src = FRASES[pid]
        w = 400
        r = pygame.Rect(config.WIDTH // 2 - w // 2, 90, w, 74)
        panel = pygame.Surface((w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (24, 40, 40, 220), panel.get_rect(),
                         border_radius=14)
        self.screen.blit(panel, r.topleft)
        pygame.draw.rect(self.screen, (120, 220, 180), r, 2, border_radius=14)
        draw_text(self.screen, f"new phrase learned:  {es}", 24,
                  r.centerx, r.y + 22, (140, 255, 190), align="center")
        draw_text(self.screen, f"\"{en}\"", 18, r.centerx, r.y + 50,
                  config.COLOR_UI_DIM, align="center")

    def _draw_ending(self):
        # slow fade on the phrase wall side, then a closing line
        a = min(1.0, self._ending_t / 2.0)
        fade = pygame.Surface((config.WIDTH, config.HEIGHT))
        fade.fill((8, 6, 14))
        fade.set_alpha(int(a * 200))
        self.screen.blit(fade, (0, 0))
        if a > 0.4:
            draw_text(self.screen,
                      "semester one, end of class",
                      40, config.WIDTH // 2, config.HEIGHT // 2 - 40,
                      (255, 210, 120), align="center")
            draw_text(self.screen,
                      "you learned to say something. it is always the same something.",
                      24, config.WIDTH // 2, config.HEIGHT // 2 + 16,
                      config.COLOR_UI_DIM, align="center")
            if int(self.t * 1.5) % 2 == 0:
                draw_text(self.screen, "press ENTER to return to the title",
                          22, config.WIDTH // 2, config.HEIGHT // 2 + 70,
                          config.COLOR_GOLD, align="center")
