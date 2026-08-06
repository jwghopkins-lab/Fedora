# Research appendix — sponsorship & local-advertising economics

*Deep-research sweep, 6 Aug 2026. Feeds the sponsorship/ads assumptions in
`../model/build_model.py` and the revenue analysis in
`../global-launch-economics.md`. Confidence: High = multiple corroborating
sources or primary source; Medium = single credible trade source; Low =
indirect/estimated or dated.*

## 1. What businesses pay for delivered foot traffic

- **UK pub spend per head (2025–26): £18.51–£26.89 per visit** (CGA/Morning
  Advertiser trackers; £24.59 avg for 52 weeks to Jun 2025). A group of 4
  spends **£75–108** at the finish pub. — High.
  (morningadvertiser.co.uk 2026-02-11 & 2026-05-19; whito.co.uk/research/uk-pub-marketing-data)
- **Repeat-customer value:** £24.59/visit twice a month ≈ **£590/year**;
  weekly at £30 ≈ £1,560/year. — Medium.
- **Restaurant/hospitality CAC (US-heavy): $30–120 per new customer**;
  paid channels $27–83/guest. A pub paying £3–10 per genuinely delivered new
  head is well inside industry norms. — High.
  (7shifts.com, get.chownow.com, merchants.doordash.com)
- **Google's own store-visit example value: $25 per walk-in** (Performance
  Max for Store Goals docs). Anchor only, not a market-clearing price. — High/Low.
- **Geofenced location ads: $6–15 CPM** (~$0.01 per impression). A verified
  physical visit is worth 1–2 orders of magnitude more than an impression. — High.

## 2. Local sponsorship price anchors

- **Community event tiers (UK, published tariffs):** Bronze £150–250, Silver
  £1,000, Gold £2,500 (Runnymede civic awards; Farnham TC from £500+VAT). — High.
- **Sculpture/art trails — closest comp to "sponsor a clue location":**
  Wild in Art-style trails charge **£6,000–8,000 +VAT per sculpture** for a
  10–12-week marketed city trail (Pride of Yorkshire, Doncaster 2026; Wild in
  Art: 190+ trails). Strongest evidence local businesses pay £6–8k to be a
  named stop. — High.
- **Local run/5K sponsorship:** $150–1,000 small events; parkrun sells only
  national partnerships. — Medium.
- **UK SME marketing budgets: £400–2,500/month** (avg client ~£900–1,200/mo).
  A £50–150/month sponsorship is 5–20% of budget — an easy yes; £500+/mo
  competes with their Google Ads line. — High.

## 3. Tourist boards / BIDs / museums

- **UK BID levy income: £448k/year average** (British BIDs 2023); range
  £15k–£4.1m. A £5–25k commission is 1–5% of a typical budget. — High.
- **BIDs already buy this:** Downtown LA BID ran Eventzee scavenger hunts to
  push visitors to businesses. Eventzee: $49.99 pre-built packs; custom
  events priced per player. — Medium (pricing), High (precedent).
- **Public procurement anchors:** Ipswich BC AR heritage trail → Go Jauntly
  **£22,845**; Derry Girls immersive trail **£346,325** (2026–31); Stevenage
  arts & heritage trail **£800,000** (incl. physical build). The Ipswich
  award is the best "a council pays this for a digital trail" anchor. — High.
- **Geocaching GeoTours:** destinations pay **~$2,500/year** listing; a
  50-cache GeoTour cost ~$12,000 to set up (South Downs case study). — Medium.
- **Museum audio-guide/white-label:** platform plans ~$2,500–3,000/yr
  (STQRY); listing in an existing guide app $750–800/yr; fully custom app
  $70,000–150,000 + $40,000/yr. White-label sweet spot **£3k–25k**. — High.

## 4. In-app advertising reality check

- eCPMs Tier-1 2025: banner $0.50–1.50, interstitial $5–8, rewarded $15–30. — High.
- Ad-only monetization averages **~$0.04 per user per month**. — Medium-High.
- Treasure-hunt usage is episodic → realistic **$10–50 per 1,000 MAU per
  month**. At 10k–100k MAU that is **£1k–30k/year — a rounding error next to
  sponsorship**. Only sponsor-funded native placements (really sponsorship)
  are material. — High confidence in conclusion.

## 5. Direct precedents

- **Niantic/Pokémon GO sponsored locations (key anchor):** officially
  "partners spend **less than $0.50 per daily unique visit**"; initial exec
  figure $0.15/visitor. A "visit" is a weak in-game interaction — a verified
  group physically finishing at a pub justifies a multiple. — High.
- **Niantic SMB flat rates (2019):** **$30/month sponsored PokéStop,
  $60/month sponsored Gym** = $360–720/year per location. Best per-SMB
  subscription anchor. — High.
- **McDonald's Japan:** 3,000 stores, ~2,000 game visitors/store/day at peak. — Medium.
- **Foursquare:** merchant CPA per check-in validated, rates unpublished,
  later pivoted to data licensing. — Medium.
- **Peers monetize consumers, not venues:** Questo €8–20/quest, creators keep
  up to 75%, distributes via TripAdvisor/GetYourGuide/Expedia; Secret City
  Trails 60+ cities, creator fee + 25% share. **Venue-side monetization is
  untapped by direct competitors.** — High.
- **UK corporate treasure hunts:** £12–16+ pp; self-managed packages ~£140;
  managed events £550–850. — High.
- **Referral norms:** walking tours ~10% commission; Viator pays hosts 8%.
  10% of a £75–108 group tab = £8–11/group. — Medium.

## Planning numbers (used in the model)

| Planning number | Low | Medium | High |
|---|---|---|---|
| Till value of a delivered group of 4 at a pub | £75 | £90 | £108 |
| Defensible per-delivered-group fee to pub | £4 | £10–12 | £25–40 |
| Per-SMB clue-location sponsor | £25–50/mo | £60–100/mo | £200+/mo |
| Per-city annual sponsorship revenue | £2,500–4,000 | £8,000–15,000 | £30,000–60,000 |
| White-label deal (museum/BID/council) | £2,500–5,000/yr | £10,000–25,000 | £50,000–150,000 |
| Ad revenue per 1,000 MAU/month | $10 | $25–40 | $100 |
| Annual ads at 10k/100k MAU | £1k/£10k | £3k/£30k | £9k/£90k |

**Bottom line:** the market has already priced every component. Venue-side
monetization has a proven ceiling (Niantic) and floor (community event
tiers); advertising is garnish; sponsorship and white-label commissions are
the meal.
