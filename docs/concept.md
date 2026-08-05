# Fedora — concept & research synthesis

*Compiled 5 Aug 2026 from a three-track research sweep: (1) digital
location-based games, (2) analog/historical real-world games and ARGs,
(3) AI-proof puzzle design + video-game mechanics. Sources at the end.*

## The pitch

An educational treasure hunt through a real city — Da Vinci Code × National
Treasure × Indiana Jones. Teams solve a crossword whose answers are only
discoverable by physically going somewhere: the clue tells you where to stand
and what to look at; the thing you observe *is* the answer. Solving a word
unlocks the next clue; the grid's shaded squares assemble into the location of
the finish — a pub. First team there wins.

## What already exists (and what it teaches)

**Digital.** Pokémon GO proved synchronized real-world events drive mass
engagement; Ingress proved forced competition scares off casuals. Zombies, Run!
proved serialized narrative is the retention engine. Randonautica proved novelty
without authored content dies in months. The closest commercial relatives are
**Secret City Trails** (browser-only riddle chains, correct answer unlocks the
next stop, hint = +10 min penalty, time-based leaderboard — proof the pure
web-app model works commercially), **CityDays** (two-part clues: cryptic
navigation + on-site observation, scheduled pub stops, "like cracking the Da
Vinci Code" reviews), and **HiddenCity** (clues by SMS, pre-briefed venue staff
hand teams physical props). ClueKeeper/DASH contribute the event-race toolkit:
start codes, par-time scoring, skip-for-zero, and an unscored first puzzle
purely to stagger the field. Watson Adventures rebuilt their app because players
read answers out of the HTML — **answers must never reach the client**, which is
Fedora's core architecture.

**Analog & ARG.** Masquerade (1979) invented the national-obsession treasure
hunt and its failure modes (trespass, digging, an insider-leak scandal that
poisoned the genre). Letterboxing (Dartmoor, since 1854) contributes the
stamp-as-proof-of-visit and logbook-as-community. Orienteering contributes
bearing-and-pace-count legs. ARGs (I Love Bees' ringing payphones, Year Zero's
USB drops and staged rally, Jejune Institute's self-guided city game with live
garnish) contribute the drip-feed, the in-fiction phone number, and the
scheduled live moment — someone waving a flag from a window at 3pm is a
century-old genre with a modern name. Pre-briefed pub staff handing over an
envelope on a codeword is the cheapest live magic available.

**London specifically** is crowded at the low end (Treasure Trails booklets,
generic app hunts) and the premium end (HiddenCity, A Door in a Wall), but
**nobody combines crossword-grade authored clues + on-site-only answers + team
racing + a narrative pub finale in a free-to-start web app**. That's the gap.

## The core design bet: AI-resistant, human-quick

The game only works if a team at home with ChatGPT cannot out-race a team on
the street. Research says this is achievable but the failure modes are
specific:

**Design rules (the checklist):**

1. Ask for **relations or counts, never names**. Which painting hangs three
   frames left of X is not indexed; what the plaque says is.
2. **Never make an inscription on a named/notable object the answer** — London
   Remembers, OpenPlaques and OpenBenches (~43k benches!) have transcribed
   effectively all of it.
3. **Counts of unremarkable features** (railings, steps, tiles, lamps) are
   strong: no database holds them and vision models are measurably bad at
   counting (VLMCountBench: ~0.60 accuracy on *clean* images).
4. **Sightlines and stances**: "stand on X, what does Y point at" defeats
   Street View's car-height, path-bound, frozen coverage.
5. **Ephemeral content** (chalkboards, temporary notices, current exhibition
   labels) is unindexable by construction — but needs re-verification before
   game day.
6. **Compose across sites**: make an answer a function of observations at two
   places; even if each half leaks, the composition doesn't.
7. Museum interiors: Google's virtual tours cover e.g. every National Gallery
   room, but as a **frozen snapshot** that rehangs invalidate — usable, but
   verify the target is post-snapshot or off the tour path. This cuts both
   ways: **your own clues rot on the same schedule**; every clue needs a
   ground-truth photo and a re-check date.
