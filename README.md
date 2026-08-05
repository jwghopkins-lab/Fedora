# Fedora

A real-world treasure hunt game — Da Vinci Code × National Treasure × Indiana
Jones. Crossword clues lead teams to physical places in London; what you
observe on-site *is* the answer; solving a word unlocks the next clue; the
grid's shaded squares name the finish pub. First team there wins.

Concept research and roadmap: `docs/concept.md`. Provenance of the pipeline
(ported from the TRIVIUM crossword project, fully independent of it):
`docs/port-decision.md`.

## Architecture

```
hunt/<name>.json      PRIVATE hunt definition (answers, clue text, team codes)
                      — never committed for a real hunt; example fixture only
        |
        v
pipeline/validate_hunt.py    structural checks: grid legality, unlock graph,
                             leak rules   (CI gates on exit code)
pipeline/build_hunt.py  -->  app/grid.json   PUBLIC geometry, no content
                        -->  seed_<name>.sql PRIVATE, pasted into Supabase
        |
        v
Supabase (new, dedicated project)   all tables deny-all RLS; the anon key can
                                    only call three RPCs: fedora_join,
                                    fedora_submit, fedora_leaderboard
        |
        v
app/index.html        browser app on GitHub Pages: team code -> crossword grid
                      + clue panel; answers checked server-side; correct
                      answer reveals dependent clues; live leaderboard
```

The security model in one line: **the client never holds an answer or a locked
clue** — clue text leaves the database only after that team has solved the
clue's prerequisites, guesses are rate-limited server-side (15s/clue/team),
and every attempt is logged, which is also what makes the leaderboard.

## Develop

```
python3 pipeline/validate_hunt.py hunt/example_hunt.json   # structural checks
python3 pipeline/build_hunt.py hunt/example_hunt.json      # grid.json + seed sql
python3 pipeline/test_backend.py                           # backend contract test
python3 pipeline/mock_backend.py 8765                      # play locally against mock
python3 pipeline/deploy_pages.py                           # whitelist site build
```

Deploys to GitHub Pages via `.github/workflows/pages.yml` on push to `main`
(whitelist only: `index.html`, `config.js`, `grid.json`). CI
(`.github/workflows/ci.yml`) runs the validator, builder and backend contract
test on the example fixture.

## Operational notes

- Real hunt content (answers, clue text, field-verification notes, team codes)
  exists in exactly two places: the organiser's private copy and the Supabase
  database. This repo is public; nothing spoilable is committed.
- `app/config.js` carries the Supabase URL + anon key. The anon key is safe to
  publish — security lives in the database rules, not in hiding the key.
- Supabase free projects pause after ~1 week idle; wake before game day.
