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
import re
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
        "-- fix clue text with a manual UPDATE instead. Team codes are globally",
        "-- unique across hunts: reusing another hunt's code aborts this whole",
        "-- transaction (nothing is applied).",
        "begin;",
        f"delete from public.hunts where id = {q(hid)};",
        "insert into public.hunts (id, title, intro, starts_at, active, "
        "strike_limit, hint_wait_s) values",
        f"  ({q(hid)}, {q(hunt['title'])}, "
        f"{q(hunt['intro']) if hunt.get('intro') else 'null'}, "
        f"{q(hunt['starts_at']) if hunt.get('starts_at') else 'null'}, true, "
        f"{int(hunt['strike_limit']) if hunt.get('strike_limit') is not None else 'null'}, "
        f"{int(hunt['hint_wait_s']) if hunt.get('hint_wait_s') is not None else 300});",
    ]
    for c in hunt["clues"]:
        arr = "'{" + ",".join(str(n) for n in c.get("unlocked_by", [])) + "}'::int[]"
        avail = q(c["available_from"]) if c.get("available_from") else "null"
        # v3: accepted-answer sets; legacy grid hunts carry a single 'answer'.
        # Number answers get the runtime's number normalization (leading zeros
        # stripped) so seeded values always remain matchable.
        acc = [str(a) for a in c.get("answers", [c["answer"]] if "answer" in c else [])]
        if c.get("qtype", "text") == "number":
            norm = [(re.sub(r"\D", "", a).lstrip("0") or "0") for a in acc]
        else:
            norm = [re.sub(r"[^A-Z0-9]", "", a.upper()) for a in acc]
        aarr = ("array[" + ",".join(q(a) for a in norm) + "]::text[]"
                if norm else "'{}'::text[]")
        hints = c.get("hints", [])
        harr = ("array[" + ",".join(q(h) for h in hints) + "]::text[]"
                if hints else "'{}'::text[]")
        waits = c.get("hint_waits", [])
        warr = "'{" + ",".join(str(int(w)) for w in waits) + "}'::int[]"
        after = q(c["after_text"]) if c.get("after_text") else "null"
        glim = int(c["guess_limit"]) if c.get("guess_limit") is not None else "null"
        if c.get("gate_lat") is not None:
            gate = (f"{float(c['gate_lat'])}, {float(c['gate_lon'])}, "
                    f"{int(c['gate_radius_m'])}, "
                    + (q(c["gate_prompt"]) if c.get("gate_prompt") else "null"))
        else:
            gate = "null, null, null, null"
        out.append(
            "insert into public.clues (hunt_id, idx, qtype, kind, answers, match_mode, "
            "clue_text, hints, hint_waits, after_text, guess_limit, unlocked_by, "
            "unlock_mode, available_from, gate_lat, gate_lon, gate_radius_m, "
            "gate_prompt) values\n"
            f"  ({q(hid)}, {c['idx']}, {q(c.get('qtype', 'text'))}, "
            f"{q(c.get('kind', 'ground'))}, {aarr}, {q(c.get('match_mode', 'exact'))}, "
            f"{q(c['clue_text'])}, {harr}, {warr}, {after}, {glim}, {arr}, "
            f"{q(c.get('unlock_mode', 'any'))}, {avail}, {gate});")
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
    is_grid = all("row" in c and "col" in c and "dir" in c for c in hunt["clues"])
    if is_grid:
        gj = grid_json(hunt)
        (BASE / "app" / "grid.json").write_text(json.dumps(gj, indent=1))
        print(f"app/grid.json: {gj['rows']}x{gj['cols']}, {gj['n_clues']} clues "
              f"(public, no content)")
    else:
        print(f"QA hunt ({len(hunt['clues'])} questions) — no grid artifact")
    seed = seed_dir / f"seed_{hunt['hunt_id']}.sql"
    seed.write_text(seed_sql(hunt))
    print(f"{seed}: PRIVATE seed — paste into Supabase SQL editor, never commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