8. "Identify this place from a photo/description" has **zero AI resistance**
   (o3-class geolocation is near-superhuman). Location-finding can be a fun
   light puzzle, but never the gate — the gate is what you do on arrival.
9. On-site answers are low-entropy, so **rate-limit guesses server-side**
   (Fedora: 15s per clue per team) and never ship answers to the client.
10. GPS is **friction, not proof** — browser geolocation is trivially
    spoofed. Presence-proof is the observed value itself, or a code
    physically posted at the site (the Encounter model).
11. Answers **will** be shared between teams in a recurring game — rotate
    per-team/per-day variables (which letter to extract, day-codes) so a
    shared answer rots. (Geocaching's unsolved problem.)
12. Keep the on-site action under ~60 seconds. Difficulty belongs in finding
    the spot and knowing what to look at, not in on-site puzzling — that's
    also what keeps the AI-shaped work (deduction) separate from the
    human-shaped work (being there, looking).

**Failure modes from 45 years of treasure hunts:** difficulty miscalibration
with no feedback loop (The Secret: 9 of 12 caskets unfound after 44 years) —
so playtest cold and have a hint escalation path; physical danger and property
damage (Masquerade's nationwide digging, Fenn's five deaths) — nothing buried,
nothing at height, everything resolvable by looking; insider leaks destroying
trust (the Masquerade scandal) — minimize who holds solutions.

## Feature roadmap, ordered by ease of realisation

**v0 — this PoC (build now).** 7-word crossword hunt in central London.
Browser app, no install. Team join codes. Server-checked answers (Supabase
RPC), progressive clue reveal, some clues open from the start (multiple entry
points), guess cooldown, live leaderboard, shaded-square meta puzzle naming
the finish pub. All content hand-authored and field-verified once.

**v0.5 — trivial additions after one playtest.** Tiered hint ladder with time
penalties (never hard-stuck — the single most praised mechanic in commercial
hunts); Wordle-style spoiler-free share grid; per-leg split times on the
finish screen.

**v1 — event polish (still just code).** Timed clue releases (schema already
supports `available_from`); staggered starts DASH-style (unscored stagger
puzzle); par times with skip-for-zero; multiple parallel hunts (schema
already keyed by `hunt_id`); post-game answer-reveal page.

**v1.5 — first physical infrastructure (SETUP, no staff).** Printed
QR/code-word labels at 1–2 locations as hard presence proof; a pre-briefed
barman at the finish handing the winners' envelope on a codeword; an
in-fiction phone number (cheap voicemail) that plays a recorded clue;
per-team letter-extraction variants to rot shared answers.

**v2 — live-orchestrated events (needs people on the day).** The
flag-from-a-window moment at a stated time; a roaming "rival" (Journey to the
End of the Night chase pressure); actors at one stop (A Door in a Wall
model); monthly cadence once there's a following.

**v3 — platform ambitions (real engineering).** Camera integration and photo
challenges with review; soft GPS confirmation UX; fog-of-war map; serialized
narrative across monthly episodes (Zombies, Run! retention model); authoring
tools for other cities (Wherigo's lesson: the platform lives or dies on
creator-tool friction); pub/venue partnership revenue.

## Sources

Full source lists with URLs are in the three research reports this file
condenses; headline references: Secret City Trails/CityDays/HiddenCity/Questo
product docs and reviews; ClueKeeper + DASH players' guides; puzzled pint &
MIT Mystery Hunt writing guides; Watson Adventures' cheating post-mortem;
London Remembers / OpenPlaques / OpenBenches coverage; VLMCountBench (arXiv
2510.04401); PIGEON geolocation (NPR); Niantic anti-spoofing (Schneier);
Digital Antiquarian on Masquerade; Atlas Quest letterboxing history; I Love
Bees / Year Zero / Jejune Institute retrospectives; Fire Hazard's Citydash;
Encounter (en.cx) codes-at-location model.
