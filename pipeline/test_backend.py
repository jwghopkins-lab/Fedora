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
    # a newly unlocked clue must arrive fully described: the UI paints its hint
    # button and guess counter straight from this payload, and a poll may not
    # re-render before the player looks
    expect(set(r["newly_unlocked"][0]) >=
           {"idx", "qtype", "kind", "clue_text", "since", "n_hints", "hints_taken",
            "hints_shown", "next_hint_wait", "guess_limit", "guesses_used"},
           "newly_unlocked describes hint and guess state, not just idx/qtype/text")
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


HINT_A = "TEST HINT ONE: it is a shade of red."
HINT_B = "TEST HINT TWO: it rhymes with 'his son'."


def hint_checks():
    r = rpc("fedora_join", p_code="TESTTEAM1")
    expect(r.get("hint_wait_s") == 1,
           "join reports the hunt's hint_wait_s so the UI counts to the real moment")
    open1 = [u for u in r["unlocked"] if u["idx"] == 1][0]
    expect(open1["n_hints"] == 2 and open1["hints_taken"] == 0
           and open1["hints_shown"] == [],
           "open clue advertises 2 hints, none taken")
    expect(open1["next_hint_wait"] == 1,
           "state reports the wait on the NEXT hint, so the UI counts to the "
           "moment the server will actually open")
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
    expect(r["status"] == "ok" and r["hints"] == [HINT_A] and r["n_taken"] == 1,
           "hint 1 released after ITS wait — and only hint 1")
    expect(r["more"] is True and r["next_hint_wait"] == 3,
           "the reply carries the wait on hint 2, not a repeat of hint 1's")
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=1)
    expect(r["status"] == "too_soon",
           "hint 2 is gated on its OWN longer wait, not released by hint 1")
    time.sleep(2.1)
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=1)
    expect(r["status"] == "ok" and r["hints"] == [HINT_A, HINT_B]
           and r["n_taken"] == 2 and r["more"] is False,
           "hint 2 released, and every hint so far comes back with it")
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=1)
    expect(r["status"] == "exhausted" and r["hints"] == [HINT_A, HINT_B],
           "asking past the end returns what was paid for, charging nothing")
    board = rpc("fedora_leaderboard", p_hunt="example")
    us = [t for t in board if t["team_name"] == "Test Team"][0]
    expect(us["hints"] == 2, "leaderboard counts both hints, not the clue")
    r = rpc("fedora_join", p_code="TESTTEAM1")
    open1 = [u for u in r["unlocked"] if u["idx"] == 1][0]
    expect(open1["hints_taken"] == 2 and open1["hints_shown"] == [HINT_A, HINT_B],
           "rejoin returns the hints already paid for, so a reload loses none")
    expect(open1["next_hint_wait"] is None,
           "no next wait once every hint is spent")


def budget_checks():
    r = rpc("fedora_join", p_code="TESTTEAM1")
    open1 = [u for u in r["unlocked"] if u["idx"] == 1][0]
    expect(open1["guess_limit"] == 2 and open1["guesses_used"] == 0,
           "open clue advertises its guess budget and what is left of it")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="NOPEA")
    expect(r["status"] == "wrong" and r["guess_limit"] == 2 and r["guesses_used"] == 1,
           "a wrong guess reports the budget back so the UI can warn")
    time.sleep(0.35)
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="NOPEB")
    expect(r["status"] == "wrong" and r["guesses_used"] == 2, "second guess spent")
    time.sleep(0.35)
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="CRIMSON")
    expect(r["status"] == "no_guesses_left" and r["guess_limit"] == 2,
           "budget is enforced on the SERVER: even the right answer is refused")
    expect(r["hints_left"] == 1,
           "and it says a hint is still available, so this is not a dead end")
    # With no skip button, a spent budget would strand a team forever. A hint is
    # the way out: taking one buys a guess back.
    time.sleep(1.1)
    r = rpc("fedora_hint", p_code="TESTTEAM1", p_idx=1)
    expect(r["status"] == "ok", "the hint is available on the spent clue")
    r = rpc("fedora_join", p_code="TESTTEAM1")
    open1 = [u for u in r["unlocked"] if u["idx"] == 1][0]
    expect(open1["guess_limit"] == 3 and open1["guesses_used"] == 2,
           "the taken hint raised the budget from 2 to 3")
    time.sleep(0.35)
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=1, p_guess="CRIMSON")
    expect(r["status"] == "correct", "the guess the hint bought is accepted")
    r = rpc("fedora_submit", p_code="TESTTEAM1", p_idx=2, p_guess="SUNDIAL")
    expect(r["status"] == "correct", "an unlimited clue is unaffected")
    expect(r.get("after_text") == "TEST AFTER: the dial told the hour by shadow.",
           "a correct answer returns the explainer for that clue")
    r = rpc("fedora_join", p_code="TESTTEAM1")
    s2 = [s for s in r["solved"] if s["idx"] == 2][0]
    expect(s2.get("after_text") == "TEST AFTER: the dial told the hour by shadow.",
           "the explainer comes back on every reload and every teammate's phone")


with_variant(lambda h: h.update(starts_at="2999-01-01T00:00:00Z"), PORT + 1, pre_start_checks)
with_variant(lambda h: h.update(active=False), PORT + 2, inactive_checks)
with_variant(lambda h: h["clues"][0].update(available_from="2999-01-01T00:00:00Z"),
             PORT + 3, timed_clue_checks)
with_variant(lambda h: h.update(strike_limit=1), PORT + 4, strikes_checks)
with_variant(lambda h: (h.update(hint_wait_s=1),
                        h["clues"][0].update(hints=[HINT_A, HINT_B],
                                             hint_waits=[1, 3])),
             PORT + 5, hint_checks, env={"MOCK_HINT_WAIT_S": "1"})
with_variant(lambda h: (h.update(hint_wait_s=1),
                        h["clues"][0].update(guess_limit=2, hints=[HINT_A],
                                             hint_waits=[1]),
                        h["clues"][1].update(
                          after_text="TEST AFTER: the dial told the hour by shadow.")),
             PORT + 6, budget_checks, env={"MOCK_HINT_WAIT_S": "1"})
print("VARIANT DRIVES PASS")
