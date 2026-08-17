# GROUND TRUTH — the v4 edit list

Every annotation on the treatment and script v3, enumerated, researched, with a
recommendation. **E** = treatment, **S** = script, **N** = the v4 notes.

Verdict column: **CUT** · **KEEP** · **EMBELLISH** · **ASK** (surfaced as a
dropdown) · **FIXED** (settled by research, no decision needed).

---

## Corrections that research settled

### E3 — "The fire had been started deliberately" · FIXED, and I was wrong

**The fire was accidental.** What was deliberate was the *burning of the tally
sticks*: the Clerk of Works decided the two underfloor stoves beneath the House
of Lords were a proper place to dispose of them, and two workmen fed dry willow
into furnaces designed for coal. Wood burns with a high flame, the copper lining
of the flues melted, a chimney fire started, and it caught the woodwork behind
the panelling.

My sentence reads as though the conflagration was intended. Rewrite to: *the
sticks were burned deliberately; the fire was not.*

**Two gifts from the same research.** The Clerk of Works was named **Cross**, a
convicted criminal who should never have held the post. And Melbourne, the Prime
Minister, called the whole thing **"one of the greatest instances of stupidity
upon record."** Both are quotable and both are free.

### E5 — three sites versus four copies · FIXED. Nothing moved. They are two different programmes

The lists do not match because they are not the same objects.

| | 1845 | 1876 |
|---|---|---|
| what | forty **bronze bars**, precision instruments | **brass strips in stone**, for public use |
| where | Imperial Standard + **four Parliamentary Copies** — Royal Mint, Royal Society, Greenwich Observatory, walled into the New Palace | **three public standards** — Guildhall Great Hall, the Royal Observatory gate, Trafalgar Square north terrace |
| purpose | the definition, and its insurance | so any citizen could check a tradesman |
| indoors? | yes | no, deliberately |

Greenwich is on both lists and they are **different objects at the same
address**: a Parliamentary Copy bar inside the Observatory, and a public
standard by the gate. Nothing was moved. The treatment implies otherwise and
must be corrected.

### ⚠ A source says the Trafalgar plates were re-cut in 1952

This matters, because *"no source states whether the plates are the 1876
originals or recuts"* has been one of our three documented gaps since the start.
One source now says plainly that they were **re-cut in 1952**.

**Needs corroboration before we lean on either version.** If the 1952 recut is
well attested, the gap closes and the honest line becomes *"these are not the
1876 plates; they were re-cut in 1952, and re-cut from what is not stated"* —
which is arguably a better hook, because it moves the question from *are these
original* to *what were they copied from.*

### N3 — Newton cannot have met Smyth or Ray Strachey · FIXED by arithmetic

**Newton died in 1727.** Smyth was born in 1819. Ray Strachey was born in 1887.

The meeting is impossible and would be refuted instantly. **But the fix is
better than the idea.** What all three can share is the *document*: Newton wrote
it, Smyth found it, and a twentieth-century figure found it again. Three people
touching the same object across two centuries is stronger than a meeting,
because it is the only kind of contact the dates permit — and it is exactly how
research actually works.

---

## The geometry — the crossing point, computed

Four sites, in the coordinates used *(all approximate, all need verification —
the Westminster one is a guess, because nobody has told us where in the wall the
Parliamentary Copy sits)*:

```
GREENWICH   Observatory gate standards     51.47790, -0.00140
TRAFALGAR   north terrace standards        51.50850, -0.12810
GUILDHALL   Great Hall standards           51.51550, -0.09220
WESTMINSTER Parliamentary Copy, in wall    51.49950, -0.12470
```

Four points give three ways to pair them into two lines. **Only one pair crosses
between the sites**; the other two cross only if you extend the lines beyond
them, and both land in places with no meaning.

```
                    GUILDHALL
                        ●
   TRAFALGAR    .   ╱      ╲   .
       ●─────────╲╱          ╲
        ╲       ╱ ✕            ╲
         ╲     ╱   ╲             ╲
   WESTMINSTER      ╲              ╲
       ●─────────────╲──────────────●  GREENWICH

   ✕  =  GREENWICH–TRAFALGAR  crossed with  GUILDHALL–WESTMINSTER
         51.50499, -0.11355
```

**The crossing is at 51.50499, -0.11355.** That is in Waterloo, south of the
river:

| | |
|---|---|
| 149 m | the IBM and ITV buildings, Upper Ground |
| 211 m | Royal Festival Hall |
| 212 m | Waterloo Station |
| 221 m | Waterloo Bridge, south end |
| 222 m | National Theatre |
| **832 m** | **Maiden Lane** — the current last stop |

**The geometry is robust.** Moving any one of the four inputs by 100 m moves the
crossing by less than 100 m — Greenwich by 13 m, Guildhall 32 m, Westminster
62 m, Trafalgar 97 m. So the answer will not evaporate when the coordinates are
pinned down properly.

