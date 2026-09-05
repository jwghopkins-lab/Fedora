# The Architect Order — build handoff, v1

You are starting a new repository, `jwghopkins-lab/architect-order`. This
document is the whole brief. Read it to the end before touching anything.

## What you are building

A real-world walking puzzle game played on a phone alongside a physical notebook
the players carry (the "diary"). A static web page on GitHub Pages, no backend.
The page walks a team through a fixed sequence of stops. At a stop it shows text
and pictures; it may require the phone to be physically at a place before going
on; it may ask a question with a small number of guesses; and it may open the
phone's camera with a picture laid over the live view (a stencil, a knotted
cord, an arrow) that the player lines up against something real.

The story, the real places and the real questions are not part of this brief.
The owner adds them later. You build the engine, and a fixture hunt of fake
stops that exercises every feature.

## What you are not building

- No database, no Supabase, no server. Everything is in the page.
- No logins, no teams. A team is a phone. Progress lives in localStorage.
- No timed hints.
- No directions engine, map data, routing, or writing-style checker.
- No computer vision. The camera overlay is positioned by hand.
- No pass or skip button on location gates.
- No plot content.
- No frameworks, no npm, no bundler, no external scripts or fonts. Plain HTML,
  CSS and JavaScript, plus one Python build script with no dependencies.

## Sources — clone both, read-only

Both are public. Clone them beside your working directory and read them before
writing anything:

    git clone --depth 1 https://github.com/jwghopkins-lab/london-noticing
    git clone --depth 1 https://github.com/jwghopkins-lab/Fedora

**Primary source: `london-noticing/app/index.html`**, a single-file player of
about 1,250 lines. Most of this game is already in it. Take:

- the page shell, the CSS variables and the card layout;
- the word-by-word text reveal: `typeInto`, `TYPE_SLOWDOWN = 2.6`, tap to
  finish;
- the location code exactly as tuned: `haversineM`, `gatePasses` with
  `ACC_ALLOWANCE_M = 15` and `ACC_USELESS_M = 75`, `getFix` (best fix over a
  window via `watchPosition`, `maximumAge: 0`, `enableHighAccuracy`),
  `locationPreflight`, and the pass rule
  `distance − min(accuracy, 15) ≤ radius`. Keep the comments: they record why
  each constant is what it is;
- the answer matcher: `normalise`, `withinOneEdit`, `oneSwapApart`,
  `matchesUnder`, `answerAccepted`, with its comment about never stripping a
  word that could itself be an answer;
- the localStorage state pattern and the **Start over** button with its confirm
  (`#restartbtn`);
- the development position simulator behind `#testing` / `?testing=1`, and the
  rule that it must be visibly a dev tool and must not weaken the real pass
  rule;
- the `.stop.wrong` shake and the toast.

Leave behind: the topic picker and route combinations, `topics.json`, the "not
sure, tell me" reveal, the gate pass/skip button, anything about directions,
headings or distances between stops, and the whole `pipeline/` except as a
reference for how JSON is baked into the page (`build_tour.py` around lines
1600–1625: the `MARKER` replacement that writes `window.NOTICING_BUNDLE`).

**Secondary source: `Fedora/app/quest.html`**, the same player's older sibling
with a backend. Take only the idea of the guesses meter (`paintLives`,
`#lives`, `livesText`) for the per-question guess counter. Leave everything
else: RPC calls, polling, hints, login, leaderboard.

**Deploy pattern: `Fedora/.github/workflows/pages.yml`** — checkout, build,
`upload-pages-artifact`, `deploy-pages`, then curl the deployed URL. Copy it and
replace the build step with ours.

## Repository layout

    content/fixture.json        the fixture hunt (fake stops, committed)
    content/<hunt>.json         real hunts, added later by the owner (also committed:
                                this is a friends-only test, and the physical diary
                                is the secret, not the answer list)
    app/player.html             the player template, with one marker line where
                                the hunt JSON goes
    app/lens.js                 the camera overlay, a separate file so the player
                                stays readable
    app/img/                    images referenced by content, relative paths
    pipeline/build.py           validate the content, bake it into the page
    site/                       build output, gitignored
    .github/workflows/pages.yml
    README.md                   short: what it is, how to build, how to test

