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
SUBS = []   # {team, clue_idx, guess, correct, skipped, t}
HINTS = []  # {team, clue_idx, hint_no, t}
CHECKINS = []  # {team, clue_idx, passed, skipped, distance_m, t}
SIGNUPS = []  # landing-page email registrations
# mirrors hunts.hint_wait_s (env overrides it, so tests need not wait 5 minutes);
# the client counts down using the value we report, so the two cannot drift
HINT_WAIT = float(os.environ.get("MOCK_HINT_WAIT_S")
                  or HUNT.get("hint_wait_s") or 300)
LOCK = threading.Lock()


def iso_to_epoch(v):
    """Accept null / ISO-8601 string / epoch number, like the hunt file may hold."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    from datetime import datetime, timezone
    return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()


def iso(ts):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


START_T = time.time()
TEAM_BORN = {}
STARTS_AT = iso_to_epoch(HUNT.get("starts_at"))
ACTIVE = HUNT.get("active", True)
STRIKE_LIMIT = HUNT.get("strike_limit")


def started():
    return STARTS_AT is None or time.time() >= STARTS_AT


def strikes(team):
    return sum(1 for s in SUBS if s["team"] == team and not s["correct"])


def eligible(team):
    return STRIKE_LIMIT is None or strikes(team) <= STRIKE_LIMIT


def norm_code(code):
    return "".join((code or "").upper().split())


def norm_text(g):
    return "".join(ch for ch in (g or "").upper() if ch.isalnum() and ord(ch) < 128)


def norm_number(g):
    d = "".join(ch for ch in (g or "") if ch.isdigit())
    if not d:
        return ""
    return d.lstrip("0") or "0"


def qtype_of(c):
    return c.get("qtype", "text")


def answers_of(c):
    # legacy grid-hunt files carry a single 'answer'; v3 files carry 'answers'.
    # number answers use the number normalization (leading zeros stripped) so
    # a seeded value can always be matched by a normalized guess.
    raw = c["answers"] if "answers" in c else ([c["answer"]] if "answer" in c else [])
    if qtype_of(c) == "number":
        return [norm_number(str(a)) for a in raw]
    return [norm_text(str(a)) for a in raw]


def solved_at(team):
    out = {}
    for s in SUBS:
        if s["team"] == team and (s["correct"] or s.get("skipped")) \
                and s["clue_idx"] not in out:
            out[s["clue_idx"]] = s["t"]
    return out


def was_skipped(team, idx):
    return any(s["team"] == team and s["clue_idx"] == idx and s.get("skipped")
               for s in SUBS)


def is_unlocked(team, c):
    af = iso_to_epoch(c.get("available_from"))
    if af is not None and time.time() < af:
        return False
    need, mode = c.get("unlocked_by", []), c.get("unlock_mode", "any")
    if not need:
        return True
    done = solved_at(team)
    return all(n in done for n in need) if mode == "all" else any(n in done for n in need)


def latest_accepted_guess(team, idx):
    hits = [s for s in SUBS if s["team"] == team and s["clue_idx"] == idx
            and (s["correct"] or s.get("skipped"))]
    return hits[-1]["guess"] if hits else None


def available_since(team, c):
    need = c.get("unlocked_by", [])
    base = TEAM_BORN.get(team, START_T)
    if need:
        ts = [s["t"] for s in SUBS if s["team"] == team and s["clue_idx"] in need
              and (s["correct"] or s.get("skipped"))]
        base = max(ts) if ts else START_T
    # a gated clue's hint clock runs from the moment the gate was passed
    g = gate_passed_at(team, c["idx"])
    return max(base, g) if g is not None else base


def hints_taken(team, idx):
    return sum(1 for x in HINTS if x["team"] == team and x["clue_idx"] == idx)


def hint_wait_for(c, n):
    """Wait in seconds before hint n (1-based) is released, mirroring
    coalesce(c.hint_waits[n], h.hint_wait_s) in the SQL."""
    waits = c.get("hint_waits") or []
    return float(waits[n - 1]) if n <= len(waits) else HINT_WAIT


def guesses_used(team, idx):
    return sum(1 for s in SUBS if s["team"] == team and s["clue_idx"] == idx)


def budget_for(team, c, idx):
    """The effective guess budget: the clue's base allowance plus one for every
    hint taken on it, so the hint ladder is always a way out of a spent budget."""
    return None if c.get("guess_limit") is None \
        else c["guess_limit"] + hints_taken(team, idx)


def distance_m(lat1, lon1, lat2, lon2):
    import math
    return 2 * 6371008.8 * math.asin(min(1.0, math.sqrt(
        math.sin(math.radians(lat2 - lat1) / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
        * math.sin(math.radians(lon2 - lon1) / 2) ** 2)))


def gate_passed(team, c):
    if c.get("gate_lat") is None:
        return True
    return any(k["team"] == team and k["clue_idx"] == c["idx"] and k["passed"]
               for k in CHECKINS)


def gate_passed_at(team, idx):
    ts = [k["t"] for k in CHECKINS
          if k["team"] == team and k["clue_idx"] == idx and k["passed"]]
    return min(ts) if ts else None


def gated_card(team, c):
    return {"idx": c["idx"], "gated": True,
            "gate_prompt": c.get("gate_prompt") or "Are you there?",
            "since": iso(available_since(team, c))}


def open_card(team, i, fresh=False):
    """The payload for a clue the team can currently see. `fresh` is for a clue
    that has only just unlocked, where no hint or guess can exist yet. Behind an
    unpassed location gate, the clue's text does not leave the server at all."""
    c = CLUES[i]
    if not gate_passed(team, c):
        return gated_card(team, c)
    hints = c.get("hints") or []
    taken = 0 if fresh else hints_taken(team, i)
    n_hints = len(hints)
    return {"idx": i, "qtype": qtype_of(c), "kind": c.get("kind", "ground"),
            "clue_text": c["clue_text"],
            "n_hints": n_hints,
            "hints_taken": taken,
            # already paid for, so a reload restores them without a second call
            "hints_shown": hints[:taken],
            "next_hint_wait": (hint_wait_for(c, taken + 1)
                               if taken < n_hints else None),
            # a fresh clue has no hints taken, so its budget is the base one
            "guess_limit": c.get("guess_limit") if fresh else budget_for(team, c, i),
            "guesses_used": 0 if fresh else guesses_used(team, i),
            "since": iso(available_since(team, c))}


