/* End-to-end smoke test of the QUEST app (quest.html) against the mock backend
   loaded with the QA fixture. Flow: join -> intro + part 1 open, rest sealed ->
   collect-mode number accepted -> compete number wrong then right (strike) ->
   text answer wrong then variant right (strike, hits limit boundary) ->
   win modal -> leaderboard -> reload resumes.
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
  const answerBox = (idx) => page.locator(`.part[data-idx="${idx}"] input`);
  const submitBtn = (idx) => page.locator(`.part[data-idx="${idx}"] button`);
  const pause = () => page.waitForTimeout(400);

  try {
    await page.goto(BASE + "/quest.html");
    await page.waitForSelector("#s-join.on");
    await page.fill("#codein", "testteam1");
    await page.click("#joinbtn");
    await page.waitForSelector("#s-quest.on");
    if (!(await page.locator(".part.intro").count())) throw new Error("intro card missing");
    if (!(await page.locator('.part.open[data-idx="1"]').count()))
      throw new Error("part 1 not open");
    if ((await page.locator(".part.sealed").count()) !== 2)
      throw new Error("parts 2+3 should be sealed");
    if (!(await page.locator("#progresstext").textContent()).includes("0/3"))
      throw new Error("progress not 0/3");
    console.log("join ok: intro + part 1 open, 2 sealed");

    // part 1: collect mode — any whole number accepted, echoed back
    await answerBox(1).fill("17 lampposts");
    await submitBtn(1).click();
    await page.waitForSelector('.part.done[data-idx="1"]');
    const a1 = await page.locator('.part.done[data-idx="1"] .answer').textContent();
    if (a1.trim() !== "17") throw new Error("collect answer not normalized to 17: " + a1);
    await page.waitForSelector('.part.open[data-idx="2"]');
    console.log("collect ok: '17 lampposts' -> 17, part 2 revealed");

    // part 2: compete number — wrong then right
    await answerBox(2).fill("41");
    await submitBtn(2).click();
    await page.waitForFunction(() =>
      document.getElementById("strikeline").textContent.includes("1/2"));
    await pause();
    await answerBox(2).fill("42");
    await submitBtn(2).click();
    await page.waitForSelector('.part.done[data-idx="2"]');
    console.log("compete ok: 41 struck (1/2), 42 accepted");

    // part 3: text — wrong name strikes to the limit boundary, variant accepted
    await page.waitForSelector('.part.open[data-idx="3"]');
    await answerBox(3).fill("dragon");
    await submitBtn(3).click();
    await page.waitForFunction(() =>
      document.getElementById("strikeline").textContent.includes("2/2"));
    await pause();
    await answerBox(3).fill("gryphon!!");
    await submitBtn(3).click();
    await page.waitForSelector("#modal.show");
    const card = await page.locator("#modalcard").textContent();
    if (!card.includes("given up its numbers")) throw new Error("win modal wrong: " + card.slice(0, 80));
    console.log("text ok: dragon struck (2/2 still in), gryphon variant wins");

    // leaderboard from the win modal
    await page.click("#mboard");
    await page.waitForFunction(() =>
      document.getElementById("modalcard").textContent.includes("Parts cracked"));
    const lb = await page.locator("#modalcard").textContent();
    if (!lb.includes("3/3") || !lb.includes("Rival Team"))
      throw new Error("leaderboard missing 3/3 or rival: " + lb.slice(0, 120));
    await page.click("#mclose");
    console.log("board ok: 3/3 with rival listed");

    // reload resumes into completed state
    await page.reload();
    await page.waitForSelector("#s-quest.on", { timeout: 5000 });
    await page.waitForFunction(() =>
      document.querySelectorAll(".part.done").length === 3);
    console.log("resume ok: reload shows 3 done parts");

    if (errors.length) throw new Error("page errors: " + errors.join(" | "));
    console.log("QUEST SMOKE TEST PASS");
  } finally {
    await browser.close();
    server.kill();
  }
})().catch((e) => { console.error("QUEST SMOKE TEST FAIL:", e.message); process.exit(1); });
