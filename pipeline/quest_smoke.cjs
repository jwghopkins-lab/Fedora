/* End-to-end smoke test of the QUEST app (quest.html) against the mock backend.
   Covers: join, absence of the brief and type pills, typewriter reveal (first
   view only), the hint
   countdown and its recovery after a reload, collect-mode number, the
   two-numbers ambiguity guard, compete-mode strike, text variants, the skip
   escape hatch, leaderboard, and resume.
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
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
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
    await page.fill("#codein", "testteam1");
    await page.press("#codein", "Enter");           // Enter on the code field
    await page.waitForSelector("#s-quest.on");
    if ((await page.locator(".part.sealed").count()) !== 3)
      throw new Error("expected 3 sealed parts, got " + await page.locator(".part.sealed").count());
    if (!(await page.locator("#progresstext").textContent()).includes("0/4"))
      throw new Error("progress not 0/4");
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
    console.log("join ok: no brief, no pills, 1 open, 3 sealed, 0/4");

    // typewriter: text starts partial on first view, then completes
    const full = "FIXTURE: Count the imaginary lampposts on Example Street. Any whole number is accepted (collect mode).";
    const early = await page.locator('.part[data-idx="1"] .ptext').textContent();
    if (early.length >= full.length)
      throw new Error("typewriter did not stagger the first view");
    await page.waitForFunction((f) =>
      document.querySelector('.part[data-idx="1"] .ptext').textContent === f,
      full, { timeout: 25000 });
    console.log("reveal ok: clue text typed out, then completed");

    // hint: gated at first, then available, then shown and logged
    const hb = page.locator('.part[data-idx="1"] .hintbtn');
    if (!(await hb.count())) throw new Error("hint button missing on part 1");
    // the countdown must use the server's hint_wait_s (25s here), not a hard-coded 5 min
    // must be counting down to the SERVER's wait (25s), not a hard-coded 5 min
    if (!/^Hint in 0:[0-2]\d$/.test((await hb.textContent()).trim()))
      throw new Error("hint countdown should track the server wait, got: " + await hb.textContent());
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
      const h = document.querySelector('.part[data-idx="1"] .hinttext');
      return h && !h.hidden && h.textContent.includes("FIXTURE HINT");
    }, { timeout: 20000 });
    console.log("hint ok: countdown disabled -> released after the server wait -> shown");

    // a hint survives a reload: the text is not in the state payload, so the
    // button must re-fetch the hint the team already paid for
    await page.reload();
    await page.waitForSelector("#s-quest.on");
    const hb2 = page.locator('.part[data-idx="1"] .hintbtn');
    if (!(await hb2.textContent()).includes("Show the hint you took"))
      throw new Error("after reload the taken hint should be recoverable, got: "
                      + await hb2.textContent());
    await hb2.click();
    await page.waitForFunction(() => {
      const h = document.querySelector('.part[data-idx="1"] .hinttext');
      return h && !h.hidden && h.textContent.includes("FIXTURE HINT");
    }, { timeout: 20000 });
    console.log("hint ok: recovered after reload without a second charge");

    // ambiguity guard: two numbers must be refused, not concatenated
    await box(1).fill("20-22");
    await send(1).click();
    await page.waitForFunction(() =>
      document.getElementById("toast").textContent.includes("one whole number"));
    await pause();
    // collect mode: any single whole number accepted, echoed normalized
    await box(1).fill("17 lampposts");
    await send(1).click();
    await page.waitForSelector('.part.done[data-idx="1"]');
    const a1 = (await page.locator('.part.done[data-idx="1"] .answer').textContent()).trim();
    if (a1 !== "17") throw new Error("collect answer not normalized to 17: " + a1);
    await page.waitForSelector('.part.open[data-idx="2"]');
    if (await page.locator('.part[data-idx="2"] .pill').count())
      throw new Error("newly opened part must not carry a type pill either");
    console.log("ok: '20-22' refused as ambiguous, '17 lampposts' -> 17, no pill on part 2");

    // compete-mode number: wrong costs a strike, right advances
    await box(2).fill("41");
    await send(2).click();
    await page.waitForFunction(() =>
      document.getElementById("strikeline").textContent.includes("1/2"));
    await pause();
    await box(2).fill("42");
    await send(2).click();
    await page.waitForSelector('.part.done[data-idx="2"]');
    console.log("compete ok: 41 struck (1/2), 42 accepted");

    // text variant accepted after a wrong name
    await page.waitForSelector('.part.open[data-idx="3"]');
    await box(3).fill("dragon");
    await send(3).click();
    await page.waitForFunction(() =>
      document.getElementById("strikeline").textContent.includes("2/2"));
    await pause();
    await box(3).fill("gryphon!!");
    await send(3).click();
    await page.waitForSelector('.part.done[data-idx="3"]');
    console.log("text ok: dragon struck, gryphon variant accepted");

    // the escape hatch: a clue nobody can answer must not end the run
    await page.waitForSelector('.part.open[data-idx="4"]');
    await page.locator('.part[data-idx="4"] .skipbtn').click();
    await page.waitForSelector("#modal.show");
    await page.click("#skyes");
    await page.waitForSelector('.part.skipped[data-idx="4"]');
    console.log("skip ok: part 4 skipped, run continues");

    // finishing (3 solved + 1 skipped) opens the win card mentioning the skip
    await page.waitForSelector("#modal.show");
    const card = await page.locator("#modalcard").textContent();
    if (!card.includes("given up its numbers")) throw new Error("win modal wrong");
    if (!card.includes("1 left behind")) throw new Error("win card should note the skip");
    await page.click("#mboard");
    await page.waitForFunction(() =>
      document.getElementById("modalcard").textContent.includes("Parts cracked"));
    const lb = await page.locator("#modalcard").textContent();
    if (!lb.includes("hint")) throw new Error("leaderboard should note the hint: " + lb.slice(0,140));
    if (!lb.includes("3/4") || !lb.includes("skipped"))
      throw new Error("leaderboard should read 3/4 with a skip: " + lb.slice(0, 140));
    await page.click("#mclose");
    console.log("board ok: 3/4 with 1 skipped");

    // reload resumes, and seen clues do NOT re-animate
    await page.reload();
    await page.waitForSelector("#s-quest.on", { timeout: 5000 });
    await page.waitForFunction(() =>
      document.querySelectorAll(".part.done").length === 3 &&
      document.querySelectorAll(".part.skipped").length === 1);
    console.log("resume ok: 3 done + 1 skipped after reload");

    if (errors.length) throw new Error("page errors: " + errors.join(" | "));
    console.log("QUEST SMOKE TEST PASS");
  } finally {
    await browser.close();
    server.kill();
  }
})().catch((e) => { console.error("QUEST SMOKE TEST FAIL:", e.message); process.exit(1); });