def state(team):
    done = solved_at(team)
    return {
        "solved": [{"idx": i, "answer": latest_accepted_guess(team, i),
                    "skipped": was_skipped(team, i),
                    "after_text": CLUES[i].get("after_text"),
                    "solved_at": iso(done[i])}
                   for i in sorted(done) if i in CLUES],
        "unlocked": [open_card(team, i) for i in sorted(CLUES)
                     if i not in done and is_unlocked(team, CLUES[i])],
    }


def rpc_join(body):
    team = TEAMS.get(norm_code(body.get("p_code")))
    if not team:
        return {"status": "bad_code"}
    if not ACTIVE:
        return {"status": "inactive"}
    code = norm_code(body["p_code"])
    base = {"status": "ok", "team_name": team, "hunt_id": HUNT["hunt_id"],
            "title": HUNT["title"], "starts_at": HUNT.get("starts_at"),
            "n_clues": len(CLUES), "strike_limit": STRIKE_LIMIT,
            "hint_wait_s": int(HINT_WAIT)}
    if not started():
        # pre-start, the read path reveals nothing (mirrors fedora_join)
        return {**base, "intro": None, "started": False, "strikes": 0,
                "eligible": True, "solved": [], "unlocked": []}
    return {**base, "intro": HUNT.get("intro"), "started": True,
            "strikes": strikes(code), "eligible": eligible(code), **state(code)}


