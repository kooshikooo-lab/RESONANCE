# RESONANCE - story data
# Characters, phrases, movements, and the two-mini-game content.
#
# Phrases are defined as (midi, duration_seconds) note lists. Their shapes are
# chosen so they SOUND like what they mean (the Havari language is iconic):
#   * questions rise at the end
#   * statements fall to the home note
#   * refusals use the tritone (the unstable interval)
#   * grief is a slow descending minor
# All tuning uses just intonation ratios off a root so it sounds "alien-perfect".

from . import config
from .pitch import midi_to_hz

A4 = 440.0
MIDI_A4 = 69.0


def m(note, dur=0.5):
    """midi number + duration helper."""
    return (round(note, 3), dur)


# ---------------------------------------------------------------- the phrase library

PHRASES = {
    # --- greetings / basic trust
    "greeting": {
        "meaning": "we are here in peace",
        "notes": [m(60.0, 0.45), m(64.0, 0.45), m(67.0, 0.45), m(64.0, 0.6)],   # rising, returns home
        "form": "statement",
        "learned_from": "seravak",
    },
    "you": {
        "meaning": "you",
        "notes": [m(62.0, 0.35), m(65.0, 0.4)],
        "form": "statement",
        "learned_from": "seravak",
    },
    "i": {
        "meaning": "I",
        "notes": [m(67.0, 0.35), m(62.0, 0.4)],
        "form": "statement",
        "learned_from": "seravak",
    },
    "are you": {
        "meaning": "are you?",
        "notes": [m(60.0, 0.35), m(63.0, 0.35), m(66.0, 0.45)],   # rising = question
        "form": "question",
        "learned_from": "ilyan",
    },
    "i am": {
        "meaning": "I am",
        "notes": [m(66.0, 0.35), m(62.0, 0.5)],                  # falls home = answer
        "form": "statement",
        "learned_from": "seravak",
    },
    # --- the child's melody (the game's leitmotif)
    "child_melody": {
        "meaning": "the child's song - I am small and not afraid",
        "notes": [m(60.0, 0.3), m(64.0, 0.3), m(67.0, 0.3), m(72.0, 0.5), m(67.0, 0.3), m(64.0, 0.6)],
        "form": "statement",
        "learned_from": "ilyan",
    },
    # --- emotions (contour = feeling)
    "sorrow": {
        "meaning": "I am grieving",
        "notes": [m(64.0, 0.5), m(62.0, 0.5), m(60.0, 0.5), m(57.0, 0.7)],   # slow descending
        "form": "statement",
        "learned_from": "seravak",
    },
    "longing": {
        "meaning": "I miss something / someone",
        "notes": [m(60.0, 0.4), m(62.0, 0.4), m(64.0, 0.4), m(65.0, 0.6)],   # rises, wants to fall
        "form": "statement",
        "learned_from": "seravak",
    },
    "joy": {
        "meaning": "I am glad / I am playing",
        "notes": [m(60.0, 0.2), m(64.0, 0.2), m(67.0, 0.2), m(72.0, 0.3), m(76.0, 0.4)],  # bright rising
        "form": "statement",
        "learned_from": "ilyan",
    },
    # --- requests / refusals (the Dialogue forms)
    "please_stay": {
        "meaning": "please stay",
        "notes": [m(60.0, 0.4), m(63.0, 0.4), m(67.0, 0.5)],      # suspense -> resolve
        "form": "request",
        "learned_from": "ilyan",
    },
    "i_will_stay": {
        "meaning": "I will stay",
        "notes": [m(67.0, 0.4), m(64.0, 0.4), m(60.0, 0.6)],      # answer, falling home
        "form": "statement",
        "learned_from": "seravak",
    },
    "no": {
        "meaning": "no / I refuse",
        "notes": [m(60.0, 0.4), m(66.0, 0.6)],                    # the tritone - refusal
        "form": "refusal",
        "learned_from": "ilyan",
    },
    "the_star_is_dying": {
        "meaning": "the star is dying",
        "notes": [m(64.0, 0.5), m(62.0, 0.5), m(59.0, 0.5), m(55.0, 0.8)],   # deep falling
        "form": "statement",
        "learned_from": "thrael",
    },
    "the_star_lives": {
        "meaning": "the star lives",
        "notes": [m(55.0, 0.4), m(59.0, 0.4), m(62.0, 0.4), m(64.0, 0.7)],    # rising from the deep
        "form": "statement",
        "learned_from": "pulse",
    },
    # --- the humility phrase (Seravak's secret)
    "humility": {
        "meaning": "I am allowed to be imperfect - sung wrong on purpose",
        "notes": [m(60.0, 0.4), m(64.0, 0.4), m(65.0, 0.4), m(64.0, 0.5), m(62.0, 0.6)],
        "form": "statement",
        "learned_from": "seravak",
    },
    # --- the unanswered question (the star's need)
    "the_unanswered": {
        "meaning": "the star's question - what will you sing that I could not predict?",
        "notes": [m(45.0, 0.7), m(49.0, 0.7), m(53.0, 0.7), m(58.0, 0.9)],     # deep, rising, open
        "form": "question",
        "learned_from": "pulse",
    },
    "the_answer": {
        "meaning": "the answer - a second voice",
        "notes": [m(58.0, 0.5), m(53.0, 0.5), m(49.0, 0.5), m(45.0, 0.8)],     # completes, resolves
        "form": "statement",
        "learned_from": "pulse",
    },
    # --- the requiem / departure phrase (finale)
    "requiem": {
        "meaning": "we were always here, listening",
        "notes": [m(60.0, 0.5), m(64.0, 0.5), m(67.0, 0.5), m(64.0, 0.5), m(62.0, 0.7)],
        "form": "statement",
        "learned_from": "seravak",
    },
}

