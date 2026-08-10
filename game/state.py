# RESONANCE - persistent game state (trust, learned phrases, movement progress)

from . import story


class GameState:
    def __init__(self):
        self.trust = {cid: 0.0 for cid in story.CHARACTERS}
        self.learned_phrases = {}     # phrase_id -> True
        self.movement_index = 0
        self.beat_index = 0
        self.player_name = "the Speaker"
        self.ending = None
        self.song = 0                  # total successful echoes
        self.total_attempts = 0
        self.avg_fidelity = 0.0
        self.seen_intros = set()

    # ---- trust helpers
    def add_trust(self, who, amount):
        c = story.CHARACTERS[who]
        self.trust[who] = max(0.0, min(100.0, self.trust[who] + amount))

    def trust_of(self, who):
        return self.trust.get(who, 0.0)

    # ---- phrase learning
    def learn(self, phrase_id):
        self.learned_phrases[phrase_id] = True

    def knows(self, phrase_id):
        return self.learned_phrases.get(phrase_id, False)

    def learned_list(self):
        """Phrases the player can currently use in a Dialogue."""
        return [p for p, v in self.learned_phrases.items() if v]

    # ---- movement tracking
    def current_movement(self):
        if self.movement_index >= len(story.MOVEMENTS):
            return None
        return story.MOVEMENTS[self.movement_index]

    def current_beat(self):
        mv = self.current_movement()
        if mv is None:
            return None
        if self.beat_index >= len(mv["beats"]):
            return None
        return mv["beats"][self.beat_index]

    def advance_beat(self):
        mv = self.current_movement()
        if mv is None:
            return
        self.beat_index += 1
        if self.beat_index >= len(mv["beats"]):
            self.movement_index += 1
            self.beat_index = 0

    def is_first_beat_of_movement(self):
        return self.beat_index == 0

    # ---- stats
    def record_attempt(self, fidelity):
        self.total_attempts += 1
        self.song += 1 if fidelity >= 0.6 else 0
        self.avg_fidelity = (self.avg_fidelity * (self.total_attempts - 1) + fidelity) / self.total_attempts