## Content format

Top level:

    {
      "id": "fixture",
      "title": "…",
      "intro": [blocks],
      "outro": [blocks],
      "diary_mm": {"w": 148, "h": 210},
      "stops": [ … ]
    }

`diary_mm` is the physical notebook's size, used by the lens scale bar. A5 by
default; the owner will confirm.

A **block** is one of:

    {"type": "text",  "text": "…"}                       paragraphs split on blank
                                                         lines, revealed word by word
    {"type": "image", "src": "img/x.jpg", "alt": "…", "caption": "…"}
                                                         full width, shown at once

Blocks render in order, so an image can sit between paragraphs.

A **stop**:

    {
      "id": "unique-slug",
      "chapter": "Label shown above the title",
      "title": "…",
      "body": [blocks],
      "gate": {"lat": 0, "lon": 0, "radius_m": 40, "prompt": "…"}   or null,
      "compass": true,
      "question": {"ask": "…", "answers": ["…", "…"], "guesses": 3}  or null,
      "after": [blocks],
      "lens": one of
              {"kind": "stencil", "src": "img/s.png", "note": "…"}
              {"kind": "cord", "marks_mm": [0, 300, 600, 914], "note": "…"}
              {"kind": "arrow", "note": "…"}
              or null
    }

`body` shows on arrival. `after` shows once the question resolves; if there is
no question, once the gate passes; if neither, straight away.

Validation in `build.py`, failing loudly with the stop id: ids unique; every
image `src` exists under `app/`; a question has at least one answer and
`guesses ≥ 1` (default 3); a gate has all four fields and `radius_m ≥ 20`;
`compass` only with a gate; lens kinds known; `chapter`, `title` and `body`
present.

## Player behaviour

Sequence: intro → stops in order → outro. One stop open at a time; earlier
stops collapse to a line showing their result. State is per phone.

A stop card, top to bottom, each part appearing only when the one before is
done:

1. Chapter label, title.
2. Body blocks: text revealed word by word, images at once. Tap to finish the
   reveal.
3. **If gated:** the gate prompt and a **Check location** button. No skip.
   While checking, "Finding you…" for the fix window. Then pass → "You're
   here." and on to 4; or fail → the distance if the fix is usable ("About 140
   metres away"), otherwise "No usable fix. Step into the open and try again."
   The button re-arms.

   **Compass.** While the gate card is open, the fix is usable (accuracy
   ≤ 75 m) and the phone is more than 500 m from the target, show the nearest
   of eight compass points from the phone to the target: N, NE, E, SE, S, SW,
   W, NW, with sector = round(bearing / 45) mod 8. Update it from
   `watchPosition` while the card is open; stop watching when it closes. Under
   500 m show nothing at all: not "close", nothing. Known and accepted: a
   player who watches where the reading flips can triangulate the target. That
   is fine for this build.
4. **If a question:** the ask, an input, and a guesses-left meter starting at
   `guesses`. Wrong → shake, decrement. Right → "Yes." At zero → "Marked
   wrong. The answer was X." and the stop resolves as wrong. Answers are
   checked with the london-noticing matcher, unchanged.
5. After blocks.
6. **If a lens:** a **Lens** button, available once the gate has passed, or
   from the start if there is no gate. It can be reopened from a collapsed stop.
7. **Next.**

The outro shows a summary: how many right, how many wrong, and which.

A menu, top right: Start over (with confirm), and in testing mode the
simulator.

On the intro screen, preload every image in the hunt with `new Image()` so the
walk works with poor signal after that first screen.

## The lens: camera with an overlay

A full-screen view opened from a stop. Lives in `app/lens.js`. No dependencies.

- **Feed.** `getUserMedia({video: {facingMode: {ideal: "environment"}}, audio:
  false})` into a `<video autoplay playsinline muted>` filling the screen. Needs
  a secure context: Pages is one, `file://` is not, `localhost` is. If the
  camera is refused or absent, fall back to a **Choose a photo** control
  (`<input type="file" accept="image/*" capture="environment">`) and put the
  same overlay over that photo, same code path. Stop all tracks on close.