# ---------------------------------------------------------------- the characters

CHARACTERS = {
    "seravak": {
        "name": "Seravak",
        "role": "Teacher - a connoisseur of imperfection",
        "color": config.COLOR_ALIEN_A,
        "voice": "seravak",
        "detune": 0.0,
        "bass_hum": True,
        "trust": 0.0,
        "intro": (
            "Seravak does not greet you. Seravak studies you the way a curator studies "
            "a ruined statue - with delight in the breakage. Her first phrase is the "
            "greeting, sung slowly, and she waits to see if you can become it."
        ),
    },
    "ilyan": {
        "name": "Ilyan",
        "role": "The Young - a revolutionary who refuses to grow in tune",
        "color": config.COLOR_ALIEN_B,
        "voice": "ilyan",
        "detune": 6.0,
        "bass_hum": False,
        "trust": 0.0,
        "intro": (
            "Ilyan is small and bright and wrong on purpose. The elders call the youth "
            "'dissonants' as an insult; Ilyan sings it back like a crown. Everything "
            "Ilyan says is slightly sharp - not a flaw, a stance."
        ),
    },
    "thrael": {
        "name": "Thrael",
        "role": "The Negotiator - the despairing faithful",
        "color": config.COLOR_ALIEN_C,
        "voice": "thrael",
        "detune": -14.0,     # THE PERFECT LIE: always sung slightly flat
        "bass_hum": False,
        "trust": 0.0,
        "intro": (
            "Thrael is flawless, and that is the wound. Every official phrase is filed "
            "down to a glass edge - and 14 cents flat, always 14 cents flat, in a way "
            "your ear refuses to believe at first and then cannot stop hearing."
        ),
    },
    "pulse": {
        "name": "The Pulse",
        "role": "The Star - a symbiote, lonely as a mountain",
        "color": config.COLOR_ALIEN_D,
        "voice": "pulse",
        "detune": 0.0,
        "bass_hum": False,
        "trust": 0.0,
        "intro": (
            "There is no face, only the deep blue breathing of the sky itself. The "
            "Pulse does not speak in words - it speaks in a phrase that has been "
            "waiting, unanswered, for a thousand years."
        ),
    },
    # Voss is the human anchor - tracked but not a singing NPC (no voice).
    # The crew does not have trust; they have VOSS_SIGNS tracking (see DESIGN_P3 4.9).
    "voss": {
        "name": "Commander Voss",
        "role": "Captain of the Aria - the human who must learn to hear again",
        "color": (150, 160, 180),
        "voice": "voss",
        "detune": 0.0,
        "bass_hum": False,
        "trust": 0.0,
        "intro": (
            "Voss was a musician once. A war and a loss took his voice, and he built his "
            "life on measurement, not feeling - a defense. He watches you sing with the "
            "look of a man watching something he has forgotten how to do."
        ),
    },
}

# ---------------------------------------------------------------- movements

