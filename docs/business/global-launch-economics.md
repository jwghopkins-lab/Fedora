# Fedora — global launch economics

*Business model for the 10-city global launch, 6 Aug 2026. Deep research +
three-year low/medium/high scenario model. Companion artefacts:*

- `model/build_model.py` — the scenario engine (run it; assumptions inline)
- `model/fedora-3yr-model.xlsx` — the same model as a live spreadsheet
- `research/*.md` — five research appendices with sources and confidence
  ratings (competitor pricing, marketing/CAC, sponsorship, market sizing,
  competitive response)

*The plan modeled, as briefed: one field-verified hunt per city in 10 big
cities at launch, all tested and AI-red-teamed; big marketing effort; app
free to download with the first hunt free; local-business sponsorship and
advertising switched on at a second launch wave (month 9). All money GBP.*

---

## 1. Executive summary

**How much could we make?** Over 36 months: **−£1.0M (low), −£1.8M
(medium), +£2.3M (high)** cumulative. The high case reaches a ~£3.5M/yr
revenue run-rate by year 3 but passes through a **−£1.8M cash trough**
first, so even the win scenario needs ~£2M of funding. The plan as briefed
is, financially, **a bet on the launch becoming a viral moment** — the
research supports that this can happen to real-world games (Pokémon GO,
Randonautica), but the median outcome of this launch shape loses money for
three straight years.

**How far ahead before someone catches up?** Copying is cheap — a
competitor could field-verify 10 cities for **$10–40K** — but nobody is
positioned or motivated to do it until Fedora visibly succeeds. Research
timelines: a startup fast-follower **6–18 months after visible traction**;
a Questo-class incumbent retrofit **12–24 months after a forcing event**;
AI-proof positioning stops differentiating in **24–48 months**. At the
moment a competitor lands, Fedora has banked **£99K (low) / £511K (medium)
/ £3.0M (high)** of revenue. The durable asset is not the head start in
cash: it is the ground-truth dataset, the red-team methodology, and a
community that re-verifies content — a recurring-cost moat a copycat must
fund forever.

**The model's biggest surprise:** in every scenario that isn't viral, the
consumer game is not the business. By year 3 of the medium case, **75% of
revenue is corporate events, sponsorship, and white-label commissions**;
direct consumer hunt sales are 15%. The free city game is best understood
as the marketing engine and proof-of-quality for a B2B business — which is
also exactly where the research says the category's money has always been
(ClueGo at £55–65/head corporate vs Questo at €8–20 consumer, funded to
just $2.1M in 7 years).

**Recommendation (§9):** don't launch 10 cities simultaneously on paid
marketing. Sequence: prove London unit economics in 2–3 quarters
(≈£250K), then expand city-by-city with sponsor/OTA-funded launches, and
keep "global launch day" as a PR moment once conversion is proven. If the
10-city big bang proceeds anyway, it needs ~£2.5M and the wave-2
monetisation date is the critical path (§6).

---

## 2. What the research established

Five research sweeps (full appendices with sources in `research/`):

**Category economics are proven — and modest.** Consumer self-guided
pricing clusters at €7–15/person or €22–27/team. Questo — the only
VC-backed pure-play, with 3,000 quests in 1,000 cities and ~500K users —
raised just $2.1M in 7 years. Secret City Trails exited small. The 20-year
survivor (Treasure Trails UK, £9.99 booklets, 2M lifetime players) is a
profitable lifestyle business at roughly £0.5–1.5M/yr. Nobody has made
venture-scale money selling self-guided hunts to consumers.
[`research/competitor-pricing.md`]

**Paid installs cannot carry a £12 ticket.** Blended tier-1-city CPI is
~£2.40; freemium conversion ~2.1% of installs; that's **~£120–150 of paid
media per paying team** against a ~£40 gross purchase. Viator's SEC
filings show 67–71% of revenue going back into marketing — that is what
buying experience-customers costs at scale. Every location-game success
grew organically (Pokémon GO ~zero paid launch; Randonautica 10.8M
downloads off TikTok; Zombies, Run! a sustained business on ~zero paid
UA). OTA distribution (GetYourGuide/Viator listings at 20–30% commission ≈
£3 per ticket) reaches buyers ~30× cheaper than a paid funnel.
[`research/marketing-cac.md`]

