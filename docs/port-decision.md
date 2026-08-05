# What was ported from TRIVIUM, and what was deliberately left behind

Fedora reuses parts of the TRIVIUM crossword pipeline
(`jwghopkins-lab/greyhound2`, branch `claude/ai-crossword-generator-research-2iemh5`,
`poc/crossword/pipeline/`, per its `REUSE.md`). Everything is a **copy** —
Fedora shares no files, paths, database tables or infrastructure with the live
TRIVIUM app. Decision recorded 5 Aug 2026.

## Ported

| Fedora file | Source | What changed |
|---|---|---|
| `pipeline/gridlib.py` | `gridlib.py` (as-is tier) | TRIVIUM scoring/metrics (topic balance, composite content, density thresholds) removed — a 7-word hunt grid is hand-designed and sparse; only structural legality rules kept. |
| `pipeline/mock_backend.py` | `mock_backend.py` (as-is tier) | Route handlers swapped: PostgREST `results`/`events` tables → the three `fedora_*` RPCs. Kept: ThreadingHTTPServer (single-threaded serialisation trap), config.js interception, `SLOW_POST_MS` scoped to one route. |
| `pipeline/deploy_pages.py` | `deploy_pages.py` (as-is tier) | Same explicit-whitelist pattern; date gate dropped — Fedora's release control is server-side (locked clues never reach the repo at all). |
| `pipeline/validate_hunt.py` | `validate_bank.py` (structure) | Same shape (validate JSON, report per-item, fail loudly) with hunt-shaped checks: grid legality, unlock-graph reachability under any/all semantics, `{N}` placeholder guarantees, answer-leak rules, team codes, meta-puzzle spelling. |
| `pipeline/smoke_test.cjs` (planned with app) | `app_smoke_test.cjs` (harness) | Playwright boilerplate (mock spawn, `/opt/pw-browsers/chromium`, `--no-sandbox`, pageerror capture, 390×844 viewport). Assertions will be Fedora's. |
| `app/index.html` (planned) | TRIVIUM `app/index.html` | Grid renderer / keyboard / cursor rules ported; TRIVIUM's name-setup, topic picker, XOR-obfuscated solutions and daily-leaderboard flow replaced by team join, clue panel and server-authoritative reveal. |
| `app/sql/schema.sql` | TRIVIUM `schema.sql` (ideas only) | Kept the lessons (RLS from day one, immutable rows, the column-grant privacy trick, views-don't-inherit-RLS trap). Architecture differs: TRIVIUM grants direct table access; Fedora is deny-all + three `security definer` RPCs, because answers live server-side. |

Also inherited deliberately (TRIVIUM's paid-for traps): gate CI on exit codes,
never on grepping output; stage before `git diff --quiet`; verify deploys
against the deployed URL, not the local build; fresh-session crons with
standalone briefs.

## Left behind, and why

- **`bake_day.py`** (the crown jewel there) — all of its hard-won logic is
  about *daily content rotation*: seeded menu draws, freshness scoring, retry
  salts, relaxed fallbacks. Fedora has one hand-authored hunt, no daily bake.
  If Fedora ever does "a new hunt every month", reread it first.
- **`fill_grids.py`** — 800-restart randomized grid search for 10–14-word
  dense puzzles. Seven words interlock by hand in an afternoon; the search
  and its determinism machinery are dead weight here.
- **`validate_candidates.py`** — wordlist membership, UK/US regionality, the
  three-iteration `confusable()` collision rule. TRIVIUM draws answers from
  candidate pools where near-duplicates collide; Fedora's answers are dictated
  by physical reality at specific locations. The analogous risk here is
  *rival on-site answers* (two plausible readings of what you're looking at),
  which a code rule can't catch — that gets an adversarial review pass
  instead.
- **`build_html.py` / `build_app_artifact.py`** — single-file offline builds.
  A hunt with server-held answers is online-only by design; an offline build
  would require shipping answers, which is exactly the Watson Adventures
  mistake.
- **`validate_puzzle.py`, `test_pipeline.py`, `smoke_test.cjs`** — TRIVIUM
  POC-pack specific (three-topic combos, ghost cohorts, difficulty
  calibration).
- **Library/menu/pars content and crons** — TRIVIUM's live daily operation;
  explicitly untouched.

The `verify_bakes.py` *pattern* (independently re-derive constraints from the
built artifact, trust nothing the builder said) is adopted as a principle —
`validate_hunt.py` re-checks the grid from raw placements, and the smoke test
will assert against the running app, not the build report.
