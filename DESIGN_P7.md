# RESONANCE - DESIGN_P7: The Outpost - a young world, a young crowd

> "Everyone is a little bit thrilled to be here, and no one has unpacked properly."

Tone: **light, warm, often funny; serious only when it needs to be.** This is the
diplomatic outpost on the frontier world under Proxima - brand new, prefab, and
already crowded with emissary crews from a dozen species. It is not an ancient
capital. It is a campus. It smells like fresh paint and curiosity.

## 1. The world

- The planet is **newly inhabited** - a diplomatic outpost, not a homeland. A few
  hab-domes, a landing field, string lights, and a lot of hope, set down on the
  twilight valley floor.
- **The star is Proxima**, the dim red dwarf - its light is always a little
  rusty, a little sleepy. The Havari have lived here longest, but the outpost
  itself is young and shared.
- People have just **travelled here to meet each other**. Ships blink on the pads.
  The plaza is full of beings who have never met a member of another species
  before this season.

## 2. Who is here (the crowd is not a monolith)

Emissary crews are not all diplomats. Everyone who came has a role, and the roles
matter. When the player looks out at the outpost, they should see a real society:

- **The diplomats** - the ones who talk, negotiate, and sign things. Usually
  formal, often nervous about doing it wrong. The visible face of a crew.
- **The support crew** - engineers, medics, pilots, cooks, linguists, technicians.
  They keep the outpost and the ships running. They are the majority, and they
  gossip in every species' equivalent of a break room.
- **The families** - diplomats and support crew alike brought people: partners,
  children, grandparents, and found-family. Children chase each other between the
  habs. Someone has planted a garden that has nothing to do with the mission.
- **The hangers-on** - students, artists, translators, the curious. People who
  came because this was the one chance to see another sky. Some are brilliant;
  some are just eager. Both are welcome.

The player's own crew - the Aria's people - arrived the same way: a few diplomats,
a lot of support, and families who are doing their best to feel at home on a
world that just got here.

## 3. Why this matters for the story

- **The outpost is a place, not a stage.** Diplomacy is not a clean table; it is
  kids running past it, an engineer fixing a light mid-negotiation, a parent
  humming a lullaby in the hall. The Havari are not the only aliens here - they
  are the oldest residents of a brand-new town, which changes how they behave.
- **The Havari among the crowd.** A species that has been alone for so long now
  finds itself sharing a valley. How they handle *other* aliens - the loud ones,
  the fast ones, the ones who keep things - is a window into who they are.
- **Most characters are young.** The outpost skews toward the young and the
  hopeful - which is exactly right, because this story is about learning to be
  imperfect together before you've had time to harden.

## 4. Visual notes (procedural, no assets)

- Prefab **hab-domes and modules**, warm windows breathing, string lights strung
  between poles by someone's first attempt at decoration.
- **Landing field** with small emissary shuttles on pads, nav lights blinking.
- **Native flora** planted in beds between the habs - the new residents keeping
  the old world's plants close.
- **The crowd**: small figures of several species wandering the plaza - a diplomat
  pair in quiet conference, a tech with a toolkit, a child chasing a light. See
  `graphics.py::EmissaryNPC`.

## 5. The cast (who stands out in the crowd)

The main characters keep their individual shapes (see DESIGN_P6) but now they
exist *inside* this young, crowded world:

- **Seravak** - teacher first, and only secondarily anyone's diplomat. She is here
  the way a curator is here for an exhibition opening: delighted, collecting.
- **Ilyan** - came with the youth delegation. The outpost is the best thing that
  ever happened to a young revolutionary - finally, *other* young beings to be
  wrong with.
- **Thrael** - the actual diplomat of the Havari crew. Formal, exhausted, carrying
  the weight of representing a people who have never had to represent themselves.
- **The Pulse** - not a person at the outpost; the sky it hangs under. But the
  outpost is the first place where other beings have *seen* Proxima as a home
  rather than a threat, and it does not know what to make of them.
- **The Aria's crew** - Voss, Nnamdi, Osen, and the rest (DESIGN_P6) are the human
  side of this same mix: a few diplomats, a lot of support, a family that chose
  to come along.

## 6. Open questions (visuals first)

1. How many distinct species should be visibly at the outpost? (The EmissaryNPC
   silhouettes currently include: slim, round, quad, float - enough to feel
   crowded without a species bible.)
2. Should the player's own shuttle be visibly theirs on the pad?
3. Where does the "campus" feel most matter - the plaza, the landing field, the
   hab interiors?