**Venue-side money is real and unclaimed.** Niantic proved SMBs pay
$30–60/month per sponsored location and <$0.50 per (weak) in-game visit; a
group of 4 finishing at a pub is worth £75–108 across the bar. UK art
trails charge £6–8K per sponsored stop; councils/BIDs provably pay
£2.5–25K for commissioned digital trails (Ipswich: £22,845); museums pay
£3–25K for white-label products. **No direct competitor monetises venues.**
In-app advertising, by contrast, is a rounding error at any plausible MAU
(£1–30K/yr). [`research/sponsorship-economics.md`]

**The 10-city serviceable market is 265K–3.3M players/yr** (low–high),
worth €3.2M–€40M gross at a €12 ticket, anchored on Sandemans' ~1% capture
of city visitors and escape rooms' ~3–3.5% of population annually. Top
cities by opportunity: Paris, New York, London, Rome, Singapore. Corporate
is additive: London alone hosts an estimated ~55K paid team events/yr.
[`research/market-sizing.md`]

**The moat is operational, not technical — and it holds 2–4 years.**
Copy costs are trivial ($500–2K/city with a local contractor), but: no
incumbent has field-verification ops; Let's Roam's own reviews document
AI-generated unverified content rotting in the field; Questo's economics
(75% creator royalty) can't fund verifiers; and the industry's public AI
conversation is entirely about *generating* content cheaply, not defending
it. Precedents (Michelin, Street View, Geocaching) say physical-verification
moats hold for years-to-decades **if** compounded with community and data;
crowdsourced attacks (Waze-style) take 2–5 years to become trustworthy for
active-labour verification. [`research/competitive-response.md`]

---

## 3. Unit economics

**One hunt** (fully loaded, excluding core-team salaries):

| Item | Home city | Remote city |
|---|---|---|
| Design + field days + QA + ground-truth photos | £8,000 | £14,000 |
| Adversarial AI red-team (compute + review) | £500 | £500 |
| **Build total** | **£8,500** | **£14,500** |
| Re-verification / maintenance per year | £1,200 | £2,500 |

- **Launch content for 10 cities ≈ £136K** — a one-off that is small next
  to the marketing budget (11–22% of year-1 costs in medium).
- **Amortisation:** at £45/team gross (£41 net), a remote hunt needs ~350
  paying teams to cover its build and ~60 teams/yr to cover maintenance.
  At medium conversion (10% of engaged teams), that means ~3,500 engaged
  teams — ~12,000 free players — per city. This is the content-cost
  tension in one number: **each city must produce ~12K engaged free
  players before its first paid hunt breaks even.**
- **CAC vs LTV (medium):** effective cost per engaged team ~£16; per
  *paying* team ~£160 via paid installs, against a payer LTV of ~£95–100
  (first purchase + ~1.3 capped repeats, 5%/mo pool churn). **Paid UA is
  ~1.6× underwater**; organic, OTA, PR and referral must carry
  acquisition. This is a research-confirmed structural fact of the
  category, not a tuning artefact.

**Where unit economics actually work:**

| Channel | Unit | Net contribution | Evidence |
|---|---|---|---|
| Corporate event | 25–40 heads @ £55–65 | ~£1,600/event (65% margin) | ClueGo/Team Tactics pricing |
| City sponsorship | per city-year | £2.5–60K, ~90% margin | Niantic, Wild in Art, BID budgets |
| White-label | per deal | £2.5–150K, ~55% margin | Ipswich £22.8K; STQRY; Derry £346K |
| OTA-listed hunt | per team | ~£25 net, zero CAC | GYG/Viator 20–30% take |
| Direct hunt sale | per team | ~£37 net **before CAC** | Category pricing |

---

## 4. The three-year scenarios

Engine: 36 monthly periods; acquisition funnel (marketing → installs →
free-hunt players → teams), wave-2 conversion with a churned repeat pool
capped by catalogue releases, six revenue streams, full cost stack,
competitor entry with growth/price dampening. All assumptions sourced in
the appendices; run `python3 model/build_model.py` to reproduce.

