/* End-to-end smoke test of the Fedora app against the local mock backend.
   Harness ported from TRIVIUM's app_smoke_test.cjs (mock spawn, pinned
   chromium, pageerror capture, phone viewport); assertions are Fedora's:
   join -> two open clues -> solve one (fixed-letter skip on the crossing) ->
   wrong answer flash -> cooldown -> unlock cascade -> leaderboard -> resume.

   Run: NODE_PATH=/opt/node22/lib/node_modules node pipeline/smoke_test.cjs
   (local/sandbox only — CI runs the python contract test; browser deps are
   not installed on the CI runner)
*/
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const path = require("path");

const PORT = 8793;
const BASE = `http://localhost:${PORT}`;

(async () => {
  const server = spawn("python3", [path.join(__dirname, "mock_backend.py"), String(PORT)],
                       { env: { ...process.env, MOCK_COOLDOWN_S: "3" } });
  await new Promise((r) => setTimeout(r, 900));

  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium", args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));

  const toast = () => page.locator("#toast").textContent();

  try {
    // -- 1. join screen; bad code rejected with a message
    await page.goto(BASE + "/");
    await page.waitForSelector("#s-join.on");
    if (await page.locator("#offline-banner").isVisible())
      throw new Error("offline banner shown despite mock config");
    await page.fill("#codein", "WRONGCODE");
    await page.click("#joinbtn");
    await page.waitForFunction(() => document.getElementById("joinerr").textContent.length > 0);
    console.log("join ok: bad code rejected");

    // -- 2. good code -> game screen, 2 open cards, 5 locked, meta card
    await page.fill("#codein", "testteam1");
    await page.click("#joinbtn");
    await page.waitForSelector("#s-game.on");
    const nOpen = await page.locator(".cluecard.open").count();
    const nLocked = await page.locator(".cluecard.locked").count();
    if (nOpen !== 2 || nLocked !== 5)
      throw new Error(`expected 2 open + 5 locked, got ${nOpen}+${nLocked}`);
    if (!(await page.locator(".metacard").count())) throw new Error("meta card missing");
    if ((await page.locator(".cell.meta").count()) !== 3)
      throw new Error("expected 3 meta cells in example grid");
    // locked words with no solved crossing render dim
    if (!(await page.locator(".cell.dim").count())) throw new Error("no dim locked cells");
    console.log("game ok: 2 open, 5 locked, meta present");

    // -- 3. select clue 1 (CRIMSON), keyboard appears, type + submit
    await page.locator('.cluecard.open[data-idx="1"]').click();
    await page.waitForSelector("#kb.show");
    for (const ch of "CRIMSO") await page.keyboard.press(ch);
    await page.click("#submitbtn");   // incomplete
    await page.waitForFunction(() =>
      document.getElementById("toast").textContent.includes("whole word"));
    await page.keyboard.press("N");
    await page.keyboard.press("Enter");
    await page.waitForFunction(() =>
      document.querySelector('.cluecard.done[data-idx="1"]') !== null);
    if (!(await page.locator('.cluecard.open[data-idx="3"]').count()))
      throw new Error("solving 1 did not unlock 3");
    console.log("solve ok: clue 1 done, clue 3 unlocked");

    // -- 4. fixed-letter skip: clue 3 (MARBLE) crosses solved CRIMSON at its R
    await page.locator('.cluecard.open[data-idx="3"]').click();
    for (const ch of "MABLE") await page.keyboard.press(ch);   // R comes from the crossing
    const w = await page.evaluate(() => assembled(3));
    if (w !== "MARBLE") throw new Error(`fixed-letter skip broken: assembled ${w}`);
    await page.keyboard.press("Enter");
    await page.waitForFunction(() =>
      document.querySelector('.cluecard.done[data-idx="3"]') !== null);
    console.log("crossing ok: fixed R skipped, MARBLE accepted");

    // -- 5. wrong answer flashes the word; instant retry hits the cooldown
    await page.locator('.cluecard.open[data-idx="2"]').click();
    for (const ch of "AAAAAAA") await page.keyboard.press(ch);
    await page.keyboard.press("Enter");
    await page.waitForFunction(() => document.querySelectorAll(".cell.badword").length >= 7);
    await page.keyboard.press("Enter");
    await page.waitForFunction(() =>
      document.getElementById("toast").textContent.includes("Steady"));
    console.log("verdicts ok: wrong flashes red, cooldown enforced");

    // -- 6. leaderboard modal
    await page.click("#lbbtn");
    await page.waitForSelector("#modal.show");
    const card = await page.locator("#modalcard").textContent();
    if (!card.includes("Test Team") || !card.includes("2/7"))
      throw new Error("leaderboard missing us at 2/7: " + card.slice(0, 120));
    if (!card.includes("Rival Team")) throw new Error("rival missing from board");
    await page.click("#mclose");
    console.log("leaderboard ok: 2/7 with rival visible");

    // -- 7. reload resumes straight into the game with server state intact
    await page.reload();
    await page.waitForSelector("#s-game.on", { timeout: 5000 });
    await page.waitForFunction(() =>
      document.querySelectorAll(".cluecard.done").length === 2);
    const fixed = await page.locator(".cell.fixed").count();
    if (fixed < 12) throw new Error(`expected >=12 fixed cells after resume, got ${fixed}`);
    console.log("resume ok: reload keeps 2 solved words as fixed letters");

    if (errors.length) throw new Error("page errors: " + errors.join(" | "));
    console.log("FEDORA SMOKE TEST PASS");
  } finally {
    await browser.close();
    server.kill();
  }
})().catch((e) => { console.error("FEDORA SMOKE TEST FAIL:", e.message); process.exit(1); });
