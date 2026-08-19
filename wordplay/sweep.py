#!/usr/bin/env python3
"""Wordplay sweep over the measurement/London theme lexicon (Part II of README).

Expects two wordlists beside this script (not committed):
  words_alpha.txt  https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt
  20k.txt          https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt

Hunts: (1) conjectured-anagram verification, (2) single-word anagrams of the
theme lexicon, (3) two-word anagrams of key targets (both words common),
(4) unit names as contiguous substrings of common words, (5) re-splits of
theme words into dictionary words. Findings are only candidates — every hit
still needs the truth-grading discipline in README.md before use.
"""
from collections import Counter, defaultdict
import os

D = os.path.dirname(os.path.abspath(__file__))
ALL = set(w.strip().lower() for w in open(os.path.join(D, "words_alpha.txt")) if w.strip().isalpha())
COMMON_LIST = [w.strip().lower() for w in open(os.path.join(D, "20k.txt")) if w.strip().isalpha()]
COMMON = set(COMMON_LIST)
RANK = {w: i for i, w in enumerate(COMMON_LIST)}

def key(s):
    return "".join(sorted(c for c in s.lower() if c.isalpha()))

def fits(inner, outer):
    ci, co = Counter(inner), Counter(outer)
    return all(co[c] >= n for c, n in ci.items())

def minus(outer, inner):
    c = Counter(c for c in outer.lower() if c.isalpha())
    c.subtract(Counter(inner))
    return "".join(sorted(c.elements()))

# ---------------------------------------------------------------- 1. conjectures
print("=== 1. CONJECTURE CHECKS ===")
pairs = [("smyth", "myths"), ("turner", "return"), ("observatory", "sober votary"),
         ("lutyens", "unstyle"), ("meridian", "i dream in"), ("verne", "never"),
         ("minute", "minuet"), ("prime meridian", "impaired miner"),
         ("westminster", "witness term"), ("elevenplustwo", "twelveplusone")]
for a, b in pairs:
    print(f"{a!r:18} vs {b!r:18} anagram: {key(a) == key(b)}")

# ---------------------------------------------------- 2. single-word anagrams of theme words
print("\n=== 2. SINGLE-WORD ANAGRAMS OF THEME LEXICON ===")
by_key = defaultdict(list)
for w in ALL:
    by_key[key(w)].append(w)
theme = """airy smyth piazzi clarke turner belsky lutyens landseer verne nelson strachey
napier greenwich meridian standard standards imperial yard yards metre meter vestry parish
clerk tally tallies exchequer cenotaph whitehall trafalgar westminster observatory astronomer
transit theodolite pendulum ordnance survey cubit pyramid sacred degree minute second fathom
furlong bronze brass thames jewel tower cord knot chord strand measure measures gnomon
perch fahrenheit newton taylor""".split()
for w in theme:
    hits = [h for h in by_key.get(key(w), []) if h != w]
    if hits:
        strong = [h for h in hits if h in COMMON]
        print(f"{w:14} -> common: {strong}  all: {hits[:12]}")

# ------------------------------------------------------------ 3. two-word anagrams of targets
print("\n=== 3. TWO-WORD ANAGRAMS (both words in top-20k, len>=3) ===")
targets = ["observatory", "meridian", "greenwich", "trafalgar", "westminster", "imperial",
           "standard", "astronomer", "exchequer", "cenotaph", "whitehall", "theodolite",
           "ordnance", "pendulum", "landseer", "strachey", "greenwich meridian",
           "prime meridian", "standard yard", "brass bars", "tally sticks"]
common3 = [w for w in COMMON_LIST if len(w) >= 3]
kmap = defaultdict(list)
for w in common3:
    kmap[key(w)].append(w)
for t in targets:
    tk = key(t)
    seen, out = set(), []
    for w in common3:
        if len(w) > len(tk) - 3 or not fits(w, tk):
            continue
        for c in kmap.get(minus(tk, w), []):
            pair = tuple(sorted((w, c)))
            if pair not in seen and w != c:
                seen.add(pair)
                out.append(pair)
    out.sort(key=lambda p: RANK.get(p[0], 99999) + RANK.get(p[1], 99999))
    if out:
        print(f"\n{t.upper()} ({len(out)} pairs), most-common first:")
        for p in out[:25]:
            print("   ", " + ".join(p))

# ------------------------------------------------------------ 4. unit names hidden in words
print("\n=== 4. UNIT NAMES AS CONTIGUOUS SUBSTRINGS (host word in top-20k) ===")
units = ["yard", "inch", "mile", "foot", "feet", "hand", "span", "chain", "acre", "meter",
         "metre", "gram", "stone", "ounce", "pint", "dram", "cubit", "fathom", "league",
         "knot", "perch", "carat", "grain", "furlong", "gallon", "pound"]
for u in units:
    hosts = sorted((w for w in COMMON if u in w and w != u and len(w) <= 14), key=lambda w: RANK[w])
    if hosts:
        print(f"{u:8} in: {hosts[:16]}")

# ------------------------------------------------------------ 5. re-splits of theme words
print("\n=== 5. RE-SPLITS INTO 2 DICTIONARY WORDS (parts >=2, at least one in 20k) ===")
for w in ["standard", "meridian", "greenwich", "imperial", "measure", "trafalgar",
          "westminster", "cenotaph", "vestry", "exchequer", "observatory", "fahrenheit",
          "sangreal", "mortgage", "nowhere", "southampton", "whitehall", "ordnance"]:
    outs = []
    for i in range(2, len(w) - 1):
        a, b = w[:i], w[i:]
        if a in ALL and b in ALL and (a in COMMON or b in COMMON):
            outs.append(f"{a}|{b}")
    if outs:
        print(f"{w:12} -> {outs}")
