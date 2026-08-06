#!/usr/bin/env python3
"""Fedora global-launch economics — 3-year scenario engine.

Models the launch plan in the 6 Aug 2026 handoff: 10 cities at launch, one
field-verified hunt per city, first hunt free, big marketing push, paid
catalogue + local-business sponsorship + advertising from the second launch
wave. Produces monthly cashflows aggregated to years for low / medium / high
scenarios, plus "head start" metrics: what is banked by the month a credible
competitor lands.

All money in GBP. Assumptions live in ASSUMPTIONS below; every number there
is documented in docs/business/global-launch-economics.md with sources.

Usage:
    python3 docs/business/model/build_model.py            # print summary
    python3 docs/business/model/build_model.py --csv DIR  # also write CSVs
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
HOME_CITY = "London"

# ---------------------------------------------------------------------------
# ASSUMPTIONS — every value here must be sourced in the report before use.
# Scenario keys: low / medium / high.
# ---------------------------------------------------------------------------

SHARED = {
    # Content operation (the moat and the ceiling)
    "hunt_build_home": 9_000,        # design+field+red-team+QA, home city
    "hunt_build_remote": 16_000,     # + travel/local contractor
    "hunt_maintain_yr_home": 1_500,  # re-verification visits, fixes
    "hunt_maintain_yr_remote": 3_000,
    "redteam_compute_per_hunt": 500, # AI attack runs pre-ship
    # Platform
    "platform_monthly": 800,         # Supabase/hosting/tools at scale
    "app_build_oneoff": 45_000,      # native app wrapper + polish for launch
    # Fees on consumer revenue (blend of store cut / Stripe)
    "fee_rate": 0.20,
    # Corporate delivery cost as share of corporate revenue (host, props)
    "corp_delivery_rate": 0.35,
    # Monthly churn of the active repeat-buyer pool (lapse rate)
    "payer_churn_mo": 0.05,
}

ASSUMPTIONS = {
    "low": {
        # Demand
        "cpi": 3.00,                   # blended cost per install
        "organic_mult": 1.25,          # installs = paid * mult (PR/WoM uplift)
        "install_to_active": 0.22,     # installs that actually start the free hunt
        "backlog_conv": 0.03,          # engaged teams buying when paid catalog lands
        "ongoing_conv": 0.04,          # new engaged teams that buy a paid hunt
        "repeats_per_payer_yr": 0.6,   # further paid hunts per paying team per year
        "price_per_team": 40.0,        # gross, ~£11.50/head at 3.5 heads
        # Marketing (launch burst then trickle)
        "mkt_launch_burst": 150_000,   # months 0-2
        "mkt_monthly_after": 8_000,
        # Sponsorship / ads from wave 2
        "sponsor_per_city_yr": 4_000,  # one finish-pub deal per city
        "sponsor_cities_ramp": [3, 6, 8],   # cities with sponsors, yr1/2/3
        "ad_rev_per_1k_mau_mo": 4.0,
        # Corporate (home city only in low)
        "corp_events_mo_yr": [0, 1.0, 2.0],  # events/month by year
        "corp_rev_per_event": 2_200,
        # Team (founders + contractors), fully loaded per month
        "staff_monthly_yr": [12_000, 15_000, 15_000],
        # Content roadmap: new paid hunts per year beyond the free 10
        "new_hunts_yr": [10, 4, 4],    # wave-2 paid hunt per city, then top-ups
        # Competition
        "competitor_entry_month": 30,  # nobody hurries to copy a quiet product
        "post_entry_growth_dampener": 0.85,
        "post_entry_price_factor": 0.95,
    },
    "medium": {
        "cpi": 2.20,
        "organic_mult": 1.6,
        "install_to_active": 0.30,
        "backlog_conv": 0.06,
        "ongoing_conv": 0.08,
        "repeats_per_payer_yr": 1.0,
        "price_per_team": 45.0,
        "mkt_launch_burst": 400_000,
        "mkt_monthly_after": 25_000,
        "sponsor_per_city_yr": 12_000,
        "sponsor_cities_ramp": [5, 8, 10],
        "ad_rev_per_1k_mau_mo": 6.0,
        "corp_events_mo_yr": [0.5, 3.0, 6.0],
        "corp_rev_per_event": 2_600,
        "staff_monthly_yr": [18_000, 30_000, 40_000],
        "new_hunts_yr": [10, 10, 10],
        "competitor_entry_month": 21,
        "post_entry_growth_dampener": 0.80,
        "post_entry_price_factor": 0.90,
    },
    "high": {
        "cpi": 1.60,                   # viral positioning lowers blended CPI
        "organic_mult": 2.2,
        "install_to_active": 0.38,
        "backlog_conv": 0.10,
        "ongoing_conv": 0.12,
        "repeats_per_payer_yr": 1.6,
        "price_per_team": 50.0,
        "mkt_launch_burst": 900_000,
        "mkt_monthly_after": 60_000,
        "sponsor_per_city_yr": 30_000,
        "sponsor_cities_ramp": [8, 10, 10],
        "ad_rev_per_1k_mau_mo": 8.0,
        "corp_events_mo_yr": [1.0, 6.0, 14.0],
        "corp_rev_per_event": 3_000,
        "staff_monthly_yr": [25_000, 55_000, 85_000],
        "new_hunts_yr": [10, 14, 20],
        "competitor_entry_month": 15,  # success attracts fast followers
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
    cum_net = 0.0
    backlog_pool = 0.0          # engaged teams awaiting wave-2 catalogue
    paying_teams_base = 0.0     # teams that have ever paid (repeat pool)
    live_hunts = N_CITIES       # free launch hunts
    banked_at_entry = None

    for m in range(MONTHS):
        yr = year_of(m)
        post_entry = m >= a["competitor_entry_month"]
        dampen = a["post_entry_growth_dampener"] if post_entry else 1.0
        price = a["price_per_team"] * (a["post_entry_price_factor"] if post_entry else 1.0)

        # --- acquisition ---
        mkt = (a["mkt_launch_burst"] / 3 if m < 3 else a["mkt_monthly_after"])
        installs = (mkt / a["cpi"]) * a["organic_mult"] * dampen
        new_active_players = installs * a["install_to_active"]
        new_active_teams = new_active_players / TEAM_SIZE
        cum_active_teams += new_active_teams

        # --- consumer paid revenue (from wave 2) ---
        # new_payers join the repeat pool; repeat purchases don't grow it, and
        # the pool churns. Repeats are capped by catalogue release rate (a
        # payer can't buy hunts that don't exist in their city).
        new_payers = 0.0
        if m < WAVE2_MONTH:
            backlog_pool += new_active_teams
        else:
            if backlog_pool > 0:  # backlog converts over 3 months
                tranche = backlog_pool / 3 if m < WAVE2_MONTH + 2 else backlog_pool
                new_payers += tranche * a["backlog_conv"]
                backlog_pool -= tranche
            new_payers += new_active_teams * a["ongoing_conv"]
        catalogue_cap_yr = a["new_hunts_yr"][yr] / N_CITIES  # new hunts/city/yr
        repeat_rate = min(a["repeats_per_payer_yr"], catalogue_cap_yr) / 12
        repeat_purchases = paying_teams_base * repeat_rate
        paid_teams = new_payers + repeat_purchases
        paying_teams_base = paying_teams_base * (1 - a["payer_churn_mo"]) + new_payers
        consumer_gross = paid_teams * price
        consumer_net = consumer_gross * (1 - a["fee_rate"])

        # --- sponsorship, ads, corporate ---
        sponsor = (a["sponsor_cities_ramp"][yr] * a["sponsor_per_city_yr"] / 12
                   if m >= WAVE2_MONTH else 0.0)
        mau = new_active_players + 0.35 * (cum_active_teams * TEAM_SIZE - new_active_players) * 0.1
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
        maintain = live_hunts * (
            home_share * a["hunt_maintain_yr_home"]
            + (1 - home_share) * a["hunt_maintain_yr_remote"]) / 12

        # --- fixed costs ---
        app = a["app_build_oneoff"] if m == 0 else 0.0
        staff = a["staff_monthly_yr"][yr]
        platform = a["platform_monthly"]

        revenue = consumer_net + sponsor + ads + corp_rev
        costs = mkt + build + maintain + app + staff + platform + corp_cost
        net = revenue - costs
        cum_net += net

        if banked_at_entry is None and post_entry:
            banked_at_entry = {
                "month": m,
                "cum_revenue": sum(r["revenue"] for r in rows),
                "cum_net": cum_net - net,
                "players": cum_active_teams * TEAM_SIZE,
            }

        rows.append(dict(
            month=m, year=yr + 1, installs=installs,
            active_players=new_active_players, mau=mau,
            consumer_net=consumer_net, sponsor=sponsor, ads=ads,
            corp=corp_rev, revenue=revenue, marketing=mkt,
            content=build + maintain, staff=staff,
            other=app + platform + corp_cost, costs=costs,
            net=net, cum_net=cum_net,
        ))

    return rows, banked_at_entry


def annual(rows, key):
    out = [0.0, 0.0, 0.0]
    for r in rows:
        out[r["year"] - 1] += r[key]
    return out


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
            "peak_monthly_burn": min(r["net"] for r in rows),
            "banked_at_competitor_entry": entry,
            "revenue_mix_yr3": {
                k: annual(rows, k)[2]
                for k in ("consumer_net", "sponsor", "ads", "corp")
            },
        }
        if args.csv:
            os.makedirs(args.csv, exist_ok=True)
            path = os.path.join(args.csv, f"{name}.csv")
            with open(path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)

    for name, s in summary.items():
        print(f"\n=== {name.upper()} ===")
        for i in range(3):
            print(f"  Y{i+1}: revenue £{s['annual_revenue'][i]:>10,.0f}   "
                  f"costs £{s['annual_costs'][i]:>10,.0f}   "
                  f"net £{s['annual_net'][i]:>10,.0f}")
        print(f"  36m cumulative net: £{s['cum_net_36m']:,.0f}")
        print(f"  players reached: {s['players_36m']:,.0f}")
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
