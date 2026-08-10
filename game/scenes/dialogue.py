# RESONANCE - the Dialogue mini-game (Mini-game 2)
#
# "answer me as an equal" (DESIGN_P4 5.2)
#
# The NPC sings a FORM (question / request / refusal / statement). You must
# ANSWER it with a phrase from your learned library - judged on GRAMMAR
# (the interval relationship to their Form), not rote echo.
#
#   * a question (rising) is answered by a statement (falling home)
#   * echoing the question back is a MIRROR - the social error the Havari
#     do not forgive
#   * singing the right KIND of answer matters more than singing it perfectly
#
# Loop: INTRO -> LISTEN (their Form) -> RESPOND (you sing a learned phrase)
#       -> ANALYZE (match against your library) -> RESULT (grammar grade).

import pygame
import threading

from .. import config
from ..app import Scene
from ..audio import get_voice, ui_accept, ui_decline, ui_dissonance
from ..graphics import (
    Background, AlienForm, Ribbon, ParticleField, draw_text, wrap_text, draw_glow,
)
from .. import pitch
from .. import story

RECORD_SECONDS = 5.0


class DialogueScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.bg = Background(config.WIDTH, config.HEIGHT)
        self.particles = ParticleField(config.WIDTH, config.HEIGHT, 50)
        self.ribbon = Ribbon(140, 320, config.WIDTH - 280, 220)
        self.phase = "intro"
        self.phase_timer = 0.0
        self.beat = None
        self.question_data = None
        self.alien = None
        self.voice = None
        self.analysis = None
        self.audio_capture = None
        self.result = None
        self._thread = None
        self.record_progress = 0.0
        self.record_level = 0.0
        self.intro_card = False

    def on_enter(self):
        beat = self.app.state.current_beat()
        if beat is None:
            self.app.fade_to("ending")
            return
        self.beat = beat
        self.phase = "intro"
        self.phase_timer = 0.0
        who = beat.get("who", "thrael")
        self.alien = AlienForm(who, 220, 420, 170, 140)
        self.voice = get_voice(story.CHARACTERS[who]["voice"])
        self.intro_card = False
        if who not in self.app.state.seen_intros:
            self.app.state.seen_intros.add(who)
            self.intro_card = True

        # the FORM they sing at us
        question_id = beat.get("phrase", "")
        self.question_data = story.PHRASES.get(question_id)
        # the canonical correct response phrase - made available so the
        # player can sing it (the story has communicated it by this point)
        response_id = beat.get("response_ok", "")
        if response_id:
            self.app.state.learn(response_id)

    # ---------------------------------------------------------------- library
    def _candidates(self):
        """Phrases the player could have sung: everything learned."""
        c = {}
        for pid in self.app.state.learned_list():
            pd = story.PHRASES.get(pid)
            if pd:
                c[pid] = pd
        return c

    # ---------------------------------------------------------------- phases
    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.phase == "intro":
                if self.intro_card:
                    self.intro_card = False
                    self.phase_timer = 0.0
                    return
                self.phase = "listen"
                self.phase_timer = 0.0
                self._play_form()
            elif self.phase == "listen" and self.phase_timer > 1.4:
                self.phase = "record"
                self.phase_timer = 0.0
                self._record()
            elif self.phase == "result":
                self.app.state.advance_beat()
                self.app.fade_to("hub")
                self.phase = "done"

    def _play_form(self):
        if not self.question_data:
            return
        notes = [(pitch.midi_to_hz(n[0]), n[1], 0.02) for n in self.question_data["notes"]]
        wav = self.voice.render_phrase(notes)
        self.app.audio.play_voice(wav, volume=0.9)

    def _record(self):
        def worker():
            audio = self.app.mic.record_blocking(
                RECORD_SECONDS,
                on_tick=lambda l, p: (setattr(self, "record_level", l),
                                      setattr(self, "record_progress", p)),
            )
            self.audio_capture = audio
            try:
                self.analysis = pitch.analyze_audio(audio, config.SAMPLE_RATE)
            except Exception:
                self.analysis = []
            self.phase = "analyze"

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    # ---------------------------------------------------------------- scoring
    def update(self, dt):
        self.bg.update()
        if self.alien:
            self.alien.update(dt, intensity=0.8)
        self.phase_timer += dt
        if self.phase == "analyze" and self._thread is not None and not self._thread.is_alive():
            self._thread = None
            self._compute_result()
            self.phase = "result"

    def _compute_result(self):
        beat = self.beat
        if beat is None:
            return
        detected = pitch.contour_to_notes(self.analysis or [])
        candidates = self._candidates()
        chosen_id, fid, _per_id = pitch.match_phrase(detected, candidates)
        response_id = beat.get("response_ok", "")
        question_form = self.question_data.get("form", "statement") if self.question_data else "statement"
        chosen_pd = candidates.get(chosen_id)
        response_form = chosen_pd.get("form", "statement") if chosen_pd else "statement"
        res = pitch.score_dialogue(question_form, response_form, chosen_id,
                                   response_id or None, fid,
                                   question_id=beat.get("phrase", "") or None)
        self.result = res
        self.app.state.record_attempt(res.overall)
        who = beat["who"]
        # trust: understood well, misread slightly, echoed (mirror) costs the most
        if res.summary == "understood":
            gain = 16
            self.app.audio.play_sfx(ui_accept())
        elif res.summary == "misread":
            gain = 2
            self.app.audio.play_sfx(ui_decline())
        else:
            gain = -6
            self.app.audio.play_sfx(ui_dissonance())
        self.app.state.add_trust(who, gain)
        # you understood them -> the question phrase is now fully understood too
        if res.summary == "understood" and beat.get("phrase"):
            self.app.state.learn(beat["phrase"])

    # ---------------------------------------------------------------- drawing
    def draw(self):
        self.bg.draw(self.screen, pulse_energy=0.6)
        self.particles.draw(self.screen, dt=0.016)
        if self.alien:
            self.alien.draw(self.screen)

        beat = self.beat
        if not beat:
            return
        cdata = story.CHARACTERS[beat["who"]]

        if self.phase == "intro":
            if self.intro_card:
                self._draw_character_intro(cdata)
                return
            self._draw_intro(beat, cdata)
        elif self.phase == "listen":
            self._draw_listen(beat, cdata)
        elif self.phase == "record":
            self._draw_record()
        elif self.phase == "analyze":
            draw_text(self.screen, "the response is heard...", 34, config.WIDTH // 2,
                      config.HEIGHT // 2, config.COLOR_UI, align="center")
        elif self.phase == "result":
            self._draw_result(beat, cdata)

    def _draw_intro(self, beat, cdata):
        box = pygame.Rect(80, 500, config.WIDTH - 160, 160)
        pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
        pygame.draw.rect(self.screen, cdata["color"], box, 2, border_radius=12)
        draw_text(self.screen, cdata["name"], 30, box.x + 20, box.y + 10, cdata["color"])
        lines = wrap_text(beat["line"], 24, box.w - 40)
        yy = box.y + 48
        for ln in lines[:4]:
            draw_text(self.screen, ln, 24, box.x + 20, yy, config.COLOR_UI)
            yy += 30
        draw_text(self.screen, "press ENTER to listen", 26, config.WIDTH // 2,
                  config.HEIGHT - 30, config.COLOR_GOLD, align="center")

    def _draw_listen(self, beat, cdata):
        draw_text(self.screen, "LISTEN", 34, config.WIDTH // 2, 200,
                  config.COLOR_UI, align="center")
        if self.question_data:
            self.ribbon.draw_phrase(self.screen, self.question_data["notes"],
                                    cdata["color"], progress=1.0)
            draw_text(self.screen, f'"{self.question_data["meaning"]}"', 20,
                      config.WIDTH // 2, 300, config.COLOR_UI_DIM, align="center")
        # their Form's label
        form_label = {
            "question": "a QUESTION - it rises, it asks",
            "request": "a REQUEST - it leans toward you",
            "refusal": "a REFUSAL - the tritone",
            "statement": "a STATEMENT - it rests",
        }.get(self.question_data["form"] if self.question_data else "statement", "")
        if form_label:
            draw_text(self.screen, form_label, 18, config.WIDTH // 2, 340,
                      config.COLOR_UI_DIM, align="center")
        if self.phase_timer > 1.4:
            draw_text(self.screen, "press ENTER to answer", 26, config.WIDTH // 2,
                      config.HEIGHT - 40, config.COLOR_GOLD, align="center")

    def _draw_record(self):
        draw_text(self.screen, "ANSWER", 40, config.WIDTH // 2, 190,
                  config.COLOR_PLAYER, align="center")
        draw_text(self.screen, "answer them - not by echoing, by meaning", 22,
                  config.WIDTH // 2, 240, config.COLOR_UI_DIM, align="center")
        bar_w = config.WIDTH - 300
        bx, by = 150, 330
        pygame.draw.rect(self.screen, (50, 50, 80), (bx, by, bar_w, 26), border_radius=8)
        lvl = min(1.0, self.record_level * 3.0)
        pygame.draw.rect(self.screen, config.COLOR_GOOD if lvl > 0.05 else config.COLOR_UI_DIM,
                         (bx, by, int(bar_w * lvl), 26), border_radius=8)
        draw_text(self.screen, f"{int(self.record_progress * 100)}%", 22,
                  bx + bar_w + 40, by - 4, config.COLOR_UI)
        # your learned phrases, as a quiet reminder of what you can say
        learned = self.app.state.learned_list()
        if learned:
            names = []
            for pid in learned:
                pd = story.PHRASES.get(pid)
                if pd:
                    names.append(pd["meaning"])
            draw_text(self.screen, "you know: " + "  |  ".join(names), 18,
                      config.WIDTH // 2, config.HEIGHT - 70, config.COLOR_UI_DIM,
                      align="center")

    def _draw_result(self, beat, cdata):
        if self.result is None:
            return
        res = self.result
        headline = {"understood": "UNDERSTOOD", "misread": "MISREAD",
                    "lost": "THE MEANING IS LOST"}[res.summary]
        hcol = {"understood": config.COLOR_GOOD, "misread": config.COLOR_GOLD,
                "lost": config.COLOR_BAD}[res.summary]
        draw_text(self.screen, headline, 44, config.WIDTH // 2, 140, hcol, align="center")
        # what they sang, and how it fit
        if res.chosen_id:
            pd = story.PHRASES.get(res.chosen_id)
            if pd:
                draw_text(self.screen, f'you sang: "{pd["meaning"]}"', 22,
                          config.WIDTH // 2, 195, config.COLOR_UI, align="center")
        if res.mirror:
            draw_text(self.screen, "you echoed the question back - a mirror, not an answer",
                      20, config.WIDTH // 2, 230, config.COLOR_BAD, align="center")
        else:
            draw_text(self.screen, f"grammar fit {res.grammar_fit*100:.0f}%  ·  sung {res.fidelity*100:.0f}%",
                      20, config.WIDTH // 2, 230, config.COLOR_UI_DIM, align="center")

        box = pygame.Rect(80, 470, config.WIDTH - 160, 130)
        pygame.draw.rect(self.screen, (18, 16, 40), box, border_radius=12)
        pygame.draw.rect(self.screen, cdata["color"], box, 2, border_radius=12)
        good = res.summary == "understood"
        line = beat["result_ok"] if good else beat["result_bad"]
        lines = wrap_text(line, 24, box.w - 40)
        yy = box.y + 14
        for ln in lines[:4]:
            draw_text(self.screen, ln, 24, box.x + 20, yy, config.COLOR_UI)
            yy += 30
        draw_text(self.screen, "press ENTER to continue", 24, config.WIDTH // 2,
                  config.HEIGHT - 34, config.COLOR_GOLD, align="center")

    def _draw_character_intro(self, cdata):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 6, 20, 235))
        self.screen.blit(overlay, (0, 0))
        draw_glow(self.screen, config.WIDTH // 2, 210, cdata["color"], 160, 40)
        pygame.draw.circle(self.screen, cdata["color"],
                           (config.WIDTH // 2, 210), 60)
        draw_text(self.screen, cdata["name"], 52, config.WIDTH // 2, 300,
                  cdata["color"], align="center")
        draw_text(self.screen, cdata["role"], 24, config.WIDTH // 2, 350,
                  config.COLOR_UI_DIM, align="center")
        intro_lines = wrap_text(cdata["intro"], 24, config.WIDTH - 300)
        yy = 410
        for ln in intro_lines[:6]:
            draw_text(self.screen, ln, 24, config.WIDTH // 2, yy,
                      config.COLOR_UI, align="center")
            yy += 32
        draw_text(self.screen, "press ENTER to approach", 24, config.WIDTH // 2,
                  config.HEIGHT - 50, config.COLOR_GOLD, align="center")