def rpc_submit(body):
    code = norm_code(body.get("p_code"))
    if code not in TEAMS:
        return {"status": "bad_code"}
    if not ACTIVE:
        return {"status": "inactive"}
    if not started():
        return {"status": "not_started", "starts_at": HUNT.get("starts_at")}
    idx = body.get("p_idx")
    c = CLUES.get(idx)
    if not c:
        return {"status": "no_such_clue"}
    if idx in solved_at(code) and answers_of(c):
        return {"status": "already_solved"}
    if not is_unlocked(code, c):
        return {"status": "locked"}
    if not gate_passed(code, c):
        return {"status": "gated"}
    lim = budget_for(code, c, idx)
    if lim is not None and guesses_used(code, idx) >= lim:
        return {"status": "no_guesses_left", "guess_limit": lim,
                "hints_left": len(c.get("hints") or []) - hints_taken(code, idx)}
    last = max((s["t"] for s in SUBS if s["team"] == code and s["clue_idx"] == idx),
               default=None)
    if last is not None and time.time() - last < COOLDOWN:
        return {"status": "cooldown",
                "retry_in": int(COOLDOWN - (time.time() - last)) + 1}
    if qtype_of(c) == "number":
        import re as _re
        if len(_re.findall(r"[0-9]+", str(body.get("p_guess") or ""))) > 1:
            return {"status": "ambiguous"}
        guess = norm_number(body.get("p_guess"))
        if not guess:
            return {"status": "empty"}
        guess = guess[:40]
        acc = answers_of(c)
        if not acc:
            correct = True            # collect mode: any whole number is data
        else:
            correct = len(guess) <= 4 and guess in acc
    else:
        guess = norm_text(body.get("p_guess"))
        if not guess:
            return {"status": "empty"}
        guess = guess[:40]
        acc = answers_of(c)
        if not acc:
            correct = True                       # empty list = collect mode
        elif c.get("match_mode") == "contains":  # answer may sit inside a longer reply
            correct = any(x in guess for x in acc)
        else:
            correct = guess in acc
    before = {i for i in CLUES if is_unlocked(code, CLUES[i])}
    SUBS.append({"team": code, "clue_idx": idx, "guess": guess,
                 "correct": correct, "skipped": False, "t": time.time()})
    if not correct:
        return {"status": "wrong", "strikes": strikes(code),
                "strike_limit": STRIKE_LIMIT, "guess_limit": lim,
                "guesses_used": guesses_used(code, idx),
                "eligible": eligible(code)}   # lim already includes earned guesses
    newly = [open_card(code, i, fresh=True) for i in sorted(CLUES)
             if i != idx and i not in before and is_unlocked(code, CLUES[i])]
    return {"status": "correct", "idx": idx, "answer": guess,
            "after_text": c.get("after_text"), "newly_unlocked": newly}


def rpc_signup(body):
    e = (body.get("p_email") or "").strip().lower()
    import re as _re
    if not _re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", e) or len(e) > 200:
        return {"status": "bad_email"}
    SIGNUPS.append(e)
    return {"status": "ok"}


def rpc_hint(body):
    code = norm_code(body.get("p_code"))
    if code not in TEAMS:
        return {"status": "bad_code"}
    idx = body.get("p_idx")
    c = CLUES.get(idx)
    if not c:
        return {"status": "no_such_clue"}
    if not is_unlocked(code, c):
        return {"status": "locked"}
    if not gate_passed(code, c):
        return {"status": "gated"}
    hints = c.get("hints") or []
    if not hints:
        return {"status": "no_hint"}
    # the next one in sequence, never a later one first
    n = hints_taken(code, idx) + 1
    if n > len(hints):
        return {"status": "exhausted", "hints": hints}
    waited = time.time() - available_since(code, c)
    wait = hint_wait_for(c, n)
    if waited < wait:
        return {"status": "too_soon", "wait_s": int(wait - waited) + 1}
    HINTS.append({"team": code, "clue_idx": idx, "hint_no": n, "t": time.time()})
    # every hint taken so far comes back, so a reload never loses one
    return {"status": "ok", "idx": idx, "hints": hints[:n], "n_taken": n,
            "n_hints": len(hints),
            "next_hint_wait": hint_wait_for(c, n + 1) if n < len(hints) else None,
            "more": n < len(hints)}


