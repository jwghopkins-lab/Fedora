# GROUND TRUTH — the cord, and the key mechanic

Phase 6. How the marked cord actually works, what it can and cannot do, and
the one thing about it that has to change.

---

## The problem, stated plainly

D2 locked the defect at **a few parts per million** — that correction was
necessary, because Smyth's claimed thousandth is a thousand ppm and would have
been caught in a week, where single-digit ppm plausibly survives seventy years.

D3 locked a **marked cord** as the machine-proof channel.
D7 locked **their own measurement** as the payoff.

Those three cannot all mean what they appear to. **A few ppm over a yard is a
few microns.** It is smaller than the thickness of the mark you would draw to
show it, smaller than the cord's stretch under hand tension, smaller than the
change in the cord's own length between a cold morning and a warm afternoon.
Over the terrace's full hundred-foot run the signal is still under a
millimetre, while the error budget of ten people stepping a cord along brass in
the wind is inches.

**The cord cannot show the discrepancy. No cord can.** If we script a
measurement that is supposed to come out at a particular number, it will not,
and the game breaks in public on the first outing.

I considered the escapes and none of them survive. A *pyramid* yard — Taylor's
inch is about 1.00106 British inches — accumulates roughly 1¼ inches over a
hundred feet, which sounds measurable until you notice that stepping a
ten-foot cord ten times accumulates hand error faster than it accumulates
signal. Checking the plates against *each other* for internal inconsistency
would be lovely, and is the documented gap we already own, but we would be
scripting a result we have not verified on the ground and cannot guarantee.

---

## What the cord does instead

It stops being a measuring instrument and becomes **a key**. This costs us
nothing, because the thing that made it valuable was never the precision — it
was that it is a length that exists only as an object, recoverable at 0% by any
machine.

### The mechanic *(client's design, 15 Aug — supersedes the page/line/word version)*

The cord is a **pointer**, not a ruler. The diary names a knot and an anchor.
You put the cord's zero on the anchor, pull it straight, and the named knot
lands on **one letter, digit or feature of a real inscription**. One character
per location; across the walk they spell the word.

**This is better than what it replaces, and for a reason that matters.** The
old design read page/line/word out of the diary, which put the payload inside
our own invented document. This puts it on the pavement. Under the structural
law — fiction may be an edge, only fact may be a node — the answer now lives on
a real object that was cut by somebody else for their own reasons, and the
diary demotes to what it should always have been: **the reference book that
tells you which knot and where to stand.**

### Why a cord beats a stencil — the instinct is right, and here is why

A stencil is two-dimensional, and two dimensions survive photography. Shoot the
inscription, print the stencil at any size, slide it until the registration
marks line up, read the answer. Scale is not needed because *shape* carries the
information.

A cord is one-dimensional and carries exactly **one absolute distance**. A
photograph does not contain absolute distance. That is the entire difference.

### The bigger cheat vector, which is proportion

There is an attack that beats a naive cord, and it is worse than the stencil
one because it needs nothing but a photograph.

**If the cord is laid end-to-end along the target** — zero at the left edge of
the inscription, cord roughly as long as the inscription — then the knot sits
at a *fraction* of the way along. A fraction is recoverable from any photograph
of any size. "The blue knot is a third of the way across" and the cord is
decoration.

**So the cord must never be aligned to the target's own extent.**

### The fix: anchor and offset

- The cord's zero goes on a **named physical point** — a bolt head, the corner
  of a kerbstone, the foot of a particular letter, a fixing in the ironwork.
- The knot falls at a distance with **no relationship to the target's
  dimensions**, so there is no ratio to recover.
- **Best of all: anchor on one object and land on another.** Zero on the kerb,
  knot on the plaque. No single photograph contains both at a known scale and
  there is no fraction to extract. This is the version to reach for.

That is the difference between a puzzle a photograph solves and one it cannot.

### The attack that beats anchor-and-offset, and what to do about it

*(raised by the client, 15 Aug)* Measure the cord with a ruler before you set
off — zero to blue, blue to green — feed those numbers to a model with
photographs of the targets, and read the answers off a screen.

**It works, and it should be assumed to work.** The only thing standing between
the model and the answer is *scale on the photograph*, and scale is recoverable
from a street scene by more routes than we can close: a standard brick is
215 mm, paving and kerbs are standard, doors and people are known, several of
these monuments have published dimensions, and a confederate can simply hold a
tape in frame.

**But look at what the attacker had to do first: hold the cord.** The cord is
handed over in person at the start. So this is not a sofa attack, it is a
*café* attack — somebody who has already collected the prop and begun the walk,
solving the back half indoors. That is a far smaller failure, and the cord's
real job, which it does unconditionally, is to make possession of a physical
object necessary. There is also plain effort asymmetry: measuring, photographing,
rectifying and modelling costs more than walking twenty yards and holding a
piece of string against a plaque. This is a game, not a vault.

### The two-hop traverse *(client's fix — adopted)*

Instead of one absolute offset from an anchor, use **the span between two
knots** and walk it across the object in two hops: from the bottom-left corner
up to a letter, then from that letter down and right into another. Dividers,
not a ruler. **Direction unstated** — you sweep until it sits.

Three reasons this is stronger than it looks:

1. **Error compounds across hops.** A 2% scale error on a photograph is 2% of
   one span; chain two and the second hop begins from an already-wrong origin.
   On site there is no scale error at all, because the cord *is* the scale.
2. **Unstated direction makes the search underdetermined.** A model must sweep
   a two-dimensional angle space from each anchor and will surface several
   plausible landings with no way to rank them. A person on site gets a
   confirmation the model does not: the knot sits *dead centre* on a letter and
   it feels right. That click is a strong signal in the world and a weak one in
   a rectified photograph.
