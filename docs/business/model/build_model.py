#!/usr/bin/env python3
"""Fedora global-launch economics — 3-year scenario engine.

Models the launch plan in the 6 Aug 2026 handoff: 10 cities at launch, one
field-verified hunt per city, first hunt free, big marketing push, paid
catalogue + local-business sponsorship + advertising from the second launch
wave (month 9). Produces monthly cashflows aggregated to years for
low / medium / high scenarios, plus "head start" metrics: what is banked by
the month a credible competitor lands.

Every assumption is grounded in the research appendices under
docs/business/research/ (sources + confidence ratings there):
  marketing-cac.md          CPI, conversion, retention, campaign costs, K
  sponsorship-economics.md  sponsor/ads/white-label price anchors
  market-sizing.md          demand ceilings per city
  competitive-response.md   competitor entry timing, post-entry effects
  competitor-pricing.md     ticket/corporate price anchors

All money in GBP (research $ converted at ~$1.27/£).

Usage:
    python3 docs/business/model/build_model.py            # print summary
    python3 docs/business/model/build_model.py --csv DIR  # also write CSVs
    python3 docs/business/model/build_model.py --json F   # summary as JSON
"""

import argparse
import csv
import json
import os
import sys

MONTHS = 36
N_CITIES = 10
TEAM_SIZE = 3.5          # avg players per team; one purchase covers a team
WAVE2_MONTH = 9          # paid catalogue + sponsorship + ads switch on

# ---------------------------------------------------------------------------
# ASSUMPTIONS. Sourcing notes inline; full citations in research appendices.
# ---------------------------------------------------------------------------

SHARED = {
    # Content operation (the moat and the ceiling).
    # Build = contracted design labour + field days + travel/local contractor
    # + adversarial AI red-team + QA. Core team salaries are NOT in these
    # numbers (they're in staff_monthly_yr) — these are incremental costs.
    # Anchors: Blue Badge guide £353/day; freelance writers ~$35/hr; business
    # travel ~$1,771/trip; competitor one-city verification pass $500-$2k.
    # Fedora-grade build (design + red-team + verify + ground-truth photos)
    # is several contractor-weeks, not a verification pass.
    "hunt_build_home": 8_000,
    "hunt_build_remote": 14_000,     # + travel or local contractor premium
    "hunt_maintain_yr_home": 1_200,  # quarterly re-verification (world drifts)
    "hunt_maintain_yr_remote": 2_500,
    "redteam_compute_per_hunt": 500, # frontier-model attack runs pre-ship
    # Platform (Supabase, hosting, tools; web-first per repo architecture)
    "platform_monthly": 800,
    "app_build_oneoff": 45_000,      # store-presence app wrapper + polish
    # Fees on direct consumer revenue: web checkout ~2-3% (Stripe UK
    # 1.5%+20p) blended with some store IAP at 15% (Small Business tiers)
    "fee_rate": 0.08,
    # OTA channel commission (GetYourGuide/Viator take 20-30%)
    "ota_commission": 0.25,
    # Corporate delivery cost share (host on the day, props, admin)
    "corp_delivery_rate": 0.35,
    # White-label delivery cost share (bespoke build + verification labour)
    "wl_delivery_rate": 0.45,
    # Monthly churn of the active repeat-buyer pool
    "payer_churn_mo": 0.05,
}

