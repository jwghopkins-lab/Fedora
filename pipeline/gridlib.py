"""Core freeform-crossword grid logic: placement legality, connectivity, numbering.

Ported from TRIVIUM (poc/crossword/pipeline/gridlib.py in jwghopkins-lab/greyhound2,
branch claude/ai-crossword-generator-research-2iemh5) with the TRIVIUM-specific
scoring/metrics (topic balance, composite content scores, density thresholds)
removed: a 7-word hunt grid is hand-designed and sparse by nature, so only the
structural legality rules apply here.

Grid model: a sparse dict {(row, col): letter}. Words are placements:
{idx, answer, row, col, dir} with dir 'A' (across) or 'D' (down).

Freeform rules enforced:
- perpendicular crossings only; a cell may belong to at most one word per direction
- no incidental adjacency: two orthogonally adjacent filled cells must be
  consecutive cells of a common word
- single connected component (verified via BFS over shared cells)
"""
from collections import defaultdict


def cells_of(p):
    r, c = p["row"], p["col"]
    if p["dir"] == "A":
        return [(r, c + i) for i in range(len(p["answer"]))]
    return [(r + i, c) for i in range(len(p["answer"]))]


def build_grid(placements):
    """Return (letters, per_dir, conflicts). letters: cell->letter;
    per_dir: cell->{'A': placement index, 'D': placement index}."""
    letters, per_dir, conflicts = {}, defaultdict(dict), []
    for idx, p in enumerate(placements):
        for (cell, ch) in zip(cells_of(p), p["answer"]):
            if cell in letters and letters[cell] != ch:
                conflicts.append((cell, letters[cell], ch))
            letters[cell] = ch
            if p["dir"] in per_dir[cell]:
                conflicts.append((cell, "dup_dir", p["dir"]))
            per_dir[cell][p["dir"]] = idx
    return letters, per_dir, conflicts


def crossings(placements):
    """Return list of crossing counts per placement."""
    _, per_dir, _ = build_grid(placements)
    counts = [0] * len(placements)
    for cell, dirs in per_dir.items():
        if "A" in dirs and "D" in dirs:
            counts[dirs["A"]] += 1
            counts[dirs["D"]] += 1
    return counts


def adjacency_ok(placements):
    """Every pair of orthogonally adjacent filled cells must be consecutive
    cells of one common word."""
    letters, per_dir, _ = build_grid(placements)
    for (r, c) in letters:
        for (dr, dc, d) in ((0, 1, "A"), (1, 0, "D")):
            nb = (r + dr, c + dc)
            if nb in letters:
                a, b = per_dir[(r, c)].get(d), per_dir[nb].get(d)
                if a is None or a != b:
                    return False, ((r, c), nb)
    return True, None


def bbox(letters):
    rs = [r for r, _ in letters]
    cs = [c for _, c in letters]
    return min(rs), min(cs), max(rs), max(cs)


def connected(placements):
    if not placements:
        return True
    adj = defaultdict(set)
    cell_words = defaultdict(set)
    for i, p in enumerate(placements):
        for cell in cells_of(p):
            cell_words[cell].add(i)
    for words in cell_words.values():
        for a in words:
            adj[a] |= words
    seen, stack = set(), [0]
    while stack:
        w = stack.pop()
        if w in seen:
            continue
        seen.add(w)
        stack.extend(adj[w] - seen)
    return len(seen) == len(placements)


def hard_violations(placements, max_rows=16, max_cols=16):
    """Independent re-check of every structural rule. Returns list of failures."""
    fails = []
    if not placements:
        return ["no placements"]
    letters, per_dir, conflicts = build_grid(placements)
    if conflicts:
        fails.append(f"letter/direction conflicts: {conflicts[:3]}")
    ok, where = adjacency_ok(placements)
    if not ok:
        fails.append(f"incidental adjacency at {where}")
    if not connected(placements):
        fails.append("grid not connected")
    r0, c0, r1, c1 = bbox(letters)
    rows, cols = r1 - r0 + 1, c1 - c0 + 1
    if rows > max_rows or cols > max_cols:
        fails.append(f"bbox {rows}x{cols} exceeds {max_rows}x{max_cols}")
    xing = crossings(placements)
    for p, x in zip(placements, xing):
        if x < 1:
            fails.append(f"word {p['answer']} has zero crossings")
    answers = [p["answer"] for p in placements]
    if len(set(answers)) != len(answers):
        fails.append("duplicate answers")
    return fails


def normalize(placements):
    """Shift placements so bbox starts at (0,0)."""
    letters, _, _ = build_grid(placements)
    r0, c0, _, _ = bbox(letters)
    return [dict(p, row=p["row"] - r0, col=p["col"] - c0) for p in placements]


def number_grid(placements):
    """Standard crossword numbering. Returns (normalized placements, numbers:
    cell->n, entries: list of {number, dir, idx, row, col, length})."""
    placements = normalize(placements)
    letters, per_dir, _ = build_grid(placements)
    starts = {}
    for i, p in enumerate(placements):
        starts[(p["row"], p["col"], p["dir"])] = i
    r0, c0, r1, c1 = bbox(letters)
    numbers, entries, n = {}, [], 0
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if (r, c) not in letters:
                continue
            here = [d for d in ("A", "D") if (r, c, d) in starts]
            if here:
                n += 1
                numbers[(r, c)] = n
                for d in here:
                    p = placements[starts[(r, c, d)]]
                    entries.append({"number": n, "dir": d, "row": r, "col": c,
                                    "idx": p["idx"], "length": len(p["answer"])})
    return placements, numbers, entries
