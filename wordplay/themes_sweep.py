#!/usr/bin/env python3
"""10x10 sweep: ten mystery themes, ten keywords each (Part III of README).

Same wordlists as sweep.py (words_alpha.txt, 20k.txt beside this script).
For every keyword: exact single-word anagrams, two-word anagrams (both words
in the 20k common list), and re-splits into dictionary words. Conjectured
anagrams are letter-verified first. Findings are candidates only — grade
before use.
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
    c.subtract(Counter(c2 for c2 in inner.lower() if c2.isalpha()))
    return "".join(sorted(c.elements()))

print("=== CONJECTURE CHECKS ===")
for a, b in [("templar", "trample"), ("grail", "argil"), ("round table", "not durable"),
             ("rosetta", "toaster"), ("mona lisa", "mon salai"), ("lancelot", "lance clot"),
             ("masonic", "mosaic n"), ("santa", "satan"), ("croatoan", "a cartoon")]:
    print(f"{a!r:16} vs {b!r:16} anagram: {key(a) == key(b)}")

THEMES = {
    "grail & templars": ["knights templar", "templar", "holy grail", "grail", "baphomet",
                         "priory of sion", "mary magdalene", "rosslyn chapel", "jacques de molay",
                         "last supper"],
    "freemasonry": ["freemason", "masonic", "illuminati", "lodge", "grand master", "hiram abiff",
                    "all seeing eye", "square and compass", "mosaic pavement", "initiation"],
    "ancient egypt": ["pyramid", "sphinx", "pharaoh", "rosetta stone", "hieroglyph", "cartouche",
                      "obelisk", "tutankhamun", "valley of the kings", "cleopatra"],
    "alchemy & occult": ["alchemy", "philosophers stone", "elixir", "tarot", "pentagram",
                         "grimoire", "abracadabra", "hocus pocus", "occult", "nostradamus"],
    "shakespeare & ciphers": ["shakespeare", "william shakespeare", "stratford", "first folio",
                              "francis bacon", "anagram", "cipher", "cryptogram", "quill",
                              "globe theatre"],
    "rippers london": ["jack the ripper", "whitechapel", "leather apron", "from hell",
                       "mitre square", "scotland yard", "east end", "autumn of terror",
                       "mary kelly", "lantern"],
    "arthur & avalon": ["king arthur", "round table", "camelot", "excalibur", "avalon", "merlin",
                        "guinevere", "lancelot", "pendragon", "glastonbury"],
    "vatican & relics": ["vatican", "conclave", "pontiff", "apocrypha", "relic",
                         "shroud of turin", "sistine chapel", "swiss guard", "papal bull",
                         "canonization"],
    "lost lands": ["atlantis", "el dorado", "roanoke", "croatoan", "lemuria", "shangri la",
                   "lost city", "seven cities of gold", "terra incognita", "thule"],
    "modern conspiracy": ["roswell", "area fifty one", "dreamland", "men in black",
                          "flying saucer", "weather balloon", "zodiac killer",
                          "majestic twelve", "hangar eighteen", "crop circle"],
}

by_key = defaultdict(list)
for w in ALL:
    by_key[key(w)].append(w)
common3 = [w for w in COMMON_LIST if len(w) >= 3]
kmap = defaultdict(list)
for w in common3:
    kmap[key(w)].append(w)

for theme, words in THEMES.items():
    print(f"\n############ {theme.upper()} ############")
    for t in words:
        tk = key(t)
        lines = []
        # single-word anagrams (full dictionary)
        singles = [h for h in by_key.get(tk, []) if h != t.replace(" ", "")]
        if singles:
            lines.append("  1-word: " + ", ".join(sorted(singles, key=lambda w: RANK.get(w, 99999))[:8]))
        # two-word anagrams (common words only)
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
            lines.append("  2-word: " + " | ".join("+".join(p) for p in out[:14]))
        # re-splits of the solid form
        solid = t.replace(" ", "")
        outs = []
        for i in range(2, len(solid) - 1):
            a, b = solid[:i], solid[i:]
            if a in ALL and b in ALL and (a in COMMON or b in COMMON) and {a, b} != set(t.split()):
                outs.append(f"{a}|{b}")
        if outs:
            lines.append("  splits: " + ", ".join(outs))
        if lines:
            print(f"\n-- {t}")
            print("\n".join(lines))