ASSUMPTIONS = {
    # ----- LOW: launch lands quietly; retrench toward home market ---------
    "low": {
        # CPI blended tier-1 cities: high end $4.70≈£3.70 (marketing-cac §1)
        "cpi": 3.70,
        # PR/WoM uplift on paid installs, by year; weak spike, little referral
        "organic_mult_yr": [1.25, 1.2, 1.2],
        # installs that actually start the free hunt (D1-retention-like)
        "install_to_active": 0.22,
        # engaged (finished free hunt) teams buying when catalogue lands /
        # ongoing. Freemium median is 2.1% of installs ≈ 7-10% of activated
        # (marketing-cac §2); low case sits well under that.
        "backlog_conv": 0.03,
        "ongoing_conv": 0.05,
        "repeats_per_payer_yr": 0.5,
        # £/team ≈ £11-14/head: between Questo (€8-20pp) and CityDays (£15-25pp)
        "price_per_team": 40.0,
        # OTA teams/city/month by year (paid hunts listable from wave 2)
        "ota_teams_city_mo_yr": [0, 2, 4],
        # Marketing: "scrappy" 10-city launch £250k yr1 (marketing-cac §3),
        # then cut hard when it isn't working
        "mkt_launch_burst": 160_000,   # months 0-2
        "mkt_monthly_yr": [7_000, 5_000, 5_000],
        # Sponsorship (sponsorship-economics: £2.5-4k/city/yr, few cities)
        "sponsor_per_city_yr": 3_000,
        "sponsor_cities_ramp": [2, 5, 8],
        # White-label deals/yr and value (SaaS-parity £2.5-5k)
        "wl_deals_yr": [0, 1, 2],
        "wl_value": 4_000,
        # Ads: ~$10 per 1k MAU/mo (episodic use)
        "ad_rev_per_1k_mau_mo": 8.0,
        # Corporate: hosted events, home city only
        "corp_events_mo_yr": [0, 1.0, 2.0],
        "corp_rev_per_event": 1_500,
        # Core team shrinks to near-solo after a quiet launch, fully loaded
        "staff_monthly_yr": [10_000, 8_000, 8_000],
        # Content roadmap: wave-2 paid hunts only in top 5 cities, then trickle
        "new_hunts_yr": [5, 3, 3],
        # Prune dead cities: fraction of catalogue still maintained
        "prune_factor_yr": [1.0, 0.6, 0.5],
        # Competition: little traction ⇒ nobody hurries (and it matters less)
        "competitor_entry_month": 30,
        "post_entry_growth_dampener": 0.85,
        "post_entry_price_factor": 0.95,
    },
    # ----- MEDIUM: solid regional hit; category gets named ----------------
    "medium": {
        "cpi": 2.40,                   # median $3.00
        # Referral loop + press working at launch; spike decays (Randonautica)
        "organic_mult_yr": [1.8, 1.6, 1.5],
        "install_to_active": 0.30,
        "backlog_conv": 0.06,
        "ongoing_conv": 0.10,          # ≈ freemium median at team level
        "repeats_per_payer_yr": 1.0,
        "price_per_team": 45.0,
        "ota_teams_city_mo_yr": [0, 10, 20],
        "mkt_launch_burst": 400_000,   # "plan" 10-city campaign £550-800k yr1
        # Paid UA is underwater at these conversions (CAC/team > LTV), so a
        # competent operator shifts spend to PR/creators/OTA after year 1
        "mkt_monthly_yr": [27_000, 18_000, 15_000],
        "sponsor_per_city_yr": 12_000, # full sponsor slate + a gold tier
        "sponsor_cities_ramp": [5, 8, 10],
        "wl_deals_yr": [1, 3, 6],      # Ipswich-anchor £10-25k deals
        "wl_value": 15_000,
        "ad_rev_per_1k_mau_mo": 25.0,
        "corp_events_mo_yr": [1.0, 4.0, 8.0],
        "corp_rev_per_event": 2_500,   # ClueGo £55-65pp × 25-40 heads
        "staff_monthly_yr": [22_000, 30_000, 35_000],
        "new_hunts_yr": [10, 8, 8],
        "prune_factor_yr": [1.0, 1.0, 1.0],
        # Fast-follower ~9-12mo after traction visible ⇒ ~m21
        "competitor_entry_month": 21,
        "post_entry_growth_dampener": 0.80,
        "post_entry_price_factor": 0.90,
    },
    # ----- HIGH: the launch is a cultural moment ---------------------------
    "high": {
        "cpi": 1.20,                   # low-end $1.50; virality carries UA
        # Randonautica-style creator wave at launch; viral spikes decay fast
        "organic_mult_yr": [2.5, 1.8, 1.5],
        "install_to_active": 0.38,
        "backlog_conv": 0.10,
        "ongoing_conv": 0.18,          # under the 48% travel trial→paid ceiling
        "repeats_per_payer_yr": 1.5,
        "price_per_team": 50.0,
        "ota_teams_city_mo_yr": [0, 25, 60],
        "mkt_launch_burst": 900_000,   # "heavy" £1.5M+ yr1
        "mkt_monthly_yr": [55_000, 45_000, 40_000],
        "sponsor_per_city_yr": 40_000, # BID/council commissions + trail tiers
        "sponsor_cities_ramp": [8, 10, 10],
        "wl_deals_yr": [2, 6, 12],
        "wl_value": 40_000,
        "ad_rev_per_1k_mau_mo": 80.0,
        "corp_events_mo_yr": [2.0, 8.0, 16.0],
        "corp_rev_per_event": 3_000,
        "staff_monthly_yr": [35_000, 70_000, 110_000],
        "new_hunts_yr": [10, 15, 20],
        "prune_factor_yr": [1.0, 1.0, 1.0],
        # Visible splash at launch ⇒ follower at 6-18mo, central ~m15
        "competitor_entry_month": 15,
        "post_entry_growth_dampener": 0.75,
        "post_entry_price_factor": 0.85,
    },
}


