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
            if any(not isinstance(a, str) for a in acc):
                fails.append(f"clue {c['idx']}: accepted answers must be strings "
                             f"(write numbers as \"42\", not 42)")
                acc = [str(a) for a in acc]
            norm = [re.sub(r"[^A-Z0-9]", "", a.upper()) for a in acc]
            k = c.get("kind", "ground")
            if k not in ("wits", "dig", "ground"):
                fails.append(f"clue {c['idx']}: bad kind {k!r}")
            # empty accept-list = collect mode (any answer logged) for BOTH types
            if any(not a for a in norm):
                fails.append(f"clue {c['idx']}: empty accepted answer after normalization")
            if any(len(a) > 40 for a in norm):
                fails.append(f"clue {c['idx']}: accepted answer over 40 chars")
            if len(set(norm)) != len(norm):
                fails.append(f"clue {c['idx']}: duplicate accepted answers")
            if qt == "number":
                for a in norm:
                    if not a.isdigit() or len(a) > 4:
                        fails.append(f"clue {c['idx']}: non-numeric accepted answer {a!r}")
                    elif a != (a.lstrip("0") or "0"):
                        fails.append(f"clue {c['idx']}: leading-zero number {a!r} can "
                                     f"never match a normalized guess — write it as "
                                     f"{a.lstrip('0') or '0'!r}")
    sl = hunt.get("strike_limit")
    if sl is not None and (isinstance(sl, bool) or not isinstance(sl, int) or sl < 1):
        fails.append(f"strike_limit must be a positive integer or null, got {sl!r}")
    hw = hunt.get("hint_wait_s")
    if hw is not None and (isinstance(hw, bool) or not isinstance(hw, int) or hw < 0):
        fails.append(f"hint_wait_s must be a non-negative integer or null, got {hw!r}")
    for c in clues:
        # v4: hints are a SEQUENCE. hints[i] is released hint_waits[i] seconds
        # after the clue opened, one at a time, so the waits must climb — a flat
        # or falling series would hand out two hints on the same tick.
        hints = c.get("hints", [])
        waits = c.get("hint_waits", [])
        if not isinstance(hints, list) or not isinstance(waits, list):
            fails.append(f"clue {c['idx']}: hints and hint_waits must be lists")
            continue
        if any(not isinstance(h, str) or not h.strip() for h in hints):
            fails.append(f"clue {c['idx']}: every hint must be a non-empty string")
        # an empty hint_waits means "use the hunt default for every hint"
        # (fedora_hint coalesces); anything else must pair up one for one
        if waits and len(waits) != len(hints):
            fails.append(f"clue {c['idx']}: {len(hints)} hints but "
                         f"{len(waits)} hint_waits — they must pair up")
        if any(isinstance(w, bool) or not isinstance(w, int) or w < 0 for w in waits):
            fails.append(f"clue {c['idx']}: hint_waits must be non-negative integers")
        elif any(b <= a for a, b in zip(waits, waits[1:])):
            fails.append(f"clue {c['idx']}: hint_waits must strictly ascend, "
                         f"got {waits}")
        at = c.get("after_text")
        if at is not None and (not isinstance(at, str) or not at.strip()):
            fails.append(f"clue {c['idx']}: after_text must be a non-empty string "
                         f"or absent")
        gl = c.get("guess_limit")
        if gl is not None and (isinstance(gl, bool) or not isinstance(gl, int) or gl < 1):
            fails.append(f"clue {c['idx']}: guess_limit must be a positive integer "
                         f"or absent, got {gl!r}")
        mm = c.get("match_mode", "exact")
        if mm not in ("exact", "contains"):
            fails.append(f"clue {c['idx']}: bad match_mode {mm!r}")
        if mm == "contains" and not c.get("answers"):
            fails.append(f"clue {c['idx']}: match_mode 'contains' is meaningless "
                         f"in collect mode (no accepted answers)")
    for c in clues:
        if not isinstance(c.get("clue_text"), str):
            fails.append(f"clue {c.get('idx', '?')}: missing clue_text")
            c["clue_text"] = "(missing clue_text placeholder)"

    # unlock graph
    starts = [c["idx"] for c in clues if not c.get("unlocked_by")]
    if not starts:
        fails.append("no start clue (every clue has prerequisites)")
    # A QA hunt declaring itself linear must actually be linear: one start, and
    # each clue gated on exactly its predecessor. Two clues sharing a
    # prerequisite silently opens both at once, which reads as a bug in play.
    if not is_grid and hunt.get("linear"):
        if starts != [min(idxs)]:
            fails.append(f"linear hunt must have exactly one start clue, got {starts}")
        for c in clues:
            need = c.get("unlocked_by", [])
            if c["idx"] != min(idxs) and need != [c["idx"] - 1]:
                fails.append(f"linear hunt: clue {c['idx']} should be gated on "
                             f"[{c['idx'] - 1}], got {need}")
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
        # An accepted answer must not appear in any clue text or hint that a
        # player could read BEFORE solving it. In a linear hunt, a later clue may
        # safely name an earlier answer — the player already has it, and the
        # prose reads far better for being allowed to refer back. Anything at or
        # ahead of the answer's own clue is still a leak.
        # (Caveat: a team that skipped clue N could learn N's answer from a later
        # clue. A skip already forfeits that clue, so the exploit is not worth
        # contorting every sentence to avoid.)
        linear = bool(hunt.get("linear"))
        for c in clues:
            for a in c.get("answers", []):
                for c2 in clues:
                    if linear and c2["idx"] > c["idx"]:
                        continue
                    if re.search(rf"\b{re.escape(a)}\b", c2["clue_text"], re.I):
                        fails.append(f"accepted answer {a!r} (clue {c['idx']}) "
                                     f"appears in clue {c2['idx']} text")
                    hs = c2.get("hints", [])
                    for i, h in enumerate(hs, 1):
                        # The LAST hint on a clue is allowed to hand over that
                        # clue's own answer: with no skip button, the end of the
                        # hint ladder is the only way past a wall, and it is
                        # already paid for in waiting and on the record. Every
                        # earlier hint, and every hint on any OTHER clue, must
                        # still keep its mouth shut.
                        if c2["idx"] == c["idx"] and i == len(hs):
                            continue
                        if re.search(rf"\b{re.escape(a)}\b", h, re.I):
                            fails.append(f"accepted answer {a!r} (clue {c['idx']}) "
                                         f"appears in clue {c2['idx']} hint {i}"
                                         + (" (only the LAST hint may give it away)"
                                            if c2["idx"] == c["idx"] else ""))
                for c2 in clues:
                    # after_text is read once its own clue is solved, so it sits a
                    # step later than that clue's text: naming answer N is fine
                    # from clue N onwards, a leak anywhere before it.
                    if linear and c2["idx"] >= c["idx"]:
                        continue
                    if re.search(rf"\b{re.escape(a)}\b", c2.get("after_text") or "", re.I):
                        fails.append(f"accepted answer {a!r} (clue {c['idx']}) "
                                     f"appears in clue {c2['idx']} after_text")

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
