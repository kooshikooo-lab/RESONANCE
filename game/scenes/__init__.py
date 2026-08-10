# RESONANCE - scene registry (ids + class re-exports for the app)

TITLE = "title"
HUB = "hub"
ECHO = "echo"
DIALOGUE = "dialogue"
FINALE = "finale"
ENDING = "ending"
GARDEN = "garden"
FLIRT = "flirt"

from .title import TitleScene
from .hub import HubScene
from .echo import EchoScene
from .dialogue import DialogueScene
from .finale import FinaleScene
from .ending import EndingScene
from .garden import GardenScene
from .flirt import FlirtScene

__all__ = [
    "TITLE", "HUB", "ECHO", "DIALOGUE", "FINALE", "ENDING", "GARDEN", "FLIRT",
    "TitleScene", "HubScene", "EchoScene", "DialogueScene", "FinaleScene", "EndingScene", "GardenScene", "FlirtScene",
]
