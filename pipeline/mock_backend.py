#!/usr/bin/env python3
"""Local mock of the three Supabase RPC endpoints, plus static serving of app/.

Ported from TRIVIUM's mock_backend.py (threading server, config.js
interception, SLOW_POST_MS race reproduction); the route handlers now
impersonate PostgREST's /rest/v1/rpc/fedora_join, fedora_submit and
fedora_leaderboard with the same JSON shapes as app/sql/schema.sql defines.
Behavioural contract: if mock and SQL disagree, whichever changed last is the
bug. Serves the app same-origin, so no CORS preflight is involved.

Usage: mock_backend.py [port] [huntfile]      (default 8765, hunt/example_hunt.json)
Env:   SLOW_POST_MS delays the submit route only.
State is in-memory per run; GET /__state returns submissions for tests.
"""
import json
import os
import sys
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = BASE / "app"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
HUNT = json.loads(Path(sys.argv[2] if len(sys.argv) > 2
                       else BASE / "hunt" / "example_hunt.json").read_text())

COOLDOWN = float(os.environ.get("MOCK_COOLDOWN_S", "15"))   # SQL stays at 15s
TEAMS = {t["code"].upper(): t["name"] for t in HUNT["teams"]}
CLUES = {c["idx"]: c for c in HUNT["clues"]}
SUBS = []   # {team, clue_idx, guess, correct, t}
LOCK = threading.Lock()


def norm_code(code):
    return "".join((code or "").upper().split())


def norm_guess(g):
    return "".join(ch for ch in (g or "").upper() if "A" <= ch <= "Z")


def solved_at(team):
    out = {}
    for s in SUBS:
        if s["team"] == team and s["correct"] and s["clue_idx"] not in out:
            out[s["clue_idx"]] = s["t"]
    return out


def is_unlocked(team, c):
    if c.get("available_from") and time.time() < c["available_from"]:
        return False
    need, mode = c.get("unlocked_by", []), c.get("unlock_mode", "any")
    if not need:
        return True
    done = solved_at(team)
    return all(n in done for n in need) if mode == "all" else any(n in done for n in need)


def state(team):
    done = solved_at(team)
    return {
        "solved": [{"idx": i, "answer": CLUES[i]["answer"],
                    "solved_at": done[i]} for i in sorted(done)],
        "unlocked": [{"idx": i, "clue_text": CLUES[i]["clue_text"]}
                     for i in sorted(CLUES)
                     if i not in done and is_unlocked(team, CLUES[i])],
    }


def rpc_join(body):
    team = TEAMS.get(norm_code(body.get("p_code")))
    if not team:
        return {"status": "bad_code"}
    return {"status": "ok", "team_name": team, "hunt_id": HUNT["hunt_id"],
            "title": HUNT["title"], "starts_at": HUNT.get("starts_at"),
            "started": True, **state(norm_code(body["p_code"]))}


def rpc_submit(body):
    code = norm_code(body.get("p_code"))
    if code not in TEAMS:
        return {"status": "bad_code"}
    idx = body.get("p_idx")
    c = CLUES.get(idx)
    if not c:
        return {"status": "no_such_clue"}
    if idx in solved_at(code):
        return {"status": "already_solved"}
    if not is_unlocked(code, c):
        return {"status": "locked"}
    last = max((s["t"] for s in SUBS if s["team"] == code and s["clue_idx"] == idx),
               default=None)
    if last is not None and time.time() - last < COOLDOWN:
        return {"status": "cooldown",
                "retry_in": int(COOLDOWN - (time.time() - last)) + 1}
    guess = norm_guess(body.get("p_guess"))
    if not guess:
        return {"status": "empty"}
    before = {i for i in CLUES if is_unlocked(code, CLUES[i])}
    correct = guess == c["answer"]
    SUBS.append({"team": code, "clue_idx": idx, "guess": guess,
                 "correct": correct, "t": time.time()})
    if not correct:
        return {"status": "wrong"}
    newly = [{"idx": i, "clue_text": CLUES[i]["clue_text"]}
             for i in sorted(CLUES)
             if i != idx and i not in before and is_unlocked(code, CLUES[i])]
    return {"status": "correct", "idx": idx, "answer": c["answer"],
            "newly_unlocked": newly}


def rpc_leaderboard(body):
    rows = []
    for code, name in TEAMS.items():
        mine = [s for s in SUBS if s["team"] == code]
        done = solved_at(code)
        rows.append({"team_name": name, "solved": len(done), "guesses": len(mine),
                     "last_solve": max(done.values()) if done else None})
    rows.sort(key=lambda r: (-r["solved"], r["last_solve"] or float("inf")))
    return rows


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(APP), **kw)

    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/grid.json":
            # serve geometry derived from THIS hunt file, not the committed
            # production grid.json — they are different hunts
            import build_hunt
            self._json(200, build_hunt.grid_json(HUNT))
            return
        if self.path == "/config.js":
            body = (f'window.FEDORA_CONFIG = {{ SUPABASE_URL: "http://localhost:{PORT}",'
                    f' SUPABASE_ANON_KEY: "mock-anon-key",'
                    f' HUNT_ID: "{HUNT["hunt_id"]}" }};').encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/__state":
            with LOCK:
                self._json(200, SUBS)
            return
        super().do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n)) if n else {}
        route = self.path.split("?")[0]
        if route == "/rest/v1/rpc/fedora_submit":
            # delay this route only (TRIVIUM lesson: slowing every POST starves
            # unrelated requests and fails innocent code)
            time.sleep(int(os.environ.get("SLOW_POST_MS", "0")) / 1000)
            with LOCK:
                self._json(200, rpc_submit(body))
            return
        if route == "/rest/v1/rpc/fedora_join":
            with LOCK:
                self._json(200, rpc_join(body))
            return
        if route == "/rest/v1/rpc/fedora_leaderboard":
            with LOCK:
                self._json(200, rpc_leaderboard(body))
            return
        self.send_error(404)


if __name__ == "__main__":
    print(f"fedora mock backend on http://localhost:{PORT}, "
          f"hunt {HUNT['hunt_id']!r}, serving {APP}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
