#!/usr/bin/env python3
"""Build the GitHub Pages site into an output directory.

Ported pattern from TRIVIUM's deploy_pages.py: copy an EXPLICIT WHITELIST of
paths, never a directory tree — a blacklist would eventually leak something.
Everything the site serves is public by definition; answers and clue text are
never in this repo at all (they live only in Supabase), so there is no date
gate here — release control is server-side.

Usage: deploy_pages.py [--out DIR]     (default: ./_site)
"""
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = BASE / "app"

WHITELIST = ["index.html", "quest.html", "config.js"]
OPTIONAL = ["grid.json"]


def main():
    out = Path(sys.argv[sys.argv.index("--out") + 1]
               if "--out" in sys.argv else BASE / "_site").resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for name in WHITELIST:
        shutil.copy2(APP / name, out / name)
    missing = []
    for name in OPTIONAL:
        if (APP / name).exists():
            shutil.copy2(APP / name, out / name)
        else:
            missing.append(name)
    (out / ".nojekyll").write_text("")
    print(f"site built at {out}: {', '.join(WHITELIST)}"
          + (f" (missing optional: {', '.join(missing)})" if missing else ""))


if __name__ == "__main__":
    main()
