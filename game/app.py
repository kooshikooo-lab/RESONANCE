# RESONANCE - scene framework

import pygame
import numpy as np

from . import config
from .audiomanager import AudioManager
from .mic import MicRecorder
from .audio import Soundtrack, ui_accept, ui_decline
from .graphics import Background, draw_text, wrap_text
from . import pitch
from . import story
from .state import GameState
from .graphics import Ribbon, AlienForm, ParticleField, draw_glow


class Scene:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen

    def handle(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass


class App:
    """Top-level application: owns the window, audio, mic, state, and scenes."""

    def __init__(self):
        pygame.init()
        pygame.mixer.pre_init(config.SAMPLE_RATE, -16, 2, 512)
        pygame.mixer.init(config.SAMPLE_RATE, -16, 2, 512)
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption(f"{config.GAME_TITLE} — a first-contact game about singing")
        self.clock = pygame.time.Clock()
        self.audio = AudioManager()
        self.mic = MicRecorder()
        self.state = GameState()
        self.soundtrack = Soundtrack()
        self.running = True
        self.scene = None
        self.next_scene_id = None
        self.transition_t = 0.0
        self.transitioning = False

    # ---- scene management
    def set_scene(self, scene_id):
        self.next_scene_id = scene_id

    def _build_scene(self, scene_id):
        from .scenes import TITLE, HUB, ECHO, DIALOGUE, FINALE, ENDING
        if scene_id == TITLE:
            from .scenes import TitleScene
            return TitleScene(self)
        if scene_id == HUB:
            from .scenes import HubScene
            return HubScene(self)
        if scene_id == ECHO:
            from .scenes import EchoScene
            return EchoScene(self)
        if scene_id == DIALOGUE:
            from .scenes import DialogueScene
            return DialogueScene(self)
        if scene_id == FINALE:
            from .scenes import FinaleScene
            return FinaleScene(self)
        if scene_id == ENDING:
            from .scenes import EndingScene
            return EndingScene(self)
        return TitleScene(self)

    def start(self):
        self.scene = self._build_scene("title")
        self.scene.on_enter()

    # ---- main loop
    def run(self):
        self.start()
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.scene:
                    self.scene.handle(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            if self.transitioning:
                self.transition_t += dt
                if self.transition_t >= 0.4:
                    self.transitioning = False
                    self.transition_t = 0.0
                    self.scene.on_exit()
                    self.scene = self._build_scene(self.next_scene_id)
                    self.next_scene_id = None
                    self.scene.on_enter()

            if self.scene and not self.transitioning:
                self.scene.update(dt)
                self.scene.draw()
            else:
                # draw a fade during transitions
                fade = pygame.Surface((config.WIDTH, config.HEIGHT))
                fade.fill((0, 0, 0))
                a = min(255, int(self.transition_t / 0.4 * 255))
                fade.set_alpha(a)
                self.screen.blit(fade, (0, 0))

            pygame.display.flip()
        pygame.quit()

    def fade_to(self, scene_id):
        """Begin a fade transition to another scene."""
        self.next_scene_id = scene_id
        self.transitioning = True
        self.transition_t = 0.0