| | **Low** | **Medium** | **High** |
|---|---|---|---|
| *Narrative* | Launch lands quietly; retrench | Solid hit; category gets named | Cultural moment; virality carries UA |
| Year-1 marketing | £250K | £640K | £1.4M |
| Players reached (36m) | 25K | 213K | 1.5M |
| **Y1 revenue / net** | £7K / −£624K | £181K / −£1.10M | £1.97M / −£266K |
| **Y2 revenue / net** | £48K / −£188K | £430K / −£378K | £3.53M / +£1.67M |
| **Y3 revenue / net** | £85K / −£159K | £604K / −£310K | £3.53M / +£940K |
| **Cumulative 36m** | **−£971K** | **−£1.79M** | **+£2.35M** |
| Cash trough | −£971K | −£1.79M | −£1.79M |
| Y3 revenue mix | corp 43%, sponsor 28%, OTA 15% | corp 40%, sponsor 20%, WL 15%, direct 15% | direct 50%, corp 16%, WL 14%, sponsor 11% |

Reading the scenarios honestly:

- **Low** is not a disaster-management failure — it already assumes
  competent retrenchment (marketing cut to £5K/mo, near-solo team, dead
  cities pruned). The £971K loss is mostly the unrecoverable launch spend:
  £250K marketing + £136K content + £45K app + a year of salaries against
  ~zero revenue. **The 10-city shape front-loads ~£450K of spend before
  the first paid conversion is even possible.**
- **Medium is the damning one.** A genuinely decent outcome — 213K players,
  a growing B2B book, £600K year-3 revenue — still loses £1.8M because the
  10-city cost base (content everywhere, marketing everywhere, staff to
  operate everywhere) outruns medium demand. Sensitivity checks: +50%
  conversion, half the launch burst, high-case sponsorship rates, or
  doubled corporate each improve the picture by only £150–350K; **no
  single lever flips medium positive**. The business it converges toward
  (B2B-led, ~£850K/yr revenue potential with corporate+sponsorship
  emphasis) is real — but it didn't need a 10-city consumer launch to
  build, and would break even far sooner without one.
- **High** is credible as a *scenario* — a £900K launch burst plus the
  "first game AI can't play for you" press angle producing a
  Randonautica-scale spike (1.9M installs in the launch quarter), decaying
  but converting. It makes money in year 2 and banks a real lead. The
  cost: surviving a −£1.8M trough in year 1, which must be funded in
  advance.

---

## 5. How far ahead before someone catches up

What is banked at the moment a credible competitor lands:

| | Low (m30) | Medium (m21) | High (m15) |
|---|---|---|---|
| Revenue banked | £99K | £511K | £3.0M |
| Cash position | −£890K | −£1.38M | +£306K |
| Players reached | 24K | 179K | 1.18M |

Three things the numbers say about the head start:

1. **The lead is players and data, not cash.** Even in medium, the
   competitor arrives while Fedora is £1.4M underwater. What it cannot
   copy for $40K: 179K players' worth of brand, the leaderboard
   community, two years of red-team learning, and a ground-truth photo
   archive with re-check dates for every clue in 10 cities.
2. **The window is entry-timing-fragile.** If a fast follower lands at
   month 9 instead of 15 in the high case — before wave-2 monetisation —
   banked revenue collapses from £3.0M to £114K. **Speed to monetisation
   matters as much as speed to launch.** Pulling wave 2 forward (even a
   partial paid catalogue at month 5–6) is the cheapest insurance in the
   whole plan.
3. **The 2–4 year moat needs to be spent, not sat on.** Research timeline:
   fast-follower at 6–18 months post-traction, incumbent retrofit at
   12–24, positioning parity at 24–48. Geocaching vs HintHunt is the
   fork: the winner converted its window into a community that generates
   and re-verifies content (unchallenged at 25 years); the loser watched
   1,500 copies arrive in four years. The window should be spent building
   the player-verification loop (§6.1) and signing exclusive venue/BID
   relationships — contracts and communities compound; a head start in
   revenue alone does not.

---

## 6. The seven tensions from the handoff

### 6.1 Content cost vs defensibility — moat or ceiling?

