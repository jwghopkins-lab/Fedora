# Research appendix — user-acquisition & launch-marketing benchmarks

*Deep-research sweep, 6 Aug 2026 (data 2024–Q1 2026). Feeds acquisition
assumptions in `../model/build_model.py`. Confidence: H/M/L as noted.
£ figures assume ~$1.27/£.*

## 1. CPI benchmarks

- Global Q1 2026: iOS **$5.84**, Android **$1.92** (Digital Applied; M).
  Broader envelope $1–6 (Business of Apps, Mapendo; H).
- Travel apps: $1.40 global avg, **$3–6 US**; other aggregators $4.20 avg (M).
- Casual games (Liftoff/Singular, 2.5B installs): iOS $1.41 / Android $0.14
  median (H). Entertainment: cheapest cluster, plan $1.50–3.50 (L–M).
- Geography: North America $2.50–5.00; Western Europe/UK $2.00–4.00 (M).
- Channels: Apple Search Ads CPI ~$1.40–1.80 (cheapest high-intent); Google
  App Campaigns $1.50–4.50; Meta $2.00–5.50; TikTok $1.75–4.00 (H on ranges).
- **Planning range, tier-1 cities blended: low $1.50 / median $3.00 / high $6.00.**

## 2. Conversion & retention

- Freemium mobile: median **~2.1% of downloads ever convert to paid**
  (RevenueCat, 115k+ apps; H) vs 12.1% for hard paywall. Travel
  install→purchase 2.41% (UXCam; M).
- **Activated users convert far better:** 42% of signed-up travel users
  transact in month 1 (CleverTap); travel trial→paid median 48.7%
  (RevenueCat 2025). Activated→paid planning range **10% / 20–30% / 48%**.
- Day-30 retention: entertainment 3.2–3.8%, travel ~3.6% — steepest
  drop-offs of any category; episodic use is structural (H). Build the model
  on per-hunt transactions and referral, not DAU.

## 3. Launch campaign costs

- PR: boutique retainers $3.5–10k/mo; launch projects regional $15–25k,
  national $50–75k+ (H).
- Micro-influencers (10k–100k): IG post $150–500; TikTok $200–800. A
  per-city wave of 10–20 micros × 2–3 deliverables = **$5–15k/city** (H).
- Paid social city launch: UK guidance £15–50k first 3 months; launch-year
  app budgets $10–200k, $50k practical middle (M).
- Case studies — **organic dominated every success**: Pokémon GO (~no paid
  launch, 500M installs/2mo); Randonautica (~$0 paid, 10.8M downloads off
  TikTok, decayed in months); Zombies, Run! (Kickstarter launch, 11.6M
  lifetime downloads, ~$7.9M lifetime revenue, ~300k MAU / ~50k paying,
  sold $6.65M + earnout). Real-world-visible gameplay is itself an
  acquisition channel; spikes decay fast; niche real-world games can
  sustain a business on ~zero paid UA.

## 4. App store economics (2026)

- Apple Small Business Program 15% (<$1M/yr); Google 15% first $1M (H).
- US external purchase links currently 0% Apple commission (Epic injunction;
  holds through 2026 launch window, litigation-dependent). EU DMA link-out
  applies; Google drops external-billing fee US/UK/EEA after Jun 2026.
- Stripe web checkout: UK 1.5% + 20p; US 2.9% + $0.30. **Web checkout ~2–3%
  vs 15% IAP — selling hunts on the web is worth ~13 points of margin.**

## 5. K-factor / word of mouth / team structure

- Consumer apps K = 0.1–0.5; good referral programme 0.5–0.8 (M).
- Referral programmes drive 20–35% of installs at maturity; referred users
  +37% D30 retention; effective CPI cut 40–60% (M, vendor data).
- **Structural advantage: one buyer mechanically onboards ~3 teammates —
  built-in K≈3 on exposure.** Measure CAC per team. Escape rooms (closest
  offline analogue) run on word of mouth and corporate group bookings.

## 6. Blended CAC at experience marketplaces

- **Viator/Tripadvisor 10-K: marketing = 67–71% of revenue, 2022–2024**
  ($562M in 2024). Paid acquisition of experience-bookers is brutally
  expensive (H — SEC-filed).
- GetYourGuide: €1B revenue FY2025, adj-EBITDA profitable, €4B+ GMV; take
  rate 20–35%; CAC undisclosed. Tour operators typically spend 12–15% of
  revenue on direct acquisition (M).
- Questo (closest comp): raised only $1.5M, 3,000+ quests / 1,000+ cities,
  grew via creator marketplace + OTA distribution, not paid UA (M).
- **OTA listing at 20–30% commission ≈ £3 per £12 ticket vs ~£95–120 paid
  CAC per buying team — distribution beats paid funnel by ~30×.**

## Planning numbers (used in the model)

| Metric | Low | Plan | High |
|---|---|---|---|
| CPI blended, tier-1 cities | $1.50 (£1.20) | $3.00 (£2.40) | $6.00 (£4.70) |
| Install → paying buyer | 1.0% | 2.0–2.5% | 5% |
| Activated → paid conversion | 10% | 20–30% | 48% |
| Day-30 retention | 2% | 3.5% | 6% |
| Paid CAC per buying team | ~$60 | ~$120–150 | ~$300+ |
| K-factor with referral loop | 0.3 | 0.5 | 0.8–1.0 spike |
| One-city launch (3-month) | £20k | £50–75k | £120k |
| **10-city global campaign, launch quarter + yr-1 support** | **£250k** | **£550–800k** | **£1.5M+** |

**Bottom line:** weight the 10-city budget toward per-city creator waves, PR
moments, OTA/marketplace distribution and a referral loop that exploits the
1-buyer-brings-3-players structure; paid social is amplification, not engine.