3. **The second hop self-verifies.** Get hop one wrong and hop two lands on
   nothing sensible. A free integrity check for the player; a compounding
   penalty for the attacker.

### Two further defences, one of them better than all of the above

- **Go round a corner.** A cord follows an edge; a photograph flattens it.
  Anchor on one face, run the cord round the arris onto the adjacent face. No
  single photograph sees both faces at once or measures the wrap. It is
  effortless with string, near-unrecoverable from imagery — and it is literally
  what a perambulation cord does, which is that it goes round things.
- **Mix planes.** Anchor at pavement level, land on a wall. Foreshortening
  wrecks mixed horizontal/vertical recovery and costs the player nothing.
- **And the cheapest: never print a number.** The diary names colours, never
  distances. The numbers exist only on the cord, and the only way to have them
  is to have it.

### The oracle, and why it is safe

Players type a letter and the app says yes or no, which also helps a
brute-forcer — 26 letters is not many. **The guess limit is what closes this**:
three lives per part, each hint buying one back. Already built, and it is now
load-bearing for the cord's security as well as for pacing.

### The cost to watch

Direction-free sweeping is delightful at ninety seconds and miserable at
fifteen minutes. Mitigate by giving a *sense* of direction without the angle —
*"upward, and to the left of where you are standing"* — and by making every
landing unmistakable: the centre of a letter, a full stop, a bolt head. Never
"somewhere near".

### Knots, not dots

Coloured thread whipped at a knot. Tactile, unambiguous, cannot rub off,
survives rain and pockets, and colour-codes without ink. *"The blue knot"* also
sits better in a Victorian hand than *"the blue dot"*.

### One cord, many knots

Several knots, each used once, each at a different location. The cord becomes a
key ring rather than a single-use token, the prop is amortised across the walk,
and the cumulative letters give the day a spine. It also raises the stakes on
losing it, which is why the fallback below is not optional.

### The distances are discovered, not designed

Exactly as put: you go to the thing, you lay a tape on it, and whatever the
number turns out to be is the number. **The cord cannot be derived from any
document, because it did not exist in any document before somebody measured
it.** That is the whole security argument in one sentence, and it is also why
the terrace measurement in `FIELDWORK.md` gates the physical build.

### The theme fits better than we could have arranged

**Beating the bounds.** The parish perambulation: once a year the clergy and
the parish walk the boundary and strike the marks so that everyone remembers
where it runs. **St Martin-in-the-Fields still does it.**

And St Paul's Covent Garden was a chapelry carved out of St Martin's parish in
1646, whose boundary was defined as **"40 foote without the ... bricke wall"** —
a parish boundary specified as a distance.

The players walk out of St Martin's and into Covent Garden. They cross a
boundary that was fixed by a measurement, carrying a cord, transferring lengths
from one place to another — which is what a surveyor's chain does and what a
perambulation was. **The cord is the clerk's perambulation cord**, and nothing
about that has to be invented.

### Rules for use, which go in the diary in the clerk's voice

- **Never touch the monument.** The cord is held near the surface, never
  pressed against it and never drawn along it. Listed fabric. Written as period
  propriety rather than as a safety notice, it reads as character.
- **Reachable targets only.** Nothing above head height.
- **Short spans** — under about two metres, so sag and stretch are irrelevant
  with braided line.
- **Nothing spanning a road, a barrier or a queue.**
- **Anchors must be permanent and unambiguous** — not a paving joint that gets
  relaid, not a bollard that gets moved.

---

## The planted errors *(D3)*

One or two, and they belong in **the researcher's marginalia**, not on the cord
and not in the clerk's hand.

- **On the cord** an error is unrecoverable — a knot in the wrong place gives a
  wrong letter and no way to tell. The cord must be perfect.
- **In the clerk's hand** an error undermines the one voice that has to be
  trustworthy.
- **In the margin** an error is *characterful*. A modern researcher who
  miscounts a line, or writes "p.14?" with a question mark and is wrong, is a
  person under pressure — and the moment a team notices the margin is wrong and
  the book is right is the moment they stop reading and start working.

So the marginalia gets **one confident wrong reference and one hedged right
one** — it says *blue* where it should say *green*. A wrong knot yields a
near-miss letter and a word that almost works, which is recoverable, because
the right knot is still sitting on the cord.

---

## Production consequences

| | |
|---|---|
| **The cord** | Knot positions must be set against the actual brass, on site, with a tape. They cannot be calculated from a plan — the 2003 rebuild moved the plates east and no drawing we can get is authoritative. **This is a field job before any cord is cut.** |
| **Non-stretch** | Braided polyester or linen line, not cotton and not elastic. Cheap, and it removes the one variable that could still bite. |
| **Spares** | One cord per team plus two. A lost cord is a dead hunt with no recovery path. |
| **The diary** | It no longer encodes pages, so pagination stops gating the cord. But it carries every knot reference and every anchor, so **the field measurements come first and the diary's references are written from them.** Field, then cord, then diary. |
| **Anchors** | Each one photographed and described unambiguously enough that a stranger finds it in the dark. This is where a walk goes wrong — not the knot, the anchor. |
| **A fallback** | If a team loses the cord, the app needs a way to hand them the index. Probably the last hint on part 12. Not yet built. |

---

## Open

- **What the decoded word resolves to** is the last real narrative decision and
  it fixes the ending. Open as **D11**, with a name or a rendezvous as the two
  live candidates.
- **How many knots, and at which locations.** Falls out of the field walk: any
  reachable, permanent, unambiguous inscription on the route is a candidate.
  Best targets pair an anchor on one object with a landing on another.
- The two disappearances — the clerk in 1918, the researcher now — still have
  to rhyme rather than repeat. Phase 7.
