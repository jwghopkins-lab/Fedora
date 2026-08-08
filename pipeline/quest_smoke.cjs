/* End-to-end smoke test of the QUEST app (quest.html) against the mock backend.
   Covers: join, kind pills, typewriter reveal (first view only), collect-mode
   number, the two-numbers ambiguity guard, compete-mode strike, text variants,
   the skip escape hatch, leaderboard, and resume.
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
    { env: { ...process.env, MOCK_COOLDOWN_S: "0.3" } });
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
    await page.fill("#codein", "testteam1");
    await page.press("#codein", "Enter");           // Enter on the code field
    await page.waitForSelector("#s-quest.on");
    if (!(await page.locator(".part.intro").count())) throw new Error("intro card missing");
    if ((await page.locator(".part.sealed").count()) !== 3)
      throw new Error("expected 3 sealed parts, got " + await page.locator(".part.sealed").count());
    if (!(await page.locator("#progresstext").textContent()).includes("0/4"))
      throw new Error("progress not 0/4");
    // the three-type key is explained up front
    for (const k of ["WITS", "THE DIG", "GROUND TRUTH"])
      if (!(await page.locator(".kindkey").textContent()).includes(k))
        throw new Error("intro key missing " + k);
    console.log("join ok: intro + type key, 1 open, 3 sealed, 0/4");

    // pill reflects the clue's kind
    const pill1 = (await page.locator('.part[data-idx="1"] .pill').textContent()).trim();
    if (pill1 !== "WITS") throw new Error("part 1 pill should be WITS, got " + pill1);

    // typewriter: text starts partial on first view, then completes
    const full = "FIXTURE: Count the imaginary lampposts on Example Street. Any whole number is accepted (collect mode).";
    const early = await page.locator('.part[data-idx="1"] .ptext').textContent();
    if (early.length >= full.length)
      throw new Error("typewriter did not stagger the first view");
    await page.waitForFunction((f) =>
      document.querySelector('.part[data-idx="1"] .ptext').textContent === f,
      full, { timeout: 6000 });
    console.log("reveal ok: WITS pill, text typed out then completed");

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
    const pill2 = (await page.locator('.part[data-idx="2"] .pill').textContent()).trim();
    if (pill2 !== "THE DIG") throw new Error("part 2 pill should be THE DIG, got " + pill2);
    console.log("ok: '20-22' refused as ambiguous, '17 lampposts' -> 17, DIG pill next");

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