**What it means for the walk.** It is off the route, across the river, and about
a ten-minute walk from Maiden Lane. As a *finisher* that is arguably ideal: it
is a genuine crossing of two real lines between four real objects, it is a
transport hub so people disperse easily, and there is somewhere weatherproof to
sit. As a *route extension* it costs twenty minutes and a bridge.

---

## The treatment edits

| | Edit | Verdict |
|---|---|---|
| **E1** | Cut the light thread everywhere | **CUT — agreed.** It was a second theme in a story that needs one. It costs parts 20, 21 and 23, and the 1983 metre-as-light join |
| **E2** | Ending becomes the line-crossing, location gated | **ASK** — the crossing is computed above and it is in Waterloo |
| **E3** | Was the fire deliberate | **FIXED** above |
| **E4** | Send the thirty-five bars to the conspirators; T3 in the diary | **EMBELLISH — yes, and this is the best invention available.** There is genuinely no register. A bar going to a named recipient is unfalsifiable *and* it explains what the clerk's parish actually had |
| **E5** | Three versus four | **FIXED** above |
| **E6** | Keep Clarke as establishment lead alongside Airy | **ASK** — it fights the record, and the record is what makes him useful |
| **E7** | An artefact Newton left, which Smyth uncovers | **ASK** — chronology fixed above; the question is what the artefact is |
| **E8** | Why did Britain want the meridian, and why not convert | **EMBELLISH — this is now the centre of the story.** See below |
| **E9** | Clarke reappearing via correspondence the clerk witnesses | **EMBELLISH — yes.** He resigned in 1881 and lived until 1914 with no published word. Thirty-three silent years is the largest legitimate gap in the whole cast |
| **E10** | A character glossary at the front | **KEEP — do it.** Sides, dates, what is true, what is invented, and why the invention survives. It also forces the T1/T2/T3 audit to be visible |
| **E11** | A second instance of memory as evidence; and how could anyone challenge a few ppm | **The sharpest objection in the whole list.** See below |
| **E12** | The light section goes | **CUT — agreed** |
| **E13** | Something uncovered in the 1938 move | **EMBELLISH — yes.** A department clearing a building it had occupied for 69 years is a natural discovery point, and 1938 is late enough to reach a living person |
| **E14** | Suppress the 1983 metre-as-light | **CUT the emphasis, keep the fact.** With the light theme gone it becomes a one-line aside, not a payoff |

### E11 is the objection that matters most

*"It doesn't really work with the tiny fraction the yard is off by. How would
the vestry clerk have known? How would anyone have challenged such a small
discrepancy?"*

This is right, and it is the load-bearing problem in the story. Three parts to
the answer.

**1. Nobody could measure it, and that is the point.** A few parts per million
is a few microns over a yard. No parish officer could detect it. No inspector
could. It could only ever be found by *comparing standards against each other*
under controlled conditions — which is precisely, and only, what Clarke's
department at Southampton did.

**2. So the clerk never measures anything. He collects.** He holds a run of
comparison certificates going back decades, each one recording what an inspector
found when the parish yard was checked. He cannot see a discrepancy in any single
certificate. What he can see, over forty years of them, is a **drift** — the
figures moving one way. And Smyth, gathering the same certificates from parishes
all over the country by post, is assembling the only dataset in which such a
thing could show up at all.

**That makes the clerk a node in a survey rather than a witness to a secret**,
which is both more plausible and more useful.

**3. Memory as evidence gets its second instance from this.** The nettles case
works because a boundary is a *place*, and a body can hold a place. A length
cannot be held in a body — and that is the contrast the second instance should
make, not repeat. Suggested shape: an inspector who has compared the same
parish yards for thirty years and *knows by hand* which ones feel short, whose
knowledge dies with him because nobody wrote it down. The rhyme is: the parish
put its boundary into boys so it would survive, and nobody did the equivalent
for the standards.

### E8 — why Greenwich, and why not the metre

The motive question, and it can be answered almost entirely from the record.

**Why Britain wanted Greenwich:** by 1884 roughly three quarters of the world's
shipping tonnage was already using charts reckoned from Greenwich. The meridian
was not a prize being awarded, it was a fact being ratified — and the country
whose observatory defined it sold the charts, the chronometers and the almanac.
*(Needs the tonnage figure verified; it is widely quoted.)*

**Why Britain signed the Metre Convention two weeks earlier:** because signing
cost nothing. It committed Britain to *participate* in the international metric
apparatus, not to *use* metric measure domestically. Britain got a seat at the
table and gave up nothing it cared about.

**Why it then did nothing for eighty years:** the 1895 Select Committee
recommended compulsion within two years, the 1897 Act legalised without
compelling, and the reason is prosaic and documented — industry did not want to
retool.

**Where the invention goes.** Not into any of that. It goes into the single
question none of those documents answers: **why did nobody re-derive the
standards after Clarke's comparisons made it possible?** That is a silence, not
a claim, and silences cannot be refuted.

---

## The script edits

