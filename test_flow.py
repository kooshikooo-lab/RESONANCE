# RESONANCE - headless end-to-end flow test
# Walks title -> hub -> (echo/dialogue/finale per beat kind) -> ... -> ending.
# Uses a silent recording so every attempt is "lost" but the flow must complete.

import os
import sys
import numpy as np

sys.path.insert(0, r"E:\Admin\Documents\Default Project\resonance")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init(44100, -16, 2, 512)

from game.app import App
from game.scenes import TITLE, HUB, ECHO, DIALOGUE, FINALE, ENDING


def route(app):
    mv = app.state.current_movement()
    beat = app.state.current_beat()
    if beat is None:
        return None
    if mv["id"] == "m6":
        return FINALE
    return ECHO if beat["kind"] in ("echo", "silence") else DIALOGUE


def complete_echo(sc):
    sc._thread = None
    sc.audio_capture = None
    sc.analysis = []
    sc._compute_result()
    sc.state_phase = "result"
    sc.draw()
    sc._next_round()


def complete_dialogue(sc):
    sc._thread = None
    sc.audio_capture = None
    sc.analysis = []
    sc._compute_result()
    sc.phase = "result"
    sc.draw()
    sc.app.state.advance_beat()
    sc.app.fade_to(HUB)
    sc.phase = "done"


def complete_finale(sc):
    # the finale advances the beat in on_enter; nothing more to do here
    pass


def main():
    app = App()
    app.scene = app._build_scene(TITLE)
    app.scene.on_enter()
    app.fade_to(HUB)
    app.transitioning = False

    seen = []
    guard = 0
    while app.state.current_movement() is not None and guard < 20:
        app.scene = app._build_scene(HUB)
        app.scene.on_enter()
        for _ in range(4):
            app.scene.update(1 / 60)
        app.scene.draw()
        mv = app.state.current_movement()
        beat = app.state.current_beat()
        if mv is None:
            break
        sid = route(app)
        if sid is None:
            break
        sc = app._build_scene(sid)
        sc.on_enter()
        for _ in range(4):
            sc.update(1 / 60)
        sc.draw()
        if sid == ECHO:
            complete_echo(sc)
        elif sid == DIALOGUE:
            complete_dialogue(sc)
        else:
            complete_finale(sc)
        seen.append("{}/{}".format(mv["id"], beat["kind"]))
        guard += 1

    print("visited:", " -> ".join(seen))
    print("movement now:", app.state.movement_index, "beat:", app.state.beat_index)
    es = app._build_scene(ENDING)
    es.on_enter()
    es.draw()
    print("ENDING OK, avg_fidelity", round(app.state.avg_fidelity, 3))
    print("FULL FLOW TEST PASSED")


if __name__ == "__main__":
    main()
