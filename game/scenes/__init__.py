# RESONANCE - scene registry (ids + class re-exports for the app)

TITLE = "title"
HUB = "hub"
ECHO = "echo"
DIALOGUE = "dialogue"
FINALE = "finale"
ENDING = "ending"

from .title import TitleScene
from .hub import HubScene
from .echo import EchoScene
from .dialogue import DialogueScene
from .finale import FinaleScene
from .ending import EndingScene

__all__ = [
    "TITLE", "HUB", "ECHO", "DIALOGUE", "FINALE", "ENDING",
    "TitleScene", "HubScene", "EchoScene", "DialogueScene", "FinaleScene", "EndingScene",
]