def year_of(month):
    return min(month // 12, 2)


def run_scenario(name):
    a = {**SHARED, **ASSUMPTIONS[name]}
    rows = []
    cum_active_teams = 0.0
    cum_players = 0.0
    cum_net = 0.0
    backlog_pool = 0.0          # engaged teams awaiting wave-2 catalogue
    paying_teams_base = 0.0     # teams that have ever paid (repeat pool)
    live_hunts = N_CITIES       # free launch hunts

    for m in range(MONTHS):
        yr = year_of(m)
        post_entry = m >= a["competitor_entry_month"]
        dampen = a["post_entry_growth_dampener"] if post_entry else 1.0
        price = a["price_per_team"] * (a["post_entry_price_factor"] if post_entry else 1.0)

        # --- acquisition (app funnel) ---
        mkt = (a["mkt_launch_burst"] / 3 if m < 3 else a["mkt_monthly_yr"][yr])
        installs = (mkt / a["cpi"]) * a["organic_mult_yr"][yr] * dampen
        new_active_players = installs * a["install_to_active"]
        new_active_teams = new_active_players / TEAM_SIZE
        cum_active_teams += new_active_teams
        cum_players += new_active_players

        # --- consumer paid revenue, direct (from wave 2) ---
        # new_payers join the repeat pool; repeat purchases don't grow it and
        # the pool churns. Repeats capped by catalogue release rate (a payer
        # can't buy hunts that don't exist in their city).
        new_payers = 0.0
        if m < WAVE2_MONTH:
            backlog_pool += new_active_teams
        else:
            if backlog_pool > 0:  # backlog converts over 3 months
                tranche = backlog_pool / 3 if m < WAVE2_MONTH + 2 else backlog_pool
                new_payers += tranche * a["backlog_conv"]
                backlog_pool -= tranche
            new_payers += new_active_teams * a["ongoing_conv"]
        catalogue_cap_yr = a["new_hunts_yr"][yr] / N_CITIES
        repeat_rate = min(a["repeats_per_payer_yr"], catalogue_cap_yr) / 12
        repeat_purchases = paying_teams_base * repeat_rate
        paid_teams = new_payers + repeat_purchases
        paying_teams_base = paying_teams_base * (1 - a["payer_churn_mo"]) + new_payers
        direct_net = paid_teams * price * (1 - a["fee_rate"])

        # --- consumer paid revenue via OTA listings (from wave 2) ---
        ota_teams = (a["ota_teams_city_mo_yr"][yr] * N_CITIES * dampen
                     if m >= WAVE2_MONTH else 0.0)
        ota_net = ota_teams * price * (1 - a["ota_commission"])
        cum_players += ota_teams * TEAM_SIZE * 0.5   # half are app-new

        # --- sponsorship, white-label, ads, corporate ---
        sponsor = (a["sponsor_cities_ramp"][yr] * a["sponsor_per_city_yr"] / 12
                   if m >= WAVE2_MONTH else 0.0)
        wl_rev = a["wl_deals_yr"][yr] * a["wl_value"] / 12
        wl_cost = wl_rev * a["wl_delivery_rate"]
        mau = new_active_players + 0.08 * cum_players
        ads = (mau / 1000) * a["ad_rev_per_1k_mau_mo"] if m >= WAVE2_MONTH else 0.0
        corp_rev = a["corp_events_mo_yr"][yr] * a["corp_rev_per_event"]
        corp_cost = corp_rev * a["corp_delivery_rate"]

        # --- content costs ---
        build = 0.0
        if m == 0:  # initial 10 hunts booked at launch (built pre-launch)
            build += (a["hunt_build_home"] + a["redteam_compute_per_hunt"]
                      + (N_CITIES - 1) * (a["hunt_build_remote"] + a["redteam_compute_per_hunt"]))
        monthly_new = a["new_hunts_yr"][yr] / 12
        build += monthly_new * (a["hunt_build_remote"] * 0.9 + a["redteam_compute_per_hunt"])
        live_hunts += monthly_new
        home_share = 0.15
        maintain = live_hunts * a["prune_factor_yr"][yr] * (
            home_share * a["hunt_maintain_yr_home"]
            + (1 - home_share) * a["hunt_maintain_yr_remote"]) / 12

        # --- fixed costs ---
        app = a["app_build_oneoff"] if m == 0 else 0.0
        staff = a["staff_monthly_yr"][yr]
        platform = a["platform_monthly"]

        revenue = direct_net + ota_net + sponsor + wl_rev + ads + corp_rev
        costs = (mkt + build + maintain + app + staff + platform
                 + corp_cost + wl_cost)
        net = revenue - costs
        cum_net += net

        rows.append(dict(
            month=m, year=yr + 1, installs=installs,
            active_players=new_active_players, cum_players=cum_players,
            mau=mau, direct_net=direct_net, ota_net=ota_net, sponsor=sponsor,
            white_label=wl_rev, ads=ads, corp=corp_rev,
            revenue=revenue, marketing=mkt, content=build + maintain,
            staff=staff, other=app + platform + corp_cost + wl_cost,
            costs=costs, net=net, cum_net=cum_net,
        ))

    # Head-start metrics: what is banked before the competitor-entry month
    e = a["competitor_entry_month"]
    banked_at_entry = None
    if 0 < e < MONTHS:
        banked_at_entry = {
            "month": e,
            "cum_revenue": sum(r["revenue"] for r in rows[:e]),
            "cum_net": rows[e - 1]["cum_net"],
            "players": rows[e - 1]["cum_players"],
        }

    return rows, banked_at_entry


def annual(rows, key):
    out = [0.0, 0.0, 0.0]
    for r in rows:
        out[r["year"] - 1] += r[key]
    return out


REV_KEYS = ("direct_net", "ota_net", "sponsor", "white_label", "ads", "corp")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", metavar="DIR", help="write per-scenario monthly CSVs")
    ap.add_argument("--json", metavar="FILE", help="write summary JSON")
    args = ap.parse_args()

    summary = {}
    for name in ("low", "medium", "high"):
        rows, entry = run_scenario(name)
        summary[name] = {
            "annual_revenue": annual(rows, "revenue"),
            "annual_costs": annual(rows, "costs"),
            "annual_net": annual(rows, "net"),
            "cum_net_36m": rows[-1]["cum_net"],
            "players_36m": sum(r["active_players"] for r in rows),
            "trough_cash": min(r["cum_net"] for r in rows),
            "banked_at_competitor_entry": entry,
            "revenue_mix_yr3": {k: annual(rows, k)[2] for k in REV_KEYS},
        }
        if args.csv:
            os.makedirs(args.csv, exist_ok=True)
            with open(os.path.join(args.csv, f"{name}.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)

    for name, s in summary.items():
        print(f"\n=== {name.upper()} ===")
        for i in range(3):
            print(f"  Y{i+1}: revenue £{s['annual_revenue'][i]:>10,.0f}   "
                  f"costs £{s['annual_costs'][i]:>10,.0f}   "
                  f"net £{s['annual_net'][i]:>10,.0f}")
        print(f"  36m cumulative net: £{s['cum_net_36m']:,.0f}   "
              f"(cash trough £{s['trough_cash']:,.0f})")
        print(f"  players reached: {s['players_36m']:,.0f}")
        mix = s["revenue_mix_yr3"]
        total = sum(mix.values()) or 1
        mix_str = ", ".join(f"{k} {v/total:.0%}" for k, v in mix.items() if v > 0)
        print(f"  yr-3 revenue mix: {mix_str}")
        e = s["banked_at_competitor_entry"]
        if e:
            print(f"  at competitor entry (m{e['month']}): "
                  f"revenue banked £{e['cum_revenue']:,.0f}, "
                  f"cash position £{e['cum_net']:,.0f}, "
                  f"players {e['players']:,.0f}")
    if args.json:
        with open(args.json, "w") as f:
            json.dump(summary, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
