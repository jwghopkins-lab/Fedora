#!/usr/bin/env python3
"""Validate a hunt definition file (the PRIVATE content: answers + clue text).

Structure ported from TRIVIUM's validate_bank.py (validate a JSON bank, report
per-item rejections, fail loudly) but the checks are hunt-shaped:

- answers: A-Z only, 3-15 chars, unique, no answer contained in another
- grid: legal freeform crossword via gridlib (conflicts, adjacency,
  connectivity, every word crosses, bbox)
- unlock graph: at least one start clue; every clue reachable under its
  any/all semantics; no dependency cycles; the final clue exists
- {N} placeholders in clue text: N must be guaranteed-solved at reveal time
  (i.e. N in unlocked_by, and unlock_mode == 'all' or unlocked_by == [N])
- leak rules: no answer appears literally in ANY clue text (chaining is done
  with {N} placeholders, never by writing an answer into a clue)
- teams: codes unique, 6-40 chars, alphanumeric
- meta letters (optional): meta.cells must be filled grid cells and spell
  meta.answer

Exit code 1 on any failure — gate CI on the exit code, never on output text
(TRIVIUM trap: grepping for success phrases let a real warning sail through).

Usage: validate_hunt.py <hunt.json>
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gridlib


def check(hunt):
    fails = []
    clues = hunt.get("clues", [])
    if not clues:
        return ["no clues"]
    idxs = [c["idx"] for c in clues]
    if sorted(idxs) != list(range(1, len(clues) + 1)):
        fails.append(f"idx must be 1..{len(clues)}, got {sorted(idxs)}")
    by_idx = {c["idx"]: c for c in clues}

    # two hunt shapes: GRID (crossword; every clue has answer+row/col/dir) and
    # QA (question journey; clues have qtype + answers[], no geometry)
    is_grid = all("row" in c and "col" in c and "dir" in c for c in clues)
    placements = []
    if is_grid:
        for c in clues:
            if not re.fullmatch(r"[A-Z]{3,15}", c["answer"]):
                fails.append(f"clue {c['idx']}: bad answer {c['answer']!r}")
        answers = [c["answer"] for c in clues]
        if len(set(answers)) != len(answers):
            fails.append("duplicate answers")
        for a in answers:
            for b in answers:
                if a != b and a in b:
                    fails.append(f"answer {a} is contained in {b}")
        placements = [{"idx": c["idx"], "answer": c["answer"], "row": c["row"],
                       "col": c["col"], "dir": c["dir"]} for c in clues]
        fails += gridlib.hard_violations(placements)
    else:
        answers = []
        for c in clues:
            qt = c.get("qtype", "text")
            if qt not in ("text", "number"):
                fails.append(f"clue {c['idx']}: bad qtype {qt!r}")
            acc = c.get("answers", [])
            norm = [re.sub(r"[^A-Z0-9]", "", a.upper()) for a in acc]
            if qt == "text" and not norm:
                fails.append(f"clue {c['idx']}: text question with no accepted answers")
            if any(not a for a in norm):
                fails.append(f"clue {c['idx']}: empty accepted answer after normalization")
            if len(set(norm)) != len(norm):
                fails.append(f"clue {c['idx']}: duplicate accepted answers")
            if qt == "number":
                for a in norm:
                    if not a.isdigit() or len(a) > 4:
                        fails.append(f"clue {c['idx']}: non-numeric accepted answer {a!r}")

    # unlock graph
    starts = [c["idx"] for c in clues if not c.get("unlocked_by")]
    if not starts:
        fails.append("no start clue (every clue has prerequisites)")
    for c in clues:
        for n in c.get("unlocked_by", []):
            if n not in by_idx:
                fails.append(f"clue {c['idx']}: unknown prerequisite {n}")
            if n == c["idx"]:
                fails.append(f"clue {c['idx']}: depends on itself")
    # reachability under any/all semantics (monotone fixpoint)
    solved = set()
    changed = True
    while changed:
        changed = False
        for c in clues:
            if c["idx"] in solved:
                continue
            need = c.get("unlocked_by", [])
            mode = c.get("unlock_mode", "any")
            ok = (not need or
                  (all(n in solved for n in need) if mode == "all"
                   else any(n in solved for n in need)))
            if ok:
                solved.add(c["idx"])
                changed = True
    unreachable = set(idxs) - solved
    if unreachable:
        fails.append(f"unreachable clues (cycle or bad graph): {sorted(unreachable)}")

    # placeholders + leaks
    for c in clues:
        text = c["clue_text"]
        if not (10 <= len(text) <= 2000):
            fails.append(f"clue {c['idx']}: clue_text length {len(text)}")
        for m in re.finditer(r"\{(\d+)\}", text):
            n = int(m.group(1))
            need = c.get("unlocked_by", [])
            mode = c.get("unlock_mode", "any")
            guaranteed = n in need and (mode == "all" or need == [n])
            if not guaranteed:
                fails.append(f"clue {c['idx']}: placeholder {{{n}}} not guaranteed "
                             f"solved at reveal (unlocked_by={need}, mode={mode})")
        for a in answers:
            if re.search(rf"\b{re.escape(a)}\b", text, re.I):
                fails.append(f"answer {a} leaks in clue {c['idx']} text")
    if not is_grid:
        # accepted answers must not appear in ANY clue text
        for c in clues:
            for a in c.get("answers", []):
                for c2 in clues:
                    if re.search(rf"\b{re.escape(a)}\b", c2["clue_text"], re.I):
                        fails.append(f"accepted answer {a!r} (clue {c['idx']}) "
                                     f"appears in clue {c2['idx']} text")

    # crossing-leak analysis (warnings, printed by main): a word crossed by a
    # word that is solvable WITHOUT it can have letters revealed before it is
    # answered — fatal for candidate-ambiguity clues (e.g. a CHAIN/PERCH 50/50)
    # where the whole point is that no letter distinguishes the candidates.
    # teams (both hunt shapes)
    codes = [t["code"] for t in hunt.get("teams", [])]
    if len(set(codes)) != len(codes):
        fails.append("duplicate team codes")
    for t in hunt.get("teams", []):
        if not re.fullmatch(r"[A-Za-z0-9]{6,40}", t["code"]):
            fails.append(f"team {t['name']!r}: bad code")

    hunt["_leak_warnings"] = []
    if not is_grid:
        return fails
    _, per_dir, _ = gridlib.build_grid(placements)
    p_by_idx = {p["idx"]: i for i, p in enumerate(placements)}
    for w in clues:
        reach = set()
        changed = True
        while changed:
            changed = False
            for c in clues:
                if c["idx"] == w["idx"] or c["idx"] in reach:
                    continue
                need = c.get("unlocked_by", [])
                mode = c.get("unlock_mode", "any")
                if not need:
                    ok = True
                elif mode == "all":
                    ok = w["idx"] not in need and all(n in reach for n in need)
                else:
                    ok = any(n in reach for n in need if n != w["idx"])
                if ok:
                    reach.add(c["idx"])
                    changed = True
        wi = p_by_idx[w["idx"]]
        for cell, dirs in per_dir.items():
            if len(dirs) == 2 and wi in dirs.values():
                other = next(i for i in dirs.values() if i != wi)
                oidx = placements[other]["idx"]
                if oidx in reach:
                    hunt["_leak_warnings"].append(
                        f"clue {w['idx']} ({w['answer']}): letter at {cell} can be "
                        f"revealed by clue {oidx} before {w['idx']} is solved")

    # optional meta puzzle: marked cells must exist and spell the meta answer
    meta = hunt.get("meta")
    if meta:
        letters, _, _ = gridlib.build_grid(gridlib.normalize(placements))
        got = []
        for (r, c) in (tuple(x) for x in meta["cells"]):
            if (r, c) not in letters:
                fails.append(f"meta cell ({r},{c}) is not a filled cell")
            else:
                got.append(letters[(r, c)])
        if "".join(got) != meta["answer"]:
            fails.append(f"meta cells spell {''.join(got)!r}, expected {meta['answer']!r}")
        for a in answers:
            if meta["answer"] == a:
                fails.append("meta answer duplicates a grid answer")

    return fails


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    hunt = json.loads(Path(sys.argv[1]).read_text())
    fails = check(hunt)
    for f in fails:
        print(f"FAIL: {f}")
    for w in hunt.get("_leak_warnings", []):
        print(f"LEAK-WARN: {w}")
    print(f"{sys.argv[1]}: {len(hunt.get('clues', []))} clues, "
          f"{len(hunt.get('teams', []))} teams — "
          f"{'INVALID' if fails else 'valid'} "
          f"({len(hunt.get('_leak_warnings', []))} crossing-leak warnings)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
