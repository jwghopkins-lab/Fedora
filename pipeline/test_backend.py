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
    print("MOCK DRIVE PASS")
finally:
    srv.kill()
