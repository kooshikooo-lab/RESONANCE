# RESONANCE — Design Bible (Part 5: Craft Laws, Multiplayer, Social World)

---

## 9. Permanent Craft Laws (these are enforced, not aspirational)

> Added at the direction of the creator, night-before-build session. Every scene, NPC,
> system, and sentence in this game obeys these. They are the constitution.

### 9.1 No cheap plot devices

A "cheap plot device" is anything that moves the story *because the author needed it to*,
rather than because the world naturally produced it. Forbidden devices, with our
substitutes:

- **FORBIDDEN — the MacGuffin.** Nothing exists only to be fetched. The star is not a
  treasure; the phrase is not a key; the answer is not a thing you "collect." Every
  object in the game is a *person's* object, or a *moment's* residue. (The one object
  that returns across the whole game — the child's phrase — is a melody, and its only
  power is that it is *shared.*)
- **FORBIDDEN — deus ex machina / convenient arrivals.** Nobody shows up at the last
  second to save the plot. The Pulse is foreshadowed from Movement I (the background
  star *breathes* from the very first frame; the soundtrack hums its chord before the
  player can name it). Seravak's revelation is built from five earlier "mistake" lessons.
  Thrael's confession is telegraphed by 14 cents of flatness in every prior scene.
- **FORBORUN — plot-convenient stupidity.** No character withholds information only
  because the plot needs a mystery. When Thrael hides the doctrine, she hides it the way
  a person hides a wound — visibly, in her tuning, in her avoidance. When Ilyan hides
  their fear, they hide it behind *louder* singing, which is its own tell. The player is
  always given the information to *understand before* the characters say it — and the
  drama is the character finally *admitting* what the player already heard.
- **FORBIDDEN — the reveal that doesn't pay off.** Every secret has a cost already paid
  by the character before we meet them. Seravak's dead family line: she has been singing
  alone-in-chords for centuries *before* the game starts; we meet her already paying.
  Thrael's grief-ritual: a lifetime. Ilyan's resolved dissonance: an injury. Reveals are
  bill-collection, not reveals.

### 9.2 No cardboard characters — including NPCs

Everyone who speaks has:
1. **A before-now.** One line of biography that happened *before the player arrived.*
   The youth choir isn't "the youth choir" — it's a dozen named dissonants, each with a
   why. (See §10.5.)
2. **A private want they will not voice.** Not a *secret plot* — a private want. Thrael
   wants the doctrine to be true so her vigil wasn't wasted. Ilyan wants to be allowed to
   stay dissonant without being *alone.* Seravak wants to sing with someone and is
   terrified of being wrong about it.
3. **A flaw that is also their strength.** (The design's one honest cliche — it's how
   humans are.) Seravak's connoisseurship is her detachment *and* her tenderness. Ilyan's
   refusal-to-grow is rebellion *and* cowardice. Thrael's exactness is her wall *and* her
   faith.
4. **A sound.** Even the choir members have a sung fragment, however small, so the
   player *hears* them as individuals before seeing them as types.
5. **A capacity to surprise.** No character is a function. Seravak laughs. Ilyan is
   sometimes gentle. Thrael is sometimes wrong. The Pulse is sometimes *silly* — its slow
   low phrase occasionally answers a children's question with a children's answer, and it
   has no one else to be silly with.

### 9.3 NPC background stories (the choir, the crew)

- **The dissonant youth choir:** named, each with a reason for refusing consonance —
  Baer, whose family is a perfect choir and who sings off-tune out of suffocation;
  Veth, who heard the star's unanswered question as a child and has been trying to
  reproduce it ever since; old-man-thought-to-be-broken Chael, who was once the strictest
  teacher in the orthodoxy and who defected in old age because "perfection ate my
  wife's laughter." The choir is a *place,* not a crowd.
- **The Aria's crew:** Commander Voss (see 4.9) and two silent others — Dr. Nnamdi,
  the ship's xenobiologist who is quietly in love with the sound of a species she can't
  dissect, and who leaves cassette tapes of whale-song in the observation bay because
  "they should hear something that comes from our oceans"; and Osen, the pilot, who
  hums a completely different tune every time you pass him, because he's testing whether
  any human will notice, and only the player's character ever does. Both speak rarely;
  both have lives.

---

## 10. Multiplayer & Social World

> Question researched per creator request. This section is **options and a
> recommendation**, not a commitment. Resonance's single-player soul is non-negotiable;
> multiplayer must *deepen* that soul or it doesn't ship.

### 10.1 What the research says (2026, the landscape)

- **Pure-Python + pygame networking is mature enough.** Standard options:
  - **WebSockets (`websockets` + `asyncio`):** the cleanest fit for our stack. Full-duplex,
    TCP (reliable), trivial JSON, great for a small lobby game. Server can be a normal
    Python script; host runs both server+client ("one app runs it all").
  - **UDP libraries (pygase, mpgameserver, MultiplayerLib):** lower latency, better for
    twitch action; overkill for us because our network payload is *melodies* (a few
    floats per phrase), not continuous state. 45 KB/s at 32 datagrams/s is orders of
    magnitude more than we need.
  - **Pygase** (asyncio UDP, client-server, synchronized state) — the most polished
    option if we ever need real-time shared state.
