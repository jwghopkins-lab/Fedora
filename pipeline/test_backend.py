#!/usr/bin/env python3
"""Drive the mock backend through the whole unlock graph and assert semantics.

This is the behavioural contract for app/sql/schema.sql expressed as a test
against the mock: if the SQL and the mock ever diverge, whichever changed last
is the bug. CI gates on this script's exit code.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PORT = 8791
BASE = f"http://localhost:{PORT}"
MOCK = Path(__file__).resolve().parent / "mock_backend.py"


def rpc(name, **kw):
    req = urllib.request.Request(f"{BASE}/rest/v1/rpc/{name}",
                                 data=json.dumps(kw).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


def expect(cond, msg):
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"ok: {msg}")


srv = subprocess.Popen(["python3", str(MOCK), str(PORT)],
                       env={**os.environ, "MOCK_COOLDOWN_S": "0.3"})
time.sleep(0.8)
try:
    r = rpc("fedora_join", p_code="nope")
    expect(r["status"] == "bad_code", "bad join code rejected")
    r = rpc("fedora_join", p_code="testteam1 ")
    expect(r["status"] == "ok" and r["team_name"] == "Test Team",
           "join normalizes code (lower + trailing space)")
    expect([u["idx"] for u in r["unlocked"]] == [1, 2], "start clues are 1 and 2")
    expect(r["solved"] == [], "nothing solved yet")

    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=5, p_guess="OTTER")
    expect(r["status"] == "locked", "locked clue rejects even a right answer")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="scarlet")
    expect(r["status"] == "wrong", "wrong guess on open clue")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="crimson")
    expect(r["status"] == "cooldown", "immediate retry hits cooldown")
    time.sleep(0.35)
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="  crimson!! ")
    expect(r["status"] == "correct" and r["answer"] == "CRIMSON",
           "guess normalization (case, spaces, punctuation)")
    expect([u["idx"] for u in r["newly_unlocked"]] == [3], "solving 1 unlocks 3")
    # a newly unlocked clue must arrive fully described: the UI paints its pill
    # and hint button straight from this payload, and a poll may not re-render
    expect(set(r["newly_unlocked"][0]) >=
           {"idx", "qtype", "kind", "clue_text", "has_hint", "since", "hint_taken"},
           "newly_unlocked describes kind + hint state, not just idx/qtype/text")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="CRIMSON")
    expect(r["status"] == "already_solved", "re-submit blocked")

    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=2, p_guess="SUNDIAL")
    expect([u["idx"] for u in r["newly_unlocked"]] == [4], "solving 2 unlocks 4")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=4, p_guess="LANTERN")
    expect(sorted(u["idx"] for u in r["newly_unlocked"]) == [5, 6],
           "solving 4 unlocks 5 (any-mode) and 6")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=5, p_guess="OTTER")
    expect(r["newly_unlocked"] == [], "7 needs ALL of 5+6: not yet")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=6, p_guess="ORCHARD")
    expect([u["idx"] for u in r["newly_unlocked"]] == [7],
           "solving 6 completes ALL-gate, 7 unlocks")
    expect("{5}" in r["newly_unlocked"][0]["clue_text"],
           "clue 7 carries its {5} placeholder")

    board = rpc("fedora_leaderboard", p_hunt="example")
    expect(board[0]["team_name"] == "Test Team" and board[0]["solved"] == 5,
           "leaderboard: Test Team top with 5 solved")
    expect(board[1]["solved"] == 0, "rival at 0")

    r = rpc("fedora_join", p_code="TESTTEAM1")
    expect(len(r["solved"]) == 5 and [u["idx"] for u in r["unlocked"]] == [3, 7],
           "rejoin resumes: 5 solved, 3 and 7 open")
    expect(r["strikes"] == 1 and r["strike_limit"] == 3 and r["eligible"] is True,
           "join reports 1 strike of 3 (cooldown-rejected retry logs nothing)")
    print("MOCK DRIVE PASS")
finally:
    srv.kill()


# ---- variant hunts: the paths the fixture's nulls would otherwise never test
import copy
import tempfile

BASEHUNT = json.loads((MOCK.parent.parent / "hunt" / "example_hunt.json").read_text())


def with_variant(mutate, port, checks, env=None):
    hunt = copy.deepcopy(BASEHUNT)
    mutate(hunt)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(hunt, f)
        path = f.name
    global BASE
    BASE = f"http://localhost:{port}"
    p = subprocess.Popen(["python3", str(MOCK), str(port), path],
                         env={**os.environ, "MOCK_COOLDOWN_S": "0.3", **(env or {})})
    time.sleep(0.8)
    try:
        checks()
    finally:
        p.kill()


def pre_start_checks():
    r = rpc("fedora_join", p_code="TESTTEAM1")
    expect(r["status"] == "ok" and r["started"] is False,
           "pre-start join reports started=false")
    expect(r["solved"] == [] and r["unlocked"] == [],
           "pre-start join reveals NO clue text (leak fix)")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="CRIMSON")
    expect(r["status"] == "not_started", "pre-start submit blocked")


def inactive_checks():
    r = rpc("fedora_join", p_code="TESTTEAM1")
    expect(r["status"] == "inactive", "inactive hunt refuses join")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="CRIMSON")
    expect(r["status"] == "inactive", "inactive hunt refuses submit")


def timed_clue_checks():
    r = rpc("fedora_join", p_code="TESTTEAM1")
    expect([u["idx"] for u in r["unlocked"]] == [2],
           "future available_from keeps clue 1 hidden, clue 2 open")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="CRIMSON")
    expect(r["status"] == "locked", "timed clue rejects submit before release")


def strikes_checks():
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="NOPEA")
    expect(r["status"] == "wrong" and r["strikes"] == 1 and r["eligible"] is True,
           "first wrong guess: 1 strike, still eligible (limit 1)")
    time.sleep(0.35)
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="NOPEB")
    expect(r["status"] == "wrong" and r["strikes"] == 2 and r["eligible"] is False,
           "second wrong guess: over the limit, no longer eligible")
    time.sleep(0.35)
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="CRIMSON")
    expect(r["status"] == "correct", "ineligible team can still play and solve")
    board = rpc("fedora_leaderboard", p_hunt="example")
    us = [t for t in board if t["team_name"] == "Test Team"][0]
    rival = [t for t in board if t["team_name"] == "Rival Team"][0]
    expect(us["eligible"] is False and rival["eligible"] is True,
           "leaderboard flags us ineligible, rival eligible")
    expect(board[0]["team_name"] == "Rival Team",
           "eligible team sorts above ineligible despite fewer solves")


def hint_checks():
    r = rpc("fedora_join", p_code="TESTTEAM1")
    expect(r.get("hint_wait_s") == 1,
           "join reports the hunt's hint_wait_s so the UI counts to the real moment")
    open1 = [u for u in r["unlocked"] if u["idx"] == 1][0]
    expect(open1["has_hint"] is True and open1["hint_taken"] is False,
           "open clue advertises an untaken hint")
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=1)
    expect(r["status"] == "too_soon" and r["wait_s"] >= 1,
           "hint refused before the wait, with seconds remaining")
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=5)
    expect(r["status"] == "locked", "hint refused on a locked clue")
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=2)
    expect(r["status"] == "no_hint", "clue without a hint says so")
    r = rpc("fedora_hint", p_code="nope", p_idx=1)
    expect(r["status"] == "bad_code", "hint refuses an unknown team")
    time.sleep(1.1)
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=1)
    expect(r["status"] == "ok" and r["hint"] == "TEST HINT: it is a shade of red.",
           "hint released after the wait")
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=1)
    expect(r["status"] == "ok", "re-asking is idempotent, not a second charge")
    board = rpc("fedora_leaderboard", p_hunt="example")
    us = [t for t in board if t["team_name"] == "Test Team"][0]
    expect(us["hints"] == 1, "leaderboard counts the hint once")
    r = rpc("fedora_join", p_code="TESTTEAM1")
    open1 = [u for u in r["unlocked"] if u["idx"] == 1][0]
    expect(open1["hint_taken"] is True, "rejoin remembers the hint was taken")


with_variant(lambda h: h.update(starts_at="2999-01-01T00:00:00Z"), PORT + 1, pre_start_checks)
with_variant(lambda h: h.update(active=False), PORT + 2, inactive_checks)
with_variant(lambda h: h["clues"][0].update(available_from="2999-01-01T00:00:00Z"),
             PORT + 3, timed_clue_checks)
with_variant(lambda h: h.update(strike_limit=1), PORT + 4, strikes_checks)
with_variant(lambda h: (h.update(hint_wait_s=1),
                        h["clues"][0].update(hint="TEST HINT: it is a shade of red.")),
             PORT + 5, hint_checks, env={"MOCK_HINT_WAIT_S": "1"})
print("VARIANT DRIVES PASS")
