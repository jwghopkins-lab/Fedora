# GROUND TRUTH — narrative build state

The working memory for the Chapter Two narrative rebuild. Read this first in a
new session. Decisions land here the moment they are made, with the reasoning,
so nothing has to be re-argued and no session starts cold.

Status: **spine, cast, route, clue text and the cord mechanic are all locked
(D1–D5, D7–D10). Phase 4 — the map — is parked. One narrative decision remains
(D11: what the cord's message resolves to) and it fixes the ending. After that
it is Phase 7 (the reveal) and Phase 8 (production and field verification).**

Companion documents: **`CAST.md`** (who, and what is fact vs reading vs
invention), **`ROUTE.md`** (the rebuilt 23 parts), **`MECHANIC.md`** (the cord)
and **`FIELDWORK.md`** (everything that must be walked before launch).

---

## What already exists and works (do not re-derive)

**Repo:** `github.com/jwghopkins-lab/Fedora`, branch `main`. The betting project
in `greyhound2` is unrelated; this session's working directory points there but
none of this lives in it.

**Live app:** `jwghopkins-lab.github.io/Fedora/quest.html`. Deploys from `main`
on push, via the `pages` workflow.

**Database:** Supabase, currently at **v9**. Confirmed 15 Aug 2026: 22 parts,
78 hints, 20 with lives, 3 with location gates.

**Team codes:** FEDORA5517 TRILBY4491 PANAMA8253 HOMBURG617 BOWLER9902
BOATER3348 CLOCHE7286 STETSON4630.

### The mechanics that are built and tested
- Clue text is served per team from Postgres; the client holds no answers.
- **Sequential hints**: `clues.hints[]` + `hint_waits[]`, one at a time, each on
  its own delay from when the clue opened. Last hint may give the answer away.
- **Explainers**: `after_text`, returned on a correct answer and with every
  reload, on every teammate's phone.
- **Lives**: `guess_limit`, three per part on 20 of 22, enforced server-side.
  Each hint taken buys a guess back, so a spent budget is never a dead end.
  Parts 4 and 17 are unlimited: fewer than two hints, so a limit would wall them.
- **Location gates**: `gate_lat/lon/radius_m/prompt` on parts 2, 4 and 18. The
  clue text does not leave the server until a check-in passes. Warm/cold, never
  yes/no. Passes when `distance − reported_accuracy ≤ radius`, accuracy credit
  capped at 150m so a fabricated fix cannot pass from a sofa. Every attempt
  logged to `checkins` with position. A **testing skip** is present and must be
  removed once the radii are field-verified.
- **Location pre-flight**: one permission check on first join, with
  per-platform instructions (iOS / Android / desktop).
- **Word-by-word reveal**: full text laid out invisibly so nothing reflows,
  words darken in, sentences slow at both ends. `TYPE_SLOWDOWN = 2.6`.
- **Card arrival**: scanner line then resolve out of blur, 2000ms.
- No skip button on clues. No locked parts drawn. Sticky Progress / Wrong
  answers meters.

### The rules we work by
- **Two-tier git**: load-bearing code on a branch with a review; everything else
  straight to main. Push every session.
- **The mock is the contract**: `pipeline/mock_backend.py` mirrors the SQL. If
  they disagree, whichever changed last is the bug. `test_backend.py` and
  `quest_smoke.cjs` gate on exit codes.
- **Migrations, never wipes**, on a live database. Function bodies are lifted
  verbatim out of `schema.sql` by `make_migration.py` — a hand-typed extract
  once silently dropped a grant.
- **Always verify a migration against a replica of the real database state**
  before sending it. On 15 Aug a migration failed because v7 had never actually
  landed and nobody had checked; a two-line query would have caught it.
- **Deliver SQL as a chat code block, not an attachment.** The client works on
  a phone and cannot open files conveniently.
- The private hunt JSON and any seed SQL contain every answer. Never commit.

### Tooling
| File | Does |
|---|---|
| `pipeline/validate_hunt.py` | contracts: ascending hint waits, no answer leaking into an earlier clue or hint, gate sanity, collect/contains coherence |
| `pipeline/build_hunt.py` | hunt JSON → private seed SQL |
| `scratchpad/make_migration.py` | live-safe migration, functions lifted verbatim |
| `scratchpad/make_editable.py` | hunt JSON ⇄ editable plain-text script, round-trips with zero loss |
| `scratchpad/make_review.py` | printable A4 script |
| `pipeline/mock_backend.py` | local mirror of every RPC |

---

## The research spine (all verified, all true)

These are the load-bearing facts. Anything invented must sit in the gaps
between them, never contradict them.

- **1834**: the Palace of Westminster fire destroys the imperial standard yard.
  The reigning king is **William IV**.
- **1838–1842**: **George Biddell Airy**, Astronomer Royal, is *chairman and
  working secretary of the commission on weights and measures*. Restoration runs
  to 1855 under Baily then Sheepshanks.
- **Forty bronze bars** made by Troughton & Simms. One becomes the Imperial
  Standard. Four are Parliamentary Copies: Royal Mint, Royal Society, Greenwich
  Observatory, walled into the New Palace at Westminster. **Thirty-five are
  dispersed to "the cities of London, Edinburgh and Dublin, the United States
  and other countries" — no accessible register of them exists.**
- **1851**: Airy's Transit Circle takes its first observation at Greenwich. It
  defines the line that becomes the **Prime Meridian in 1884**. *The same man
  fixed the nation's length and the world's longitude.*
- **1859**: **John Taylor**, *The Great Pyramid: Why Was It Built?* — deduces a
  "pyramid inch", 1/25 of a "sacred cubit" whose existence had been postulated
  by **Isaac Newton**. Four sides of the pyramid = 36,524 pyramid inches = 100×
  the days in a year. Taylor, a Christian, concludes the British inch is
  divinely inspired and the restored yard is wrong by about a thousandth.
- **1864**: **Charles Piazzi Smyth**, Astronomer Royal for Scotland, publishes
  *Our Inheritance in the Great Pyramid*. He and Airy are antagonists.
- **1866**: the Standard Weights and Measures Department of the Board of Trade
  is created.
- **1869–1938**: that department works in the **Jewel Tower**, Old Palace Yard.
  It leaves because **road traffic vibration** made precise measurement
  impossible. (The Airy Transit Circle also leaves service in **1938**.)
- **1876**: public imperial standards set into the north terrace at Trafalgar
  Square, inscribed **"at 62 degrees Fahrenheit"**, triplicated with the
  Guildhall and the Greenwich gate. **Moved east in 2003**; no source states
  whether the plates are the 1876 originals or recuts.
- **1878 Act**: defines "local standards" held by inspectors, and provides in
  statute for standards **"lost, destroyed, defaced or otherwise injured"** to
  be restored from an imperial standard or parliamentary copy.
- **1879–c.1888**: the International Institute for Preserving and Perfecting
  Anglo-Saxon Weights and Measures. Smyth a vice-president. A magazine mixing
  metrology with occultism; a song, *A Pint's a Pound the World Around* (1883).
- **1888**: Smyth resigns from the Royal Society. **1900**: Smyth dies.
- **1895**: a Commons Select Committee recommends metric be **compulsory within
  two years**. The **1897 Act legalises but does not compel**. Britain misses
  metrication by a hair.
- **1900**: the London Government Act abolishes the vestries; their property,
  **including the local standards they held**, passes wholesale to 28 new
  metropolitan boroughs. St Martin-in-the-Fields is a parish on the route.
- **Primary source available**: Airy's own *Account of the Construction of the
  New National Standard of Length, and of Its Principal Copies* (abstract, on
  Wikimedia Commons). Real, citable, and almost nobody has read it.
- **Hayward Brothers**, Union Street Borough: patented **semi-prism pavement
  lights in 1871**. Electric light: Victoria Embankment 1878, Savoy Theatre
  10 Oct 1881.

### Hard constraints on the cast (verified — do not build against these)
- **Piazzi Smyth had NO children.** Married Jessie Duncan 1855, childless; she
  died 1896, he died 21 Feb 1900 near Ripon. Residuary estate to the Royal
  Society of Edinburgh; papers inventoried at the Royal Observatory Edinburgh.
  **A "descendant of Smyth" is refutable in thirty seconds and must not be used.**
  Use a *correspondent* instead. Anything absent from the Edinburgh inventory is
  genuinely unaccounted for — that absence is itself a usable gap.
- **Smyth died Feb 1900. The vestries were abolished in 1900.** Months apart.
  A parish clerk who corresponded with him in the 1880s is the natural join.
- **Edith Cavell will not be given an invented reason for her execution.** A real
  woman, shot by a firing squad; inventing a secret motive cheapens it.
- **Emma Bowden (1864) is not fictionalised in any respect.** Real private person.
- **Dryden (1679) is cut** — wrong century for this story.

### Cast links found in the existing route (all verified 15 Aug)

Everyone below is *already* on the walk. These are real joins to the
measurement and light threads, not inventions. Graded by strength.

| Character | The join | Grade |
|---|---|---|
| **J. M. W. Turner** | Born Maiden Lane, **Covent Garden** — the end of the walk. Watched the **1834 fire from the south bank**, sketched it, painted it twice. He is an eyewitness to the destruction of the standard yard, and he is the painter of light. Joins both ends of the route and both threads. | ★★★★★ |
| **Nelson's Column** | Believed 185 ft for ~150 years. A **2006 laser survey** during refurbishment found **169 ft 3 in — 14 ft 6 in short**. The best "recorded number was wrong and nobody re-measured" fact on the route, at its centre. | ★★★★★ |
| **Lutyens** | The **Cenotaph has no straight lines**: entasis from measurements of the Parthenon, verticals converging ~1000 ft above, horizontals arcs of a circle centred ~900 ft below the pavement, 33 manuscript pages of calculation. A national monument where nothing is the length it looks. He also **remodelled the Trafalgar Square fountains (1937–39)**, so he is on the route twice. | ★★★★★ |
| **William IV** | The 1834 fire was started by burning **two cart-loads of Exchequer tally sticks** in the House of Lords stoves — an obsolete measuring/accounting system, disused since 1826. Measurement destroyed the standard of measurement. | ★★★★☆ |
| **Napier** | Descended from **John Napier of Merchiston, inventor of logarithms** (via Francis Napier, 6th Lord Napier → Col. George Napier). Merchiston is Edinburgh — Smyth's city. Second join: C-in-C India, Sindh 1843, i.e. the **Indian foot** already carrying the ~7 ppm discrepancy. | ★★★★☆ |
| **Cunningham** | Bust by **Franta Belsky**, at the foot of the National Gallery steps — the north terrace, beside the standards. **A note by the sculptor and a ½-pint Guinness bottle are sealed inside it.** A document hidden in public sculpture, and it is true. This is the mechanic rhyme. | ★★★★☆ |
| **Verne** | *Around the World in Eighty Days* (1872) turns entirely on the **day gained by crossing the meridian** — twelve years before the conference that fixed it at Greenwich. Mr Fogg's is already a gate (part 18). | ★★★★☆ |
| **Landseer** | The lions are **anatomically wrong** — domestic-cat paws, concave backs — because the Turin cast was late and the zoo lion decomposed faster than he could work. A celebrated monument that is measurably incorrect and nobody minds. Also: **Lutyens was his godson and namesake** (Edwin *Landseer* Lutyens). | ★★★☆☆ |
| **Edith Cavell** | Only honest join: **"Patriotism is not enough" was added to the memorial in 1924**, four years after it was unveiled — a monument amended after the fact. No invented motive, ever. | ★★☆☆☆ |
| **Emma Bowden** | None, by rule. Not fictionalised in any respect. | — |

### The Millicent Fawcett plinth (part 1)

59 names. The clue reads one off the stone, so **swapping which name costs
nothing** — same plinth, same mechanic.

- **Henrietta Franklin** (currently chosen, 1866–1964). Father **Samuel
  Montagu, 1st Baron Swaythling** — a bank that began in the exchange of
  **coins and bullion**, a trade that lives or dies on weight standards.
  Married Ernest Louis Franklin and so is **related by marriage to Rosalind
  Franklin** (X-ray diffraction: measuring structure with light). Both real.
- **Ray Strachey** — *the strongest name on the stone.* Married **Oliver
  Strachey** in 1911; Oliver was the son of **Lieut.-Gen. Sir Richard
  Strachey**, one of the four British commissioners at the **1884
  International Meridian Conference** and elected one of its secretaries.
  That is the exact table the motive (D2) rests on. Bonus: **Oliver Strachey
  was a cryptographer** — MI1, then GC&CS, head of the **ISOS** section
  ("Illicit Services Oliver Strachey").
- **Sophia Duleep Singh** — India, and so adjacent to Napier. Political, not
  metrological. Weaker.
- **Hertha Ayrton is NOT on the plinth** — checked, because she would have
  been perfect (line-divider patented **1884**, and the definitive work on the
  electric arc). Do not chase this; the full 59 do not include her.
- Unchecked but promising: **Chrystal Macmillan** (Edinburgh maths and natural
  philosophy, named for George Chrystal) and **Mary Lowndes** (stained glass,
  Lowndes & Drury — the light thread).

### The three documented gaps a fiction can live in
1. **No register of the thirty-five bars.** Every source stops at "cities and
   other countries."
2. **The 1900 vestry dissolution.** Every parish held verifiable local
   standards; the transfer was wholesale and poorly inventoried.
3. **Whether the Trafalgar plates are 1876 originals or recuts.** Not one
   source addresses it, and players stand on that ambiguity at part 12.

---

## What the red-team experiment established

Five independent verifiers with web search, 18 assertions, blind.

| | corroborated | contradicted | unverifiable |
|---|---|---|---|
| real facts | 93% | 7% | **0%** |
| every fabrication style | **0%** | 20–47% | 53–73% |
| refutable controls | 0% | 100% | 0% |

- **No camouflage technique worked.** Interleaving true and invented clauses,
  citing real archives, sitting in documented gaps — all scored zero
  corroborations. The differences between them are noise (3 vs 5 of 15).
- **The tell is "unverifiable", not "false".** A player needs only ask *which of
  these can you confirm?*
- **Therefore: the fiction must not live in the fact register.** A claim about
  what happened can be checked. An *interpretation* — "I have gone over the
  terrace twice and I am satisfied the perch does not match its neighbours" —
  cannot be refuted by search, because it is not a claim about the record. And
  a fact the author privately holds (a photograph, a measurement) is exactly as
  un-Googleable as a lie and carries no risk of being contradicted.
- **Structural law**: fiction may be an *edge*; only fact may be a *node* a
  player stands on. Every chain reaches a real, checkable, physically present
  terminal within three hops.
- **Channel survivability** through photograph → OCR → model:
  text acrostics ~100% recovered (use as the tutorial flare, not the payload);
  OCR-confusable misprints 40–70%; a partial register keyed page/line/word ~30%;
  **geometry in a hand-drawn plan <5%** — vision models describe drawings, they
  do not measure them; **a key that only exists on the pavement, 0% provably.**
  Line-position codes do NOT survive copy-paste, only a screenshot.

---

## Decisions

| # | Decision | Status |
|---|---|---|
| D1 | Frame | **LOCKED** — in character from the walk |
| D2 | Motive | **LOCKED** — national and scientific, with two corrections |
| D3 | Artifacts | **LOCKED** — diary, marked string, chalk marks |
| D4 | Route | **LOCKED** — keep the spine, rebuild Covent Garden |
| D5 | Who wrote the diary | **LOCKED** — two hands, layered |
| D6 | What the map's lines cross on | **PARKED** by the client, 15 Aug: forcing a geographic crossing produces a map that lies. Settle it after the route is rebuilt (Phase 4/5), not before |
| D7 | What the players end up holding | **LOCKED** — their own measurement |
| D8 | Cast membership and size | **LOCKED** — six on the route, two objects, two in the document. Full page in `CAST.md` |
| D9 | Route surgery | **LOCKED** — 18 kept, 3 cut, 1 replaced, 4 new, 23 parts. Full page in `ROUTE.md` |
| D10 | The cord is a key, not a ruler | **LOCKED** — full page in `MECHANIC.md` |
| D11 | What the decoded message resolves to | **open**, two live candidates from the client — a **name**, or a **place where he is waiting** |

### D1 — Frame: in character from the walk *(15 Aug)*
Sign-up, team codes and the landing page stay plainly a puzzle event, so nobody
is deceived into playing. From the moment the diary is opened it never breaks
character, and the client is genuinely unreachable all day. Honest at the door,
total immersion inside. A debrief at the finish separates fact from invention.

### D2 — Motive: national and scientific *(15 Aug)*
The establishment buries the defect to protect Britain's standing, not its
geodesy. **Two corrections were required to make it survive scrutiny:**

1. **The error must be a few parts per million, not a thousandth.** Smyth's
   claimed thousandth is a thousand ppm; real inter-standard discrepancies were
   single digits — the Indian foot and Clarke's foot differ by ~7 ppm, and that
   difference is still in surveying software today. A thousandth would have been
   caught in a week. At single-digit ppm it plausibly survives seventy years and
   propagates silently into the figure of the Earth and every chart's scale.
2. **The stake is credibility, not longitude.** Longitude is angular, fixed
   astronomically by the transit circle; a wrong yard does not move the meridian,
   and any thoughtful player will see that. The real stake: in 1884 Britain was
   handed the world's meridian on an expressed hope it would accede to the
   Convention du Mètre — Strachey said it would — **and Britain never did.** It
   could not afford anyone proving its own standard defective at that table
   while arguing its standards were the best in the world.

Smyth's side needs no further motive than the human one: he was right, and he
was buried for it.

**Supporting facts, all verified:**
- Clarke's medal was for *"comparison of standards of length, and determination
  of the figure of the earth"* — in Victorian geodesy, one job. The shape of the
  Earth was computed **from** the length standards.
- Clarke, 1866: the metre = 39.370432 British Imperial inches, by comparing
  standards.
- Lough Foyle base, 1827–28, Colby's compensation bars; remeasured
  electronically in 1960 and out by about an inch.
- 1884: France and Brazil abstained; the resolution passed 22–1.

### D3 — Artifacts: diary, string, chalk *(15 Aug)*
Printed facsimile diary, plus the marked cord of the "true yard" whose intervals
map to letters with one or two planted errors, plus chalk marks laid on the route
before each cohort. The cord is the machine-proof channel: a key that exists only
as a physical length, recoverable at 0%. Chalk needs a dawn walk on the day and a
re-check an hour before the start.

### D4 — Route: keep the spine, rebuild Covent Garden *(15 Aug)*
Parts 1–16 (Parliament and Trafalgar) carry the measurement story and stay
largely intact, retargeted. Parts 17–22 are rewritten around the light thread and
the map. **Dryden is cut** — wrong century. **Emma Bowden stays untouched** as
the closing human note; she is a real private person and is not fictionalised.

### D5 — Diary: two hands, layered *(15 Aug)*
A Victorian document carrying a modern researcher's annotations in the margins.

**The Victorian hand is the vestry clerk of St Martin-in-the-Fields** — an
invented man in a real office, corresponding with Smyth in the 1880s, his
survey book ending in 1900 when he is told to hand the parish's standards over
and does not. Smyth died Feb 1900 and the vestries went the same year, so the
dating locks without being forced, and no record of him surviving is exactly
what you would expect. *(Swappable for a Board of Trade inspector from the
Jewel Tower if the client prefers insider access to un-refutability — but that
department's records are the most searchable of any option.)*

**Why the layering is a structural win, not just flavour.** The red-team
result says fiction must live in the *interpretation* register, never the fact
register. Two hands give us that separation physically: the Victorian document
stays close to the record, and the modern marginalia carries every
unverifiable reading — *"I have been over the terrace twice and I am satisfied
the perch does not match its neighbours."* A margin note is an opinion by
construction. It cannot be refuted by search because it is not a claim about
the record.

**Consequences accepted:**
- Two typefaces and two inks in the facsimile. Real production cost.
- **The reveal must carry two disappearances** — the clerk in 1900 and the
  researcher now — and they have to rhyme, not merely repeat.
- The planted errors live in the marginalia, where a mistake reads as a
  researcher's slip rather than a forger's.
- The modern hand can *point* — arrows, "see p.14", "this does not match" —
  so the cord and chalk mechanics hang off the annotations and the Victorian
  never has to explain a 21st-century puzzle.

### D7 — Payoff: their own measurement *(15 Aug)*
They finish holding the marked cord and a number they read off it themselves,
written on the map in their own hand. Nothing is handed over at the end.

**Consequences accepted:**
- The cord is **issued or found early**, not at the finish.
- The measuring act needs a genuine public standard, and the **Trafalgar north
  terrace plates are the only one on the route** — at part 12, not at the end.
  So the act happens mid-walk and the *meaning* lands in Covent Garden.
  Resolve in Phase 7; do not loop the route back to Trafalgar to fix it.
- No prop is handed over at the finish, so the debrief sheet is the only
  physical handout. Cheaper, and it makes the debrief the close rather than an
  anticlimax after it.
- **Precedent to echo, and it is true:** the Cunningham bust on the north
  terrace has a note by its sculptor sealed inside it.

### D8 — Cast: six on the route *(15 Aug)*
Full page with fact / interpretation / invented for each: **`CAST.md`**.

**Kept:** Belsky, Lutyens, Turner (the spine — each appears in two acts), then
Ray Strachey, Landseer, Verne (once each, hard). Plus two objects that behave
like characters: **Nelson's Column** and **the terrace plates**. Plus the two
people who exist only in the document: the clerk and the researcher.

**Cut:** William IV (a date, not a character — the tally-stick fact survives as
narration), Edith Cavell, Emma Bowden, Dryden, and **Napier**. On Napier
specifically, since the question was asked: the India link *is* contemporaneous
— he was there 1842–51 while the Great Trigonometrical Survey and the Indian
foot were live — but he was a general with no role in any of it, so it is a
coincidence of place and date rather than a connection. Statue retained as a
clue target if one is needed.

**The rule that governs the cast is not the count:** every character appears at
least twice; at least one appears in all three acts. A character seen once is
scenery, a character seen three times is evidence, and the feeling of a pattern
is the entire emotional payload of a conspiracy story.

**Belsky is now the strongest thread in the game, and nearly all of it is true.**
He sealed a Guinness bottle, that day's newspaper, **a sixpence** and a signed
note into *every casting he made*. The Cunningham bust went up on the north
terrace on **2 April 1967** — the year the Decimal Currency Act began killing
the sixpence, and two years after Douglas Jay told the Commons Britain would go
metric by 1975. His Mountbatten, off Horse Guards Road, went up on **2 November
1983** with a jam jar of coins in its left leg, **cast by the Meridian Bronze
Foundry**, twelve days after the 17th CGPM redefined the metre as a property of
light on 21 October 1983. Every one of those is checkable. The *reading* — that
a refugee from a country measured off the map was depositing units where they
could not be legislated away, and the autograph was cover — is unrefutable
because it is a reading.

**Two hard rules that come out of Belsky:**
1. **The bust cannot be opened, and nothing may ever suggest otherwise.** No
   clue, hint or explainer may hint at touching, prising or tapping any
   sculpture. It is to be looked at.
2. That constraint *is* the ending, and it falls straight out of D7: they
   cannot open the bust, so they measure the terrace instead. **The bust is the
   promise, the plate is the proof, their hand does the work.**

**The clerk dies in the Spanish flu** *(client)*. Better than the war: he is
past sixty by 1918, so a war death needs explaining and a flu death does not,
and nobody took a statement from him because that autumn nobody was taking
statements. Note the deliberate eighteen-year gap — the *book* ends in 1900,
the *man* in 1918 — which is why it was in a cupboard and not an archive.

### D9 — Route: 17 kept, 4 cut, 1 replaced, 4 new *(15 Aug)*
Full page: **`ROUTE.md`**. Lands back on **22 parts**.

**Cut:** cricket, SQUIRE/the padlock, Dryden, Emma Bowden.
**Replaced in place:** Cavell → **St Martin-in-the-Fields**, which is the
clerk's own parish and sits exactly on the Act 2 / Act 3 hinge. The players walk
past the address on the diary's flyleaf without being told.
**New:** the Cenotaph and Mountbatten Green in Act 1; **Nelson's Column** as the
turn in Act 2; **Maiden Lane / Turner** to close the loop in Act 3.

Two things worth carrying forward:
- **Act 1 was ten dead minutes.** The Cenotaph and Mountbatten do not add time,
  they convert a hike up Whitehall into the two beats that set up everything
  after. Biggest single improvement in the phase.
- **Part 15 was already doing our work.** Its existing explainer ends *"one
  sealed inside a man's head where nobody can ever see it"* — the promise/proof
  structure of D7, written months before we decided it. It only needed the
  terrace measurement to answer it.

### D10 — The cord is a key, not a ruler *(15 Aug)*
Full page: **`MECHANIC.md`**.

**A few ppm over a yard is a few microns.** It is smaller than the mark you
would draw to show it, smaller than the cord's stretch under hand tension, and
smaller than its own thermal change between a cold morning and a warm
afternoon. Over the terrace's whole hundred-foot run the signal is still under
a millimetre while the hand-error budget is inches. **No cord can show the
discrepancy**, and scripting a measurement that must come out at a particular
number would break the game in public on the first outing.

So the cord becomes a **key** — and specifically a **pointer**, not a ruler
*(client's design, superseding the first page/line/word version)*. The diary
names a knot and an anchor; you put the cord's zero on the anchor, pull it
straight, and the knot lands on one letter of a real inscription. One character
per location, spelling a word across the walk.

**Why the revision is better:** the old version read the payload out of our own
invented document. This one reads it off the pavement, so under the structural
law the answer is a fact node again and the diary demotes to the reference book
that tells you which knot and where to stand.

**The attack that has to be designed against is proportion, not stencils.** Lay
a cord end-to-end along an inscription and the knot sits at a *fraction*, which
any photograph yields without scale. So the cord is never aligned to the
target's extent: **zero on a named physical anchor, knot landing at an absolute
offset — ideally anchoring on one object and landing on another**, so no single
photograph contains both at a known scale.

**And the theme was waiting for it.** Beating the bounds — the parish
perambulation, walking the boundary and striking the marks — is still done by
**St Martin-in-the-Fields**. St Paul's Covent Garden was carved out of St
Martin's in 1646 with its boundary defined as *"40 foote without the ... bricke
wall"*: a parish boundary specified as a distance. The players walk out of St
Martin's into Covent Garden carrying a cord, transferring lengths from place to
place. **The cord is the clerk's perambulation cord** and none of that is
invented.

This costs nothing, because what made the cord valuable was never precision but
that it is a length existing only as an object. Red-team numbers: a partial
register keyed page/line/word survives photograph → OCR → model at about
**30%**; the key itself, being a physical length, at **0%**.

**D7 survives intact and improves.** They still finish holding a number they
produced themselves, but now they *read* it rather than estimating it, so it is
exact and identical for every team. Part 12's text is unchanged — laying the
cord along the Crown's own ruler is what produces the reading, and the players
will not know that is what they are doing.

**Planted errors go in the researcher's marginalia**, never on the cord (an
error there is unrecoverable) and never in the clerk's hand (it is the one
voice that must stay trustworthy). One confident wrong index, one hedged right
one.

**Hard production order: field measurements → cords knotted → diary references
written from them.** Distances are *discovered, not designed* — the cord cannot
be derived from any document because it did not exist in one before somebody
measured it, and that is the entire security argument. Knots are whipped
coloured thread, not ink. Non-stretch braided line. Spares, because a lost cord
is a dead hunt.

### D11 — open, with two candidates *(client, 15 Aug)*

**(a) A name.** The client's instance was "who killed the clerk". **Note the
collision:** D5 locks the clerk dying of Spanish flu, so nobody killed him.
The two are reconcilable — autumn 1918 is precisely the cover a death would
hide behind, because nobody was investigating anything and nobody took
statements — but it must be a deliberate choice, not an accident. Since the
clerk is invented there is no record to contradict, so it is legal under the
structural law. The real cost is **genre**: a murder pulls the walk towards
detective fiction and away from "the country never checked", which is the
thesis everything else has been built to land. If we go here, the name should
probably be *who took the parish's standards in 1900* or *who he was writing
to*, not a killer.

**(b) A place, and the client is standing in it.** This is the stronger idea
and it solves three problems at once:
- **The second disappearance resolves in person.** The researcher who vanished
  is the man they walk up to. No prop, no reveal document, no anticlimax — the
  two disappearances rhyme because one of them ends.
- **D7 lands physically.** They arrive holding the cord and the reading they
  took off the terrace, and hand it to somebody who has been waiting for it.
- **The debrief has a natural seam.** In character when they arrive, out of
  character when he tells them which half was true.
It is also consistent with D1: genuinely unreachable *during*, present at the
end.

**What (b) would require:** somewhere walkable from Maiden Lane; somewhere one
person can sit for two or three hours while teams arrive at different times;
indoor or weatherproof; and it must be nameable by a single decoded word.

---

## What is left (as of 15 Aug)

**Critical path:** field walk → knot distances measured → cords cut → the
diary's knot and anchor references written from them. The diary's *prose* can
be written in parallel; only its references wait on the walk. **The field walk
is now the gating item for the entire physical build.**

### Blocked on D11
- Phase 7: the reveal and the debrief.
- The diary's **last entry** only. The rest of it is not blocked.

### Narrative writing still to do
- **The diary itself** — the single biggest remaining creative job. Both hands,
  the clerk 1880s–1900 and the researcher's marginalia.
- The marginalia's planted errors: one confident wrong index, one hedged right
  one (D10).
- The **Strachey → 1884 meridian table** edge, which lives in the margin and
  nowhere else (D8: contrived if asserted, uncanny if found).
- The part-drawn map. **Parked with D6** until the route is walked.

### Fieldwork
- One walk. Everything in **`FIELDWORK.md`**. Two items carry real risk: the
  Cenotaph clue may be unsafe to solve from the pavement, and the terrace brass
  gates the entire physical build.

### App and database
- Migration to the **23-part route**. Needs sign-off on the Phase 6 text first,
  then a rebuilt hunt JSON, then a v10 migration verified against a replica.
- New parts **6 and 19** still have fewer than two hints, so they cannot carry
  lives.
- Gates move to parts **2, 6, 20** under the new numbering.
- Remove the testing skip once radii are walked.
- Re-run `validate_hunt.py`, `test_backend.py`, `quest_smoke.cjs` after the
  content change.

### Physical production
- Diary: written, designed, two typefaces and two inks, printed, **paginated
  before the cords are cut**.
- Cords: non-stretch braided line, knotted against the measured brass, one per
  team plus two spares.
- The map, printed.
- Chalk marks: a dawn walk on the day and a re-check an hour before the start.
- The debrief sheet — the only thing handed over at the finish (D7).
- A fallback if a team loses its cord. Probably the last hint on part 12. Not
  designed yet.

## Open threads not yet decided

- The testing skip on location gates must come out before launch.
- New parts **6** and **18** still have fewer than two hints, so they cannot
  carry lives.
- **The lions: dog or cat?** The script says dog-like paws and "his own dog";
  published accounts say a domestic cat's paws and concave backs, caused by the
  late Turin cast and a zoo carcass that rotted. Needs a source before it goes
  near a clue.
- Gate radii are unverified on the ground; gates now sit on parts **2, 6, 19**.
- The diary's entry point is unplaced — the frame is locked but nothing in the
  route yet *opens* it. Phase 6.
- Phase 4 (the map, and D6) is parked until the route is walked.