MOVEMENTS = [
    {
        "id": "m1",
        "title": "A Foreign Kindness",
        "summary": "You wake on the observation deck of the Aria. First contact. Seravak teaches you to Echo.",
        "beats": [
            {
                "who": "seravak",
                "kind": "echo",
                "phrase": "greeting",
                "line": "Repeat me, little broken thing. I want to hear what you do with my shape.",
                "result_ok": "You become the greeting. Seravak's mantle flickers - approval, or hunger.",
                "result_bad": "You mangle it. Seravak does not sigh; she only sings it again, differently, to see you fail prettier.",
            },
            {
                "who": "seravak",
                "kind": "echo",
                "phrase": "you",
                "line": "You. Say 'you'. I need to know if you can point at yourself with your voice.",
                "result_ok": "'You.' It rings true. Seravak hums a fifth beneath - the sound of a being singing with itself, amused.",
                "result_bad": "You sing 'you' as a noise, not a name. Seravak tilts her whole body, pleased anyway.",
            },
        ],
    },
    {
        "id": "m2",
        "title": "The Child's Argument",
        "summary": "Ilyan finds you and teaches you the child's melody - and the question beneath it.",
        "beats": [
            {
                "who": "ilyan",
                "kind": "echo",
                "phrase": "child_melody",
                "line": "Sing it with me! It's mine, I made it, the elders hate it because it's not in tune and that's why it's TRUE.",
                "result_ok": "You sing the child's song together. Ilyan laughs - a bright rising glissando - and the youth choir hums in approval from the dark.",
                "result_bad": "Your version is wrong and Ilyan is DELIGHTED. 'Even you can't make it perfect!' - as if you'd won something.",
            },
            {
                "who": "ilyan",
                "kind": "dialogue",
                "phrase": "are you",
                "response_ok": "i am",
                "line": "Are you... real? Or are you just a very good echo, like the star used to be?",
                "result_ok": "You answer 'I am' and it falls home. Ilyan's glow steadies. 'Good,' Ilyan says. 'Then you can be my argument.'",
                "result_bad": "Your answer is wrong - you sing a question back to a question. Ilyan blinks slowly. 'That's not an answer. That's a mirror. We have enough mirrors.'",
            },
        ],
    },
    {
        "id": "m3",
        "title": "The Perfect Lie",
        "summary": "Thrael opens negotiations. You learn to hear the 14 cents.",
        "beats": [
            {
                "who": "thrael",
                "kind": "echo",
                "phrase": "the_star_is_dying",
                "line": "State our condition, human. Prove you can carry a fact without breaking it.",
                "result_ok": "You reproduce the phrase - including, without knowing it, the flatness. Thrael freezes. You have echoed a wound.",
                "result_bad": "You smooth out the flatness, making it perfect. Thrael's voice blurs - an audible crack. 'You corrected me. Do you know what you corrected?'",
            },
        ],
    },
    {
        "id": "m4",
        "title": "The Unresolved Dissonance",
        "summary": "Ilyan breaks. You hold the silence.",
        "beats": [
            {
                "who": "ilyan",
                "kind": "silence",
                "phrase": None,
                "line": "Ilyan sings the unresolved dissonance and cannot stop. The music dies. There is no score, no timer - only the option to stay.",
                "result_ok": "You stay. In the silence, Ilyan finally sings their true name - a tiny, perfect, dissonant note. You are the first to hear it.",
                "result_bad": "You leave. Later, Ilyan finds you and says nothing, and you understand that some phrases are only ever sung once.",
            },
        ],
    },
    {
        "id": "m5",
        "title": "The False Accusation",
        "summary": "The pulse drops below the line. Thrael accuses you. The star answers.",
        "beats": [
            {
                "who": "thrael",
                "kind": "dialogue",
                "phrase": "the_star_is_dying",
                "response_ok": "the_star_lives",
                "line": "You brought the stillness. Sing your innocence - if you can.",
                "result_ok": "You sing 'the star lives' - the phrase the Pulse gave you - rising from the deep. Thrael's glass edge cracks. 'That is not... that is not our doctrine.'",
                "result_bad": "You sing the accusation back, and Thrael almost weeps with confirmation. But the star answers anyway, and the doctrine dies on its own.",
            },
        ],
    },
    {
        "id": "m6",
        "title": "The Duet",
        "summary": "The finale. The star asks its question. You must answer.",
        "beats": [
            {
                "who": "pulse",
                "kind": "echo_dialogue",
                "phrase": "the_unanswered",
                "response_ok": "the_answer",
                "line": "The Pulse breathes its vast question. The whole choir holds still. Voss hums a broken note into the dark. Now it is your voice.",
                "result_ok": "You sing the answer - not a repetition, a response. The star sings again. The Havari weep because the world is in tune. Thrael thanks you in a single vulnerable phrase.",
                "result_bad": "You falter, and the star's question hangs in the dark - unanswered. Not a failure. A held breath. The choir waits; the game is patient; you may try again.",
            },
        ],
    },
]

# ---------------------------------------------------------------- endings

ENDINGS = {
    "chorus": {
        "title": "The Chorus",
        "text": (
            "You stay. You become a permanent voice in the choir. The last image is you "
            "singing the child's phrase with all of them, on a loop, forever - imperfect, "
            "in tune with each other, exactly as you are."
        ),
    },
    "voyage": {
        "title": "The Voyage",
        "text": (
            "You leave with Voss, but the melody goes with you. The credits play over a "
            "recording of the Aria drifting away, the Havari singing it home. Bittersweet, "
            "gentle - a song ended, a song begun."
        ),
    },
    "silence": {
        "title": "The Silence",
        "text": (
            "The star's question goes unanswered. The ending is quiet. You are left holding "
            "the phrase you chose not to sing - and the game trusts you to know what you did."
        ),
    },
}
