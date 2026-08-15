# GROUND TRUTH — narrative build state

The working memory for the Chapter Two narrative rebuild. Read this first in a
new session. Decisions land here the moment they are made, with the reasoning,
so nothing has to be re-argued and no session starts cold.

Status: **spine locked (D1–D4). Working on cast, documents and the map.**

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
| D5 | Who wrote the diary | open |
| D6 | What the map's lines cross on | open |
| D7 | What the players end up holding | open |

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

---

## Open threads not yet decided

- Emma Bowden (1864) is a real private person. Standing rule: **not
  fictionalised in any respect.** A conspiracy link would break that.
- The testing skip on location gates must come out before launch.
- Parts 4 and 17 need more hints if they are ever to carry lives.
- Clue 15's SQUIRE rests on an unverified padlock reading.
- Gate radii are unverified on the ground.
