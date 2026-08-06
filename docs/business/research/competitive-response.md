# Research appendix — competitive response speed & moat durability

*Deep-research sweep, 6 Aug 2026. Feeds the competitor-entry assumptions in
`../model/build_model.py` and the head-start analysis in the report.*

## 1. Cloning-speed precedents

- **Pokémon Go (Jul 2016):** ops-heavy clones took **22–39 months** even for
  Universal/WB/Microsoft (Jurassic World Alive ~22mo; Wizards Unite ~35mo;
  Minecraft Earth ~39mo) — and 2 of 3 died.
- **Wordle (Jan 2022):** zero-ops software cloned in **days** (~100 lines of
  JS; Apple purged App Store clones within the viral week). The software
  layer of a hunt app is a weekend-to-weeks problem.
- **Geocaching (2000):** idea copied within 6 months (NaviCache 2001) but the
  accumulated verified-location database + community was never replicated —
  Groundspeak unchallenged at 25 years.
- **Escape rooms:** UK 1 room (2013) → 598 (2016) → 1,500+ (2019); US ~30% of
  2015–17 openings closed by 2019, 40–50% Groupon discounting standard while
  mature venues held 40–55% EBITDA. **First local copy within 6–12 months of
  visible success; saturation in 36–48 months; then price competition.**
- **Randonautica:** no credible clone — the fad decayed before copying paid.
  Fast-followers mobilize only against durable traction.

## 2. Named competitors' capacity to respond

- **Questo:** pure UGC marketplace; QA = remote editorial + 10 real-world
  playtesters per quest (crowdsourced, not staff field verification). Only
  **~$2.1M lifetime funding**; Aug 2024 round (€630K) pitched around 500K
  users and a pivot toward *events*. 75% creator royalty leaves no margin to
  pay field verifiers.
- **CityDays:** closest in spirit (observational clues, handmade), 125+
  experiences/~40 cities, no evident capital for multi-city rollout.
- **Let's Roam:** breadth-first and demonstrably NOT verifying — reviews
  document outdated answers, wrong statues, "$80 for AI-generated content
  no one bothered to verify". 3,000-city coverage is only economical
  because nobody walks the routes; verification inverts their unit economics.
- **GooseChase:** moving the opposite way (AI Mission Generator, Apr 2025).
- **No incumbent shows any field-verification operation or AI-resistance
  signal.** Fedora would likely be first to name the category.

## 3. Cost for a competitor to replicate

The dollars are trivial: local contractor verification pass **$500–2,000 per
city** (Blue Badge guide £353/day; freelance writers ~$35/hr); flying someone
in $2,500–4,000/city. **Top-10-city retrofit ≈ $10K–40K.** The moat is not
capital: it is (a) clue-design + adversarial-AI-testing methodology, (b) the
recurring re-verification burden (the physical world drifts — Let's Roam's
complaint log proves unverified content rots), (c) accepting worse coverage
economics than the 3,000-city breadth strategy.

## 4. Operational-moat precedents

- **Michelin:** nobody out-inspected them in 100 years; erosion came from
  demand-side substitutes (TikTok), not copying.
- **Street View:** Apple took 12 years to ship a partial rival; crowdsourced
  Mapillary got breadth but poor quality.
- **OSM/Waze:** crowdsourcing catches operational moats in **5–8 years**
  (~2 years/region when data collection is passive). Active-labour
  verification sits at the slow end.
- **Adventure Lab:** managed UGC took ~5 years to 50k Adventures, gated
  creators + full-time review team — and quality still disputed.
- **Realistic fast attack:** not hiring measurers — a Questo-style conversion
  of existing players into verifiers (an app update, not an ops build).
  Friction buying time: quantitative ground truth is disputable, so
  trustworthy UGC verification needs 3–5 redundant confirmations + dispute
  resolution — the exact quality problem Mapillary/Let's Roam/early
  Adventure Lab hit.

## 5. Bottom-line planning estimates

| Event | Window | Central |
|---|---|---|
| (a) Startup fast-follower, comparable field-verified product, 1 city | 6–18 months **after traction is publicly visible** | ~9–12 mo |
| (b) Questo-class incumbent retrofits top 10 cities | 12–24 months **from deciding** (decision needs a forcing event — visible share loss or an "AI solved every Questo quest" press cycle) | ~18 mo |
| (c) AI-proof positioning stops differentiating | 24–48 months (crowdsourced verification 2–5 yrs; AI+imagery creep forces clue redesign toward off-camera detail; category convergence ~3–4 yrs per escape rooms) | ~36 mo |

**The operational verification alone buys roughly a 2–4 year exclusivity
window.** Its lasting value is the freshness flywheel: a "verified in the
last 90 days" guarantee is a recurring-cost moat competitors must fund
forever, not copy once. Spend the window converting verified answers into a
proprietary ground-truth dataset and a Geocaching-style community that
re-verifies for you — the difference between year 4 as HintHunt (surrounded
by 1,500 copies) and Groundspeak (unchallenged at 25).