def rpc_skip(body):
    code = norm_code(body.get("p_code"))
    if code not in TEAMS:
        return {"status": "bad_code"}
    idx = body.get("p_idx")
    c = CLUES.get(idx)
    if not c:
        return {"status": "no_such_clue"}
    if not is_unlocked(code, c):
        return {"status": "locked"}
    if idx in solved_at(code):
        return {"status": "already_done"}
    before = {i for i in CLUES if is_unlocked(code, CLUES[i])}
    SUBS.append({"team": code, "clue_idx": idx, "guess": "SKIPPED",
                 "correct": False, "skipped": True, "t": time.time()})
    newly = [open_card(code, i, fresh=True) for i in sorted(CLUES)
             if i != idx and i not in before and is_unlocked(code, CLUES[i])]
    return {"status": "skipped", "idx": idx, "newly_unlocked": newly}


def rpc_checkin(body):
    code = norm_code(body.get("p_code"))
    if code not in TEAMS:
        return {"status": "bad_code"}
    idx = body.get("p_idx")
    c = CLUES.get(idx)
    if not c:
        return {"status": "no_such_clue"}
    if c.get("gate_lat") is None:
        return {"status": "no_gate"}
    if not is_unlocked(code, c):
        return {"status": "locked"}
    if gate_passed(code, c):
        return {"status": "ok", "already": True, **open_card(code, idx)}
    if body.get("p_skip"):
        CHECKINS.append({"team": code, "clue_idx": idx, "passed": True,
                         "skipped": True, "distance_m": None, "t": time.time()})
        return {"status": "ok", "skipped": True, **open_card(code, idx)}
    lat, lon = body.get("p_lat"), body.get("p_lon")
    if lat is None or lon is None:
        return {"status": "no_fix"}
    d = distance_m(lat, lon, c["gate_lat"], c["gate_lon"])
    # the fix's claimed error is credited, capped so a fabricated accuracy
    # cannot pass the gate from a sofa (mirrors the SQL)
    ok = d - min(float(body.get("p_acc") or 0), 150) <= c["gate_radius_m"]
    CHECKINS.append({"team": code, "clue_idx": idx, "passed": ok,
                     "skipped": False, "distance_m": round(d), "t": time.time()})
    if not ok:
        return {"status": "far", "distance_m": round(d)}
    return {"status": "ok", **open_card(code, idx)}


def rpc_leaderboard(body):
    rows = []
    for code, name in TEAMS.items():
        mine = [s for s in SUBS if s["team"] == code]
        done = solved_at(code)
        nskip = sum(1 for i in done if was_skipped(code, i))
        rows.append({"team_name": name, "solved": len(done) - nskip,
                     "skipped": nskip, "guesses": len(mine),
                     "hints": sum(1 for x in HINTS if x["team"] == code),
                     "eligible": eligible(code),
                     "last_solve": iso(max(done.values())) if done else None})
    rows.sort(key=lambda r: (-r["eligible"], -r["solved"],
                             r["last_solve"] or "9999"))
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
        if route == "/rest/v1/rpc/fedora_signup":
            with LOCK:
                self._json(200, rpc_signup(body))
            return
        if route == "/rest/v1/rpc/fedora_checkin":
            with LOCK:
                self._json(200, rpc_checkin(body))
            return
        if route == "/rest/v1/rpc/fedora_hint":
            with LOCK:
                self._json(200, rpc_hint(body))
            return
        if route == "/rest/v1/rpc/fedora_skip":
            with LOCK:
                self._json(200, rpc_skip(body))
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