Both, at different scales. At launch scale the moat is nearly free: £136K
builds 10 verified hunts, and maintenance (~£23K/yr for 10) is noise. The
ceiling appears with catalogue depth: at 100 live hunts maintenance is
~£230K/yr forever, and it scales linearly — this is exactly the
recurring cost a competitor must also fund, which is why it is a moat, and
exactly the cost that caps authored-catalogue growth, which is why it is a
ceiling. The escape: a **managed player-verification loop** (Adventure Lab
model, not open UGC) — "verified in the last 90 days" badges earned by
players re-submitting counts, with 3–5 redundant confirmations and the
collect-mode engine already built to harvest them. Research says
trustworthy crowdsourced verification takes 2–5 years to mature — which is
why it must start in year 1, not when the ceiling bites.

### 6.2 Revenue model comparison

| Model | Price point | Verdict from the model |
|---|---|---|
| Per-hunt one-off | £10–15pp | Keep as entry product; never the engine. Proven ceiling (Questo). |
| Premium narrative events | £19–40pp | Year-2+ upsell in 2–3 cities; production-heavy (HiddenCity model). |
| **Corporate team-building** | £55–65pp | **The margin engine.** 40–43% of Y3 revenue in low/medium. Ops-heavy but London demand alone (~55K events/yr) dwarfs the need. |
| Subscription/season pass | ~£8–10/mo | Blocked by the content ceiling until player-verification matures. Revisit year 2. |
| **Venue sponsorship** | £2.5–60K/city/yr | **Uncontested.** Priced by Niantic/trail precedents; the pub finish is a built-in sales demo. |
| White-label (BIDs, museums, tourist boards) | £2.5–150K/deal | Highest £/effort at medium scale; councils demonstrably procure this. |
| Engine-as-SaaS | — | Don't. It arms copycats with the software layer while GooseChase owns DIY. |

### 6.3 Beachhead

The ladder (friends → public paid → corporate → licensing) survives
contact with the model; the 10-city simultaneous launch does not. A
London-deep year — one flagship free hunt + two paid + corporate sales +
3 sponsor deals + 1 council white-label — costs ~£200–250K all-in, proves
or disproves the medium-case conversion numbers, and leaves the brand
unlaunched in 9 cities (where a later launch is *stronger* for having
reviews, press, and a sponsorship rate card). The global launch then
becomes a marketing event executed from proven economics rather than a
£1–2M experiment. §9 quantifies the comparison.

### 6.4 Market sizing