| | Part | Edit | Verdict |
|---|---|---|---|
| **S1** | 2 · Strachey | Make more relevant | **EMBELLISH.** The join already exists and nothing surfaces it: her father-in-law **Richard Strachey sat for Britain at the 1884 meridian conference**, and her husband Oliver was a cryptographer. That is the "brother or something" from note N3 |
| **S2** | 3 · Jewel Tower | Give it a secret; first measurement or first gate | **EMBELLISH.** Best candidate for the **first location gate** — it is the only building on the route where the standards physically lived |
| **S3** | 4 · Cenotaph | Relevant, or cut with Lutyens | **ASK** |
| **S4** | 5 · Mountbatten | Relevant? Does Belsky tie to length at all? | **ASK.** Honest answer: **no.** Belsky ties to *obsolete units being sealed away*, which is thematic, not causal. The Meridian foundry is a coincidence and I have been leaning on it |
| **S5** | 7 · Landseer | In more, or cut | **ASK** — same cluster as the Cenotaph |
| **S6** | 8 · SQUIRE | Keep as a real-world gate; make relevant | **KEEP, and re-purpose.** It cannot be made relevant to measurement. Use it as what it is: a **cord station**. The padlock is a small, reachable, permanent object with letters on it — an ideal anchor |
| **S7** | 9 · Temeraire | Expand; find something on or near the painting | **EMBELLISH** — see N2 |
| **S8** | 10 + 11 | Combine: 35 levels down, then west to 66 | **KEEP — agreed.** It is one physical act and two clues pretending otherwise. *(Note: the brass runs east, not west — confirm direction on the walk)* |
| **S9** | 12 · PERCH | Probably stays; make relevant | **KEEP.** It already is relevant — it is a unit. Only the "water question" reference needs rewording now the fountain is cut |
| **S10** | 13 · Cunningham | Stays for Belsky or goes | **ASK** — with S4 |
| **S11** | 14 · sixpence | As above | **ASK** — with S4 |
| **S12** | 15 · Nelson | More relevant; a note on the ground | **KEEP and EMBELLISH.** It is the thesis in one object. If the cord has a station here, "the number was wrong for 150 years" becomes something they check rather than read |
| **S13** | 16 · Newton | Keep; make Newton more relevant | **EMBELLISH** — with E7 |
| **S14** | 17 · boundary mark | Keep if a real secret makes it work | **KEEP as collect mode** until somebody walks it. Every team's answer is field data we do not have |
| **S15** | 18 · St Martin's window | Random; make relevant or cut | **CUT the window, KEEP the church.** The window was carrying the light theme, which is gone. The church matters because of the vestry and the parish yard — so the clue should be about the parish, not the glass. Needs a new target found on site |
| **S16** | 19 · Fogg / Verne | Should Verne be more prominent | **KEEP, do not promote.** He is the cleanest way to state the meridian problem in one sentence, and promoting a novelist to the cast dilutes a story whose whole strength is that the people are real |
| **S17** | 20 · pavement light | Goes | **CUT — agreed** |
| **S18** | 21 · Goodwin's Court | Goes | **CUT — agreed** |
| **S19** | 22 · Voltaire | How is it relevant? Was he stabbed for scepticism? | **See below** |
| **S20** | 23 · electricity | Goes, saved for a later quest | **CUT — agreed** |

### S19 — Voltaire, and a correction worth having

**Voltaire was not stabbed.** He was **beaten** — in Paris in 1726, by servants
of the Chevalier de Rohan, after an exchange of insults. He was then briefly
imprisoned in the Bastille and released on condition he leave the country.

**That is why he was in London at all**, and it is far better than anything we
could invent: a man beaten by an aristocrat's hired men for being insolent to
his betters, who came to England and wrote admiringly about a country where a
merchant's son could be respected.

It is also **the third beating in the story.** Boys beaten at boundary marks so
a measurement would survive. Voltaire beaten out of France for insolence.
Smyth's reputation beaten out of the Royal Society for the same offence in
different clothes.

**So Voltaire stays, and stops being trivia.** No invention required. And the
person who was stabbed at the stage door — William Terriss, 1897 — is a separate
fact and should probably be cut from the clue to stop it muddying the beat.

### N2 — Turner, and how far to go

The request is for something hidden in a painting. **This is the riskiest thing
proposed in the whole edit list**, and it needs stating plainly: Turner's
catalogue is one of the most heavily studied bodies of work in British art. Every
canvas has been x-rayed, every sketchbook is at Tate Britain and digitised.
**A claim that something is concealed in a specific painting is refutable in an
afternoon.**

The rule that has held all the way through applies exactly here: *an
interpretation cannot be refuted; a claim about the record can.* So the safe and
strong version is not *he hid a mark in the canvas.* It is **what he chose to
draw, and what he chose not to.**

He was on the river with a sketchbook and no colours. The two sketchbooks are
real, catalogued and viewable. Whatever is or is not in them is a matter of
looking — and the *reading* of why a man draws the water instead of the building
is ours for free, and nobody can take it away.

**Recommendation: no concealed object. Instead, a Turner sketch or canvas
becomes a cord station in the National Gallery or on the route**, and the
explainer does the interpretive work. See the dropdown.
