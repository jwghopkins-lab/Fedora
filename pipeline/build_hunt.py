#!/usr/bin/env python3
"""Build deployable artifacts from a hunt definition file.

Reads the PRIVATE hunt file (answers + clue text + team codes), validates it
via validate_hunt, then emits two things:

- app/grid.json          PUBLIC: grid geometry + crossword numbering only.
                         No answers, no clue text, no unlock graph — safe to
                         commit to this public repo.
- <dir>/seed_<id>.sql    PRIVATE: the full content as SQL for the Supabase
                         SQL editor. NEVER commit this file; hand it to the
                         organiser out of band.

Usage: build_hunt.py <hunt.json> [--seed-out DIR]     (seed dir default: /tmp)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gridlib
import validate_hunt

BASE = Path(__file__).resolve().parent.parent


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def seed_sql(hunt):
    hid = hunt["hunt_id"]
    out = [
        "-- PRIVATE seed for hunt " + hid + " — do NOT commit this file.",
        "-- Re-running deletes and recreates the hunt, INCLUDING its teams and",
        "-- all their submissions (cascade). Fine before launch; after launch,",
        "-- fix clue text with a manual UPDATE instead.",
        "begin;",
        f"delete from public.hunts where id = {q(hid)};",
        "insert into public.hunts (id, title, starts_at, active) values",
        f"  ({q(hid)}, {q(hunt['title'])}, "
        f"{q(hunt['starts_at']) if hunt.get('starts_at') else 'null'}, true);",
    ]
    for c in hunt["clues"]:
        arr = "'{" + ",".join(str(n) for n in c.get("unlocked_by", [])) + "}'::int[]"
        avail = q(c["available_from"]) if c.get("available_from") else "null"
        out.append(
            "insert into public.clues (hunt_id, idx, answer, clue_text, unlocked_by, "
            "unlock_mode, available_from) values\n"
            f"  ({q(hid)}, {c['idx']}, {q(c['answer'])}, {q(c['clue_text'])}, "
            f"{arr}, {q(c.get('unlock_mode', 'any'))}, {avail});")
    for t in hunt.get("teams", []):
        out.append("insert into public.teams (hunt_id, name, code) values\n"
                   f"  ({q(hid)}, {q(t['name'])}, {q(t['code'].upper())});")
    out.append("commit;")
    return "\n".join(out) + "\n"


def grid_json(hunt):
    placements = [{"idx": c["idx"], "answer": c["answer"], "row": c["row"],
                   "col": c["col"], "dir": c["dir"]} for c in hunt["clues"]]
    normalized, numbers, entries = gridlib.number_grid(placements)
    letters, _, _ = gridlib.build_grid(normalized)
    r0, c0, r1, c1 = gridlib.bbox(letters)
    assert (r0, c0) == (0, 0)
    meta = hunt.get("meta")
    return {
        "hunt_id": hunt["hunt_id"],
        "title": hunt["title"],
        "rows": r1 + 1, "cols": c1 + 1,
        "n_clues": len(hunt["clues"]),
        "entries": entries,
        "meta_cells": meta["cells"] if meta else [],
        "meta_hint": (meta or {}).get("public_hint", ""),
    }


def main():
    argv = sys.argv[1:]
    seed_dir = Path("/tmp")
    if "--seed-out" in argv:
        i = argv.index("--seed-out")
        seed_dir = Path(argv[i + 1])
        del argv[i:i + 2]
    if len(argv) != 1:
        print(__doc__)
        return 2
    hunt = json.loads(Path(argv[0]).read_text())
    fails = validate_hunt.check(hunt)
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    gj = grid_json(hunt)
    (BASE / "app" / "grid.json").write_text(json.dumps(gj, indent=1))
    seed = seed_dir / f"seed_{hunt['hunt_id']}.sql"
    seed.write_text(seed_sql(hunt))
    print(f"app/grid.json: {gj['rows']}x{gj['cols']}, {gj['n_clues']} clues "
          f"(public, no content)")
    print(f"{seed}: PRIVATE seed — paste into Supabase SQL editor, never commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
