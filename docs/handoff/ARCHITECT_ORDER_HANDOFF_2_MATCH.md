# The Architect Order — handoff 2: the visual match

Builds on handoff 1 (`ARCHITECT_ORDER_HANDOFF.md`). Read that first if you have
not. Nothing here changes it; this adds one feature to the lens.

## What you are adding

A stop can now say: after the location gate passes, open the camera with a
stencil, and **score, live, how well the shape under the stencil matches it.**
The score is shown on screen at all times so the owner can calibrate on site.
Whether the score also gates progress is a per-stop switch, off by default.

The owner will supply real stencils later. Build with a placeholder and make it
obvious how to swap one in.

**No library. No download. Plain JavaScript on a canvas. The player lines the
stencil up by hand; the code only checks the alignment.**

## Content

`lens` gains an optional `match` block, and stencil lenses gain `auto`:

    "lens": {
      "kind": "stencil",
      "src": "img/placeholder-stencil.png",
      "note": "Line the outline up with the plaque.",
      "auto": true,
      "match": {"threshold": 0.35, "hold_ms": 600, "gate": false, "fallback_s": null}
    }

- `auto` (default true when `match` is present): the lens opens by itself the
  moment the stop's location gate passes, instead of waiting for the Lens
  button. If the stop has no gate, it opens when the body reveal finishes.
- `match.threshold`: the score that counts as matched, 0 to 1.
- `match.hold_ms`: the score must stay at or above the threshold for this long.
- `match.gate`: when true, the stop's `after` blocks and **Next** are held until
  the match passes. When false, a **Continue** button is always available
  under the meter, and the score is purely informational. **Default false.**
  This is calibration mode and it is the mode the owner will use first.
- `match.fallback_s`: when `gate` is true and this is a number, after that many
  seconds of trying, Continue appears anyway. Null means never. Leave null;
  the owner will set it once thresholds are known.

Validation: `match` only on `kind: "stencil"`; threshold in (0, 1]; hold_ms
≥ 0; fallback_s null or ≥ 10.

## The score

Every 250 ms while the lens is open and a `match` exists:

1. Draw the current video frame to an offscreen canvas at working resolution,
   longest side 320 px.
2. Grayscale, 3×3 box blur, 3×3 Sobel. Keep gradient magnitude as a float
   0–1 per pixel, normalised by the frame's 99th-percentile magnitude so the
   score does not swing with exposure. Call this **E**.
3. Render the stencil, under the player's current translate / scale / rotate,
   onto a second offscreen canvas of the same working size. Its alpha channel,
   thresholded at 128 and dilated by 2 px, is the mask **M**. Dilate M again by
   6 px and subtract M from it to get the **ring R** around the stencil.
4. `on` = mean of E over M. `off` = mean of E over R.
   **score = max(0, (on − off) / (on + off + 0.001))**.
   Zero means edges are no more likely under the stencil than beside it. One
   means every edge in the neighbourhood is under the stencil.
5. Repeat step 4 for the transform shifted by −4, 0, +4 px in x and y and
   scaled by 0.96, 1.00, 1.04 (27 evaluations, all cheap at 320 px), and take
   the best. This forgives an imperfect hand alignment.
6. Smooth the best score with an exponential moving average, alpha 0.3. That
   is the number shown and the number tested.

Pass when the smoothed score has been ≥ `threshold` continuously for
`hold_ms`. On pass: a clear "Matched" state, a short vibration where
supported, and the lens closes to the stop's `after` blocks, or stays open with
a Done button if `gate` is false and the player prefers to keep looking.

Keep the whole thing under about 10 ms per evaluation on a mid-range phone.
If it is slower, drop the working resolution to 240 px before anything else.

## What the screen shows

While a `match` lens is open, a panel at the bottom that never hides:

- A horizontal bar for the smoothed score, 0 to 1, with a tick at the
  threshold. The bar turns green above the threshold.
- The numbers, small and monospaced: `score 0.41 · on 0.63 · off 0.22`.
- A **Log** button. Each press appends one line to a per-hunt log in
  localStorage: stop id, ISO time, score, on, off, the transform (x, y, scale,
  rotation), and the current GPS accuracy if known. A **Copy log** action in
  the menu puts the whole log on the clipboard as plain text lines. This is how
  the owner will collect calibration samples on site and send them back.
- When `gate` is false: a **Continue** button.
- When `gate` is true: no Continue until matched, or until `fallback_s` runs
  out if set. A small counter shows seconds tried.

The bar and numbers are not a testing-mode feature. They are always on for any
lens with a `match`, because calibrating in the field is the point.

## The placeholder stencil

Generate `app/img/placeholder-stencil.png`: transparent background, a black
3 px outline of a landscape rectangle with a smaller rectangle inside it, about
600 × 400 px. It will roughly match a doorway, a window or a notice board, so
the owner can test the meter on almost any wall before real stencils exist.

Document in the README how a real one is supplied: a PNG with a transparent
background and dark lines 2–4 px wide at roughly 600–800 px on the long side,
drawn from a head-on photo of the target at the framing a phone gets from
three to five metres. Big distinctive edges only: the outline and two or three
strong internal lines. A stencil that traces every engraved letter will fail in
glare; one that is just a rectangle will match anything.

## Fixture

Add a sixth stop to `content/fixture.json`: a location gate with compass off,
radius 40 m, then a stencil lens with `auto: true` and
`match: {threshold: 0.35, hold_ms: 600, gate: false, fallback_s: null}`, using
the placeholder stencil. Text says plainly that it is a calibration stop.

## Working method

As before: `main`, small commits, push, no pull requests. When it is live, tell
the owner in two lines what to do on the phone: open the sixth stop, pass the
gate with the simulator, point the camera at a doorway, line the rectangle up,
watch the score, press Log a few times at good and bad alignments, then Copy
log and paste it back.

## Acceptance

1. Passing the gate on stop six opens the camera with the stencil, unprompted.
2. The score bar and numbers update several times a second and are stable when
   the phone is still.
3. Lining the rectangle up on a real doorway raises the score visibly; pointing
   at a blank wall drops it near zero; a slightly-off alignment still scores
   reasonably because of the search in step 5.
4. Log appends a line each press; Copy log yields plain text with every field.
5. With `gate` false, Continue is always available. Flipping `gate` to true in
   the content and rebuilding holds Next until the bar has been green for
   `hold_ms`; setting `fallback_s: 30` produces a Continue after 30 s of
   trying.
6. Everything in handoff 1 still works.