- **Overlay.** One element over the video, placed by hand: one finger drags;
  two fingers pinch to scale and rotate. Pointer events, no library. An opacity
  slider from 30% to 100%. A **Reset** button. Nothing snaps and nothing
  detects anything.
  - `stencil`: the PNG at `src` with a transparent background, starting centred
    at 60% of the shorter screen edge.
  - `cord`: an SVG line between two draggable end handles, with knots drawn at
    the `marks_mm` positions scaled proportionally between the ends. Dragging
    an end stretches the cord and the knots keep their proportions. That is all
    that is needed to compare proportions on one flat surface.
  - `arrow`: an SVG arrow, drag and rotate.
- **Scale bar, cord only.** A **Calibrate with the diary** action. The player
  holds the diary flat against the surface, taps one end of its long edge, then
  the other. The app knows the diary is `diary_mm.h` tall, so it now has
  pixels per millimetre at that plane and that distance. Until Reset, the
  cord's ends lock to real millimetres (its length is the last `marks_mm`)
  instead of free-stretching, and a small label reads "calibrated · move the
  phone and calibrate again". It only holds while the phone stays at the same
  distance from the same flat surface, and the UI says so.
- **Capture.** A button that draws the current frame and the overlay to a
  canvas and hands the result to `navigator.share({files})` where available,
  otherwise opens it in a new tab.
- **Screenshots.** Nothing in the web platform prevents them. Do not try.
- The camera cannot be tested on `file://`. Test on a phone at the Pages URL.

## Build and deploy

`python3 pipeline/build.py content/fixture.json`: validate as above; read
`app/player.html`; replace the marker line with
`<script>window.HUNT = {…};</script>`, escaping `</` as `<\/`; write
`site/index.html`; copy `app/lens.js` and `app/img/` into `site/`. Python 3
standard library only. Non-zero exit on any validation failure.

Pages workflow: on push to `main`, checkout, run the build, upload `site/`,
deploy, curl the deployed URL. The content path is one obvious variable at the
top of the workflow, so the owner can switch hunts by editing one line.

## The fixture hunt

`content/fixture.json`: five fake stops, every text clearly saying it is a
fixture, with gate coordinates in a public London park so the owner can test
gates for real, and placeholder images you generate yourself (a PNG stencil
with a transparent hole, a photo-sized JPEG, an arrow). Cover:

1. Text with an image between paragraphs; an arrow lens; no gate, no question.
2. A gate with compass on, radius 40 m; no question.
3. A question with 3 guesses and several accepted spellings, one of them a
   number written as a word.
4. A gate, a question, and a stencil lens.
5. A cord lens with `marks_mm: [0, 300, 600, 914]`, then the outro.

## Working method

- Work on `main`. Commit small, push often. No pull requests.
- First push: the skeleton and the workflow, so the Pages URL exists. Report
  that URL to the owner as soon as it is live, then build features.
- After each feature, tell the owner in one or two lines exactly what to test
  on a phone.
- Keep the player readable. Comments say why, not what. Where you keep a
  london-noticing comment, keep it word for word.
- If this brief conflicts with the code you are copying, this brief wins. If
  the brief is silent, do the simplest thing and say what you chose.

## Acceptance

On a phone, at the Pages URL, in Safari or Chrome (not an in-app browser):

1. The fixture plays start to finish; text reveals word by word; images show
   inline.
2. Start over works.
3. `#testing` shows the simulator. A simulated position inside the gate radius
   passes; outside fails with a distance; a simulated accuracy of 100 m fails
   with "no usable fix".
4. In the park, the real gate passes at the spot and fails 60 m away.
5. The compass shows a point beyond 500 m and nothing under it.
6. A question accepts every listed spelling and a one-letter typo, marks wrong
   after three misses, and shows the answer.
7. The lens opens the rear camera; stencil, cord and arrow can be moved, scaled
   and rotated; calibrate-with-diary locks the cord; capture reaches the share
   sheet; refusing the camera falls back to a photo.
