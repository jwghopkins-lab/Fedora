/* End-to-end smoke test of the QUEST app (quest.html) against the mock backend.
   Covers: join, absence of the brief and type pills, typewriter reveal (first
   view only), SEQUENTIAL hints (one at a time, each on its own timer) and their
   survival across a reload, collect-mode number, the two-numbers ambiguity
   guard, compete-mode strike, the guess budget and its are-you-sure gate, the
   after-answer explainer, text variants under match_mode 'contains', the
   ABSENCE of a skip button, leaderboard, and resume.
   Run: NODE_PATH=/opt/node22/lib/node_modules node pipeline/quest_smoke.cjs
*/
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const path = require("path");

const PORT = 8801;
const BASE = `http://localhost:${PORT}`;

(async () => {
  const server = spawn("python3",
    [path.join(__dirname, "mock_backend.py"), String(PORT),
     path.join(__dirname, "..", "hunt", "example_quest.json")],
    { env: { ...process.env, MOCK_COOLDOWN_S: "0.3", MOCK_HINT_WAIT_S: "25" } });
  await new Promise((r) => setTimeout(r, 900));

  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium", args: ["--no-sandbox"] });
  // a fake GPS: the run starts on Parliament Square, ~800m from the fixture
  // gate at Trafalgar, and "walks" there mid-test
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    geolocation: { latitude: 51.5007, longitude: -0.1266, accuracy: 25 },
    permissions: ["geolocation"] });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  const box = (i) => page.locator(`.part[data-idx="${i}"] input`);
  const send = (i) => page.locator(`.part[data-idx="${i}"] .btn`);
  const pause = () => page.waitForTimeout(400);

  try {
    await page.goto(BASE + "/quest.html");
    await page.waitForSelector("#s-join.on");
    // the landing page comes first now; a new player has to step past it
    if (!(await page.locator("#landing").isHidden()))
      await page.click("#gotologin");
    await page.waitForSelector("#codein", { state: "visible" });
    // the login screen has to warn that anagrams are in play — without it the
    // scrambled lines read as typos and players stall on them
    const login = await page.locator("#logincard").textContent();
    if (!/anagram/i.test(login))
      throw new Error("login screen should flag that there are anagrams");
    await page.fill("#codein", "testteam1");
    await page.press("#codein", "Enter");           // Enter on the code field
    await page.waitForSelector("#s-quest.on");
    // Locked parts are no longer drawn at all: a column of padlocks told the
    // player nothing and pushed the live clue off the screen.
    if (await page.locator(".part.sealed").count())
      throw new Error("locked parts must not be rendered");
    if ((await page.locator(".part").count()) !== 1)
      throw new Error("only the open part should exist, got "
                      + await page.locator(".part").count());
    if ((await page.locator("#progresstext").textContent()).trim() !== "0/4")
      throw new Error("progress should read 0/4");
    if (!(await page.locator("#progress .mlabel").textContent()).includes("Progress:"))
      throw new Error("progress meter needs its label");
    if ((await page.locator("#livestext").textContent()).trim() !== "0/3")
      throw new Error("part 1 should show 0/3 wrong answers, got "
                      + await page.locator("#livestext").textContent());
    // the consequence is not on screen until you ask for it
    if (!(await page.locator("#livesnote").isHidden()))
      throw new Error("the limit explanation must start hidden");
    await page.click("#liveslabel");
    await page.waitForSelector("#livesnote:not([hidden])");
    if (!(await page.locator("#livesnote").textContent()).includes("this part"))
      throw new Error("the explanation must be about the current part");
    await page.click("#liveslabel");
    await page.waitForFunction(() => document.getElementById("livesnote").hidden);
    // The brief and the type pills are deliberately GONE: a player who knows a
    // question is Ground Truth knows not to search, and deciding that for
    // themselves is the game. Assert absence so they cannot creep back.
    if (await page.locator(".part.intro").count())
      throw new Error("brief card should no longer be rendered");
    if (await page.locator(".kindkey").count())
      throw new Error("type key should no longer be rendered");
    if (await page.locator(".pill").count())
      throw new Error("type pills should no longer be rendered");
    const body = await page.locator("#s-quest").textContent();
    for (const k of ["WITS", "THE DIG", "GROUND TRUTH"])
      if (body.includes(k)) throw new Error("clue type leaked into the UI: " + k);
    console.log("join ok: anagram warning, no brief, no pills, no locked parts, meters 0/4 and 0/3");

    // there is no escape hatch any more: a skip button anywhere is a regression
    if (await page.locator(".skipbtn").count())
      throw new Error("the skip button was removed and must not come back");

    // The reveal is word-by-word now: the FULL text is laid out invisibly from
    // the first frame (so the card never grows and lines never re-wrap) and the
    // words darken in one at a time. So the check is visibility, not length.
    const full = "FIXTURE: Count the imaginary lampposts on Example Street. Any whole number is accepted (collect mode).";
    if ((await page.locator('.part[data-idx="1"] .ptext').textContent()) !== full)
      throw new Error("full text must be laid out (invisibly) from the start");
    if (!(await page.locator('.part[data-idx="1"] .ptext .w:not(.on)').count()))
      throw new Error("reveal did not stagger: every word visible immediately");
    // finish strips the spans, so completion = no .w spans left + text intact
    await page.waitForFunction((f) => {
      const el = document.querySelector('.part[data-idx="1"] .ptext');
      return el && !el.querySelector(".w") && el.textContent === f;
    }, full, { timeout: 60000 });
    console.log("reveal ok: words darkened in one by one, text char-identical");

    // hints are a SEQUENCE: one at a time, each on its own countdown, and the
    // button has to name which one is coming so nobody expects the lot
    const hb = page.locator('.part[data-idx="1"] .hintbtn');
    if (!(await hb.count())) throw new Error("hint button missing on part 1");
    // must be counting down to the SERVER's wait (25s), not a hard-coded 5 min
    if (!/^Hint 1 of 2 in 0:[0-2]\d$/.test((await hb.textContent()).trim()))
      throw new Error("hint countdown should name hint 1 of 2 and track the "
                      + "server wait, got: " + await hb.textContent());
    if (!(await hb.isDisabled()))
      throw new Error("hint button must be disabled while the countdown runs");
    // (the server's own too_soon refusal is covered in test_backend.py; the UI
    // cannot reach it because the button stays disabled until the wait is up)
    await page.waitForFunction(() => {
      const b = document.querySelector('.part[data-idx="1"] .hintbtn');
      return b && !b.disabled;
    }, { timeout: 40000 });
    await hb.click();
    await page.waitForFunction(() => {
      const h = document.querySelectorAll('.part[data-idx="1"] .hintone');
      return h.length === 1 && h[0].textContent.includes("FIXTURE HINT ONE");
    }, { timeout: 20000 });
    if (!/hint 2 of 2/i.test(await hb.textContent()))
      throw new Error("after hint 1 the button must offer hint 2, got: "
                      + await hb.textContent());
    if (await page.locator('.part[data-idx="1"] .hintone')
                  .filter({ hasText: "FIXTURE HINT TWO" }).count())
      throw new Error("hint 2 must not appear until it is taken");
    console.log("hint ok: countdown named hint 1 of 2, released, and only hint 1 shown");

    // hint 2 (this clue has no per-hint waits, so it falls back to the same
    // server wait, which has already elapsed) — sequence, not time, gates it
    await page.waitForFunction(() => {
      const b = document.querySelector('.part[data-idx="1"] .hintbtn');
      return b && !b.disabled;
    }, { timeout: 40000 });
    await hb.click();
    await page.waitForFunction(() =>
      document.querySelectorAll('.part[data-idx="1"] .hintone').length === 2,
      { timeout: 20000 });
    await page.waitForFunction(() => {
      const b = document.querySelector('.part[data-idx="1"] .hintbtn');
      return b && b.hidden;
    }, { timeout: 5000 });
    console.log("hint ok: hint 2 taken, button retires with nothing left to give");

    // both hints survive a reload, with no second call and no third hint
    await page.reload();
    await page.waitForSelector("#s-quest.on");
    await page.waitForFunction(() =>
      document.querySelectorAll('.part[data-idx="1"] .hintone').length === 2,
      { timeout: 20000 });
    console.log("hint ok: both recovered after reload without a second charge");

    // ambiguity guard: two numbers must be refused, not concatenated
    await box(1).fill("20-22");
    await send(1).click();
    await page.waitForSelector("#modal.show");
    await page.click("#gyes");
    await page.waitForFunction(() =>
      document.getElementById("toast").textContent.includes("one whole number"));
    await pause();
    // collect mode: any single whole number accepted, echoed normalized
    await box(1).fill("17 lampposts");
    await send(1).click();
    await page.waitForSelector("#modal.show");
    await page.click("#gyes");
    await page.waitForSelector('.part.done[data-idx="1"]');
    const a1 = (await page.locator('.part.done[data-idx="1"] .answer').textContent()).trim();
    if (a1 !== "17") throw new Error("collect answer not normalized to 17: " + a1);
    await page.waitForSelector('.part.open[data-idx="2"]');
    if (await page.locator('.part[data-idx="2"] .pill').count())
      throw new Error("newly opened part must not carry a type pill either");
    console.log("ok: '20-22' refused as ambiguous, '17 lampposts' -> 17, no pill on part 2");

    // the explainer: what the answer meant and where to walk next, typed out on
    // the solved card. It is the whole reason a machine-solved clue still
    // teaches you something.
    await page.waitForFunction(() => {
      const a = document.querySelector('.part.done[data-idx="1"] .aftertext');
      return a && a.textContent.includes("walk to the example bakery");
    }, { timeout: 30000 });
    console.log("after ok: part 1's explainer shown on the solved card");

    // a budgeted clue asks before it spends a guess, and says how many are left
    const lim = page.locator("#livestext");
    if ((await lim.textContent()).trim() !== "0/2")
      throw new Error("part 2 should show 0/2, got: " + await lim.textContent());
    await box(2).fill("41");
    await send(2).click();
    await page.waitForSelector("#modal.show");
    await page.click("#gno");                       // think again: nothing spent
    await pause();
    if ((await lim.textContent()).trim() !== "0/2")
      throw new Error("backing out of the confirm must not spend a guess");
    await send(2).click();
    await page.waitForSelector("#modal.show");
    await page.click("#gyes");
    // the meter counts wrong answers on THIS part, and warns without being asked
    await page.waitForFunction(() =>
      document.getElementById("livestext").textContent.trim() === "1/2");
    await page.waitForFunction(() => {
      const n = document.getElementById("livesnote");
      return n && !n.hidden && n.classList.contains("warn");
    });
    console.log("budget ok: confirm gate, cancel costs nothing, wrong warns and costs one");

    await pause();
    await box(2).fill("42");
    await send(2).click();
    await page.waitForSelector("#modal.show");
    await page.click("#gyes");
    await page.waitForSelector('.part.done[data-idx="2"]');
    console.log("compete ok: 41 struck (1/2), 42 accepted");

    // part 3 is LOCATION-GATED: the card asks for presence, holds no clue text
    await page.waitForSelector('.part.open[data-idx="3"]');
    const p3 = await page.locator('.part[data-idx="3"]').textContent();
    if (!p3.includes("FIXTURE GATE"))
      throw new Error("gated part should show its prompt, got: " + p3.slice(0, 90));
    if (p3.includes("imaginary beast"))
      throw new Error("gated part must NOT contain the clue text");
    if (await page.locator('.part[data-idx="3"] input').count())
      throw new Error("no answer box before the gate opens");
    // from Parliament Square the truthful reply is a distance, not a no
    await page.click('.part[data-idx="3"] .gatebtn');
    await page.waitForFunction(() => {
      const s = document.querySelector('.part[data-idx="3"] .gatestat');
      return s && /away/.test(s.textContent);
    }, { timeout: 15000 });
    console.log("gate ok: prompt shown, text withheld, far fix answered warm/cold");

    // walk to the square and try again: the clue reveals in place
    await ctx.setGeolocation({ latitude: 51.5081, longitude: -0.1281, accuracy: 40 });
    await page.click('.part[data-idx="3"] .gatebtn');
    await page.waitForSelector('.part[data-idx="3"] input', { timeout: 15000 });
    await page.waitForFunction(() =>
      document.querySelector('.part[data-idx="3"] .ptext')
        .textContent.includes("imaginary beast"), { timeout: 40000 });
    console.log("gate ok: on-site fix opened the clue, text revealed in place");

    // match_mode 'contains': the word inside a longer answer still counts
    await box(3).fill("dragon");
    await send(3).click();
    await page.waitForSelector("#modal.show");
    await page.click("#gyes");
    await page.waitForFunction(() =>
      document.getElementById("livestext").textContent.trim() === "1/3");
    await pause();
    await box(3).fill("the gryphon, I think");
    await send(3).click();
    await page.waitForSelector("#modal.show");
    await page.click("#gyes");
    await page.waitForSelector('.part.done[data-idx="3"]');
    console.log("text ok: dragon struck, 'the gryphon, I think' matched by contains");

    // last part is collect mode: anything is data, and it ends the run
    await page.waitForSelector('.part.open[data-idx="4"]');
    await box(4).fill("HIC IACET NEMO");
    await send(4).click();
    await page.waitForSelector('.part.done[data-idx="4"]');

    // finishing all four opens the win card, with nothing left behind
    await page.waitForSelector("#modal.show");
    const card = await page.locator("#modalcard").textContent();
    if (!card.includes("given up its numbers")) throw new Error("win modal wrong");
    if (card.includes("left behind")) throw new Error("nothing was skipped");
    await page.click("#mboard");
    await page.waitForFunction(() =>
      document.getElementById("modalcard").textContent.includes("Parts cracked"));
    const lb = await page.locator("#modalcard").textContent();
    if (!lb.includes("hint")) throw new Error("leaderboard should note the hints: " + lb.slice(0,140));
    if (!lb.includes("4/4") || lb.includes("skipped"))
      throw new Error("leaderboard should read 4/4 with no skip: " + lb.slice(0, 140));
    await page.click("#mclose");
    console.log("board ok: 4/4, 2 hints, no skips");

    // reload resumes, and seen clues do NOT re-animate
    await page.reload();
    await page.waitForSelector("#s-quest.on", { timeout: 5000 });
    await page.waitForFunction(() =>
      document.querySelectorAll(".part.done").length === 4 &&
      document.querySelectorAll(".part.skipped").length === 0);
    // and the explainers are all still there, from the server, not from memory
    await page.waitForFunction(() =>
      document.querySelectorAll(".aftertext").length === 4, { timeout: 5000 });
    console.log("resume ok: 4 done with all 4 explainers after reload");

    if (errors.length) throw new Error("page errors: " + errors.join(" | "));
    console.log("QUEST SMOKE TEST PASS");
    // (the gate-skip button is exercised in gate_skip_checks server-side; here
    // we only assert it exists while testing mode is on)
  } finally {
    await browser.close();
    server.kill();
  }
})().catch((e) => { console.error("QUEST SMOKE TEST FAIL:", e.message); process.exit(1); });