Serviceable market across the 10 cities: **265K / 1.1M / 3.3M players/yr**
(low/medium/high capture), €3.2M–€40M gross. The model's scenarios stay
inside these ceilings (high uses ~⅓ of the mature-category ceiling in
year 1 — aggressive, defensible only in the viral narrative). The
under-modeled upside is day-trippers (~65M/yr across four of the cities,
excluded from the tourist base) and corporate (the model captures <0.2% of
London's team-event demand even in high).

### 6.5 Competitive response

What stops Questo or CityDays copying this? Nothing technical — and
that's the honest answer. $10–40K retrofits 10 cities. What actually
protects the position: (1) incumbents' economics and posture point away
from verification (Questo's 75% royalty split, Let's Roam's 3,000-city
breadth strategy, GooseChase's AI-generation direction); (2) they need a
forcing event to move, and the strongest forcing event — "AI solves every
Questo quest from a couch" — is **Fedora's own best press release**, a
card that can be played at a moment of choice; (3) the recurring
re-verification cost inverts breadth-first unit economics, so copying the
model means abandoning theirs. Expect the *claim* of AI-resistance to be
copied within months of it working (marketing is free); expect the
*operation* in 12–24; plan for positioning parity by year 3 and build the
community/data flywheel that outlives it.

### 6.6 Risks

- **Content decay** — the moat's own tax. Mitigated by re-check dates,
  ground-truth photos (both already methodology), and the
  player-verification loop. Let's Roam's review page is the cautionary
  benchmark and the sales pitch in one.
- **Ambiguity disputes** — an honest miscount frustrating a paying
  customer is the product's worst moment. Design margin (accept ±1 where
  sane), the strike budget, tiered hints, and a no-quibble refund policy
  are cheaper than churn; budgeted inside the 8% fee/support line.
- **Safety and trespass** — the genre's history is grim (Masquerade
  digging; Fenn's five deaths). The look-don't-touch design rule
  (nothing buried, nothing at height) is already policy; it needs to be
  a published safety charter and an insurance conversation before scale,
  and it is non-negotiable for council/BID contracts.
- **Seasonality and weather** — outdoor city play skews Apr–Oct and
  weekends; corporate bookings counter-cycle into December. Cashflow
  planning, not annual totals, carries the risk; the trough analysis in
  §4 assumes smooth months and is therefore ~10–15% optimistic on
  working-capital need.
- **Single-author dependence** — the methodology (attack → cut → verify →
  re-attack) is documented and repeatable; the *taste* is not yet. The
  first hire after traction should be a second setter trained on the
  London corpus, before city 11, not after.
- **Model risks** — the engine is deterministic and monthly; real
  virality is lumpier in both directions. The high case's launch-quarter
  install volume (1.9M) has precedent (Randonautica 10.8M/5mo) but no
  guarantee; the medium case is the planning baseline.

### 6.7 Is "the game AI can't play for you" a real wedge?

Be sceptical, as the handoff asks. The research found **zero evidence
customers buy on AI-resistance** — they buy a good day out; Let's Roam's
2.6★ Play rating punishes broken content, not cheatable content. But it
found strong evidence that AI-resistance works as **press and integrity**:
MIT Mystery Hunt's public LLM debate, SpeedQuizzing marketing
"AI-resistance", escape-room operators writing about ChatGPT — the
cultural moment is real in 2026, and no product owns it. Conclusion: it
is a *launch wedge* (the story journalists want to write) and a
*competition guarantee* (leaderboards and prizes are worthless if desk
teams can win — and prizes are what make corporate and sponsored events
valuable), not a checkout-page feature. Market the theatre; let the
AI-proofing be why the theatre stays true.

---

## 7. What was NOT modeled

Localisation costs for non-Anglophone cities (Paris/Rome/Barcelona tourist
bases shrink 30–40% English-only); FX; tax; team-scaling risk in the high
case (£110K/mo staff by year 3 implies ~15 people hired fast);
acquisition or licensing exits; any revenue from the collect-mode data
itself.

## 8. Reproducing and stress-testing

```
python3 docs/business/model/build_model.py            # scenario summary
python3 docs/business/model/build_model.py --csv out  # monthly detail
python3 docs/business/model/make_xlsx.py              # regenerate xlsx
```

Every assumption lives in one dict per scenario in `build_model.py` and
one blue cell per scenario in the spreadsheet — change either and the
scenarios recalculate.

## 9. Recommendation

The brief asked what the 10-city global launch makes. Answered: −£1M to
−£1.8M in the two likelier worlds, +£2.3M if it goes viral, with a ~£2M
funding requirement either way. The same research and model suggest a
strictly better-shaped bet with the same endpoint:

1. **Now – month 9: London-deep** (~£250K total). Wave-2 London paid
   hunts by month 5, corporate sales from month 3, three sponsor deals,
   one council/BID white-label. Targets that de-risk the global case:
   10% engaged-team conversion, £12K sponsorship/city-yr, 4 corporate
   events/mo. This is also when the player-verification loop starts.
2. **Months 9–18: expand on evidence.** Each new city launches only with
   an OTA listing live, a finish-pub sponsor signed (the sponsorship *is*
   the launch budget), and a local contractor retained for verification.
   Cities self-fund at ~£15K build + ~£20K launch against £10–15K
   year-one sponsorship + OTA sales.
3. **Month ~18: the "global launch" as a PR moment** — 10 cities live,
   the AI-challenge press story, and the armchair-hunt halo (a real
   prize, Masquerade-style, safely designed) — executed from proven unit
   economics, with the −£1.8M trough never incurred.
4. **Throughout: sell the B2B book** — corporate, sponsorship,
   white-label — because in every non-viral world that is the business,
   and it is the piece competitors can't clone with a $40K field trip.

The 10-city big bang remains the right call only if the goal is to
maximise the small chance of the viral outcome and ~£2.5M is available to
lose. In every other world, the ladder gets to the same 10 cities about a
year later, several hundred thousand pounds richer, with the moat already
compounding.