- **The singing-game precedent (Vocaluxe, UltraStar Play, FHNW collab):** proven social
  patterns that resonate with Resonance:
  - **Co-op Duet / Co-op scoring** — singing *together* scores as one.
  - **Pass-the-mic** — one mic, alternating players; builds a social rhythm.
  - **Phone-as-mic companion app** — UltraStar Play uses phones as mics; lowers
    hardware barrier. (For us: a phone mic would stream audio to the host PC for RMVPE —
    doable, moderate effort.)
  - **Per-player calibration** — each voice's pitch range measured first, so a low
    baritone and a high soprano are scored fairly. *Directly applicable* to our Dialogue
    scoring.
  - **Harmony rewarded with animation** — when two voices agree, the world responds
    visibly. *This is already our core visual metaphor* (the ribbon merging).
- **Architectural truth for us:** our bottleneck is **local pitch analysis (RMVPE on the
  host), not networking.** Players should *send sung-phrase events* (melody as notes),
  not raw audio. Analysis stays local → latency-free scoring, tiny bandwidth.

### 10.2 Thematic fit — multiplayer as "the choir"

Single-player Resonance teaches: *imperfection is the source of meaning.* Multiplayer
extends it literally: **the star cannot be answered by one voice — it needs a chord.**
This is not bolted on; it is the game's thesis made social. Two humans, each imperfect
alone, sing complementary phrases, and the *combination* is what the alien hears.

### 10.3 Multiplayer modes (ranked by fit → to → ambition)

**TIER 1 — Local co-op (recommended first; zero networking)**
- **"The Choir" (co-op duet, pass-the-mic):** two players alternate Echo phrases toward
  one NPC. The NPC's phrase is split; each player sings half; both must be accurate for
  the NPC to *finish.* Scores both, rewards harmony. Same keyboard, one mic passed, or
  two mics (second mic = config option).
- **"The Duet" (2-player dialogue):** one player sings the *question* (the NPC's form),
  the other sings the *answer.* The NPC judges the pair as a unit. Directly enacts
  Movement VI's "not a repetition, a response."

**TIER 2 — LAN/online small party (WebSockets, 2–6 players)**
- **"The Garden" (shared hub):** players occupy the same observation deck. Each player's
  alien is a distinct light. Singing adds *your* ribbon to a shared sky; the collective
  harmony meter rises; when it crests, the Pulse brightens for everyone. No score — it's
  the Chambers "boring scene," socialized: players can just *be together* in the music.
- **"The Round" (pass-the-mic online):** one shared phrase, players pass it around the
  net; each reproduction errors slightly (measured), and the *accumulated* drift becomes
  the melody's "memory" — a living game of telephone that the Havari would understand
  (memory IS melodic; error is part of the song).

**TIER 3 — Persistent social world (ambition, later)**
- **"The Choir That Remembers" (async, persistent):** the star's pulse is a *global*
  value. Every player's successful finale-answer contributes one sung phrase to a shared
  "wall of voices." New players hear faint fragments of past players' melodies echoing in
  the background of the hub — real recordings (analysis events) from real strangers.
  Thematic home run: **the game IS the Havari archive — a choir that sings the past.**
- **"The Gift" (async):** a player may *leave* a phrase (recorded via analysis) for a
  friend to find in a corner of the hub. Unlocking it plays the melody back and names
  the giver. The first "object" in the game that is purely a *shared sound.*
- **Lineage (async):** players who duet repeatedly form a "lineage chord" — a shared
  harmonic identity (their two voices together), rendered in the hub as a two-note
  glyph. Mirrors Seravak's dead family chord: friendship *as* music.

### 10.4 Social world principles (how people relate)

1. **Voice is identity.** Player name is chosen once; but their *identity* is their
   singing profile (pitch range, preferred key, vibrato signature, average fidelity
   band). Other players "recognize" you by your sound, not your name. (Deterministic
   from analysis; no privacy leak — only derived features are shared.)
2. **Harmony is cooperation; dissonance is not hostility.** In a shared space, two
   voices singing apart is just *two songs.* The social currency is *attunement* —
   players who sing in the same key drift into a shared light. No combat, no griefing;
   the worst social act is *ignoring someone's song.* (Design law: multiplayer has no
   PvP. The aliens' only taboo — silence — is the only offense, and it's passive.)
3. **Solo is always valid.** Every social feature has a solo equivalent. No content is
   locked behind having friends. Multiplayer is an *instrument,* not a gate.
4. **The social world serves the story.** The persistent choir's effect is *felt* as a
   change in the sky and the Pulse's breathing, not as a leaderboard. The final beat of
   the game (the Duet) can be done solo — or, if you have ever sung with someone, you
   hear your shared lineage chord as the star answers. Memory, as with the Havari, is
   the accumulated music.

### 10.5 Technical recommendation (if pursued)

- **Start:** Tier 1 local co-op (two-mic support + pass-the-mic), because it proves the
  *design* (duet as one voice) with zero networking risk.
- **Next:** Tier 2 WebSockets lobby (asyncio server embedded in the host app; client
  talks JSON melody events; 2–6 players; authoritative-ish server for phrase state).
- **Never:** raw audio streaming over the net; all analysis stays local, phrase events
  travel.
- **Capacity math:** ~50 bytes per sung phrase event at a few events/second → trivial
  for any connection. The hard problem is UX (lobby, mics, calibration), not bandwidth.

---

## 11. Addendum — what "social" means when it ships

Resonance ships single-player first. The social layer is **a mode, not a genre**: a
quiet space where the game's thesis ("imperfection shared is meaning") is experienced
with another person. The hub's social scene is designed so that a player who never
touches multiplayer misses *none* of the story — and a player who does feels the story
in a new register: the star, at the end, is answered by *your* voice and *theirs,*
together. That is the entire point. Good night. Go make them sing.
