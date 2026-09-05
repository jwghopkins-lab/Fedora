# The Architect Order — handoff 2: the visual match, the Progress button, haptics

Builds on handoff 1 (`ARCHITECT_ORDER_HANDOFF_1.md`, formerly
`ARCHITECT_ORDER_HANDOFF.md`). Read that first. Nothing here changes it; this
adds three things that work together:

1. **A live match score** on stencil lenses: how well the shape under the
   stencil matches it, shown on screen at all times.
2. **A Progress button** that sits grey until the match passes, then lights
   up. The player taps it to go on.
3. **A haptic tick** on that tap, and on every other success the player causes
   with a tap.

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
      "match": {"threshold": 0.35, "hold_ms": 600, "gate": true, "fallback_s": null}
    }

- `auto` (default true when `match` is present): the lens opens by itself the
  moment the stop's location gate passes, instead of waiting for the Lens
  button. With no gate, it opens when the body reveal finishes.
- `match.threshold`: the score that counts as matched, 0 to 1. **Default
  0.35.** Chosen before any testing; the log below is how it gets corrected.
- `match.hold_ms`: the score must stay at or above the threshold for this
  long. Default 600.
- `match.gate`: when true, the Progress button stays grey until the match
  passes. When false, Progress is available from the start but still turns
  green on a match, so the owner can see when it *would* have gated. Default
  true; the fixture's calibration stop sets it false.
- `match.fallback_s`: with `gate` true and a number here, Progress lights up
  anyway after that many seconds of trying. Null means never. Leave null; the
  owner sets it once thresholds are known.

Validation: `match` only on `kind: "stencil"`; threshold in (0, 1]; hold_ms
≥ 0; fallback_s null or ≥ 10.

## The score

Every 250 ms while a `match` lens is open:

1. Draw the current video frame to an offscreen canvas at working resolution,
   longest side 320 px.
2. Grayscale, 3×3 box blur, 3×3 Sobel. Keep gradient magnitude as a float 0–1
   per pixel, normalised by the frame's 99th-percentile magnitude so the score
   does not swing with exposure. Call this **E**.
3. Render the stencil, under the player's current translate / scale / rotate,
   onto a second offscreen canvas of the same working size. Its alpha channel,
   thresholded at 128 and dilated by 2 px, is the mask **M**. Dilate M again by
   6 px and subtract M to get the **ring R** around the stencil.
4. `on` = mean of E over M. `off` = mean of E over R.
   **score = max(0, (on − off) / (on + off + 0.001))**.
   Zero: edges are no more likely under the stencil than beside it. One: every
   edge in the neighbourhood is under the stencil.
5. Repeat step 4 with the transform shifted by −4, 0, +4 px in x and y and
   scaled by 0.96, 1.00, 1.04, twenty-seven evaluations, and keep the best.
   This forgives an imperfect hand alignment.
6. Smooth the best score with an exponential moving average, alpha 0.3. That
   is the number shown and the number tested.

**Matched** = the smoothed score has been ≥ `threshold` continuously for
`hold_ms`. Matched is a state, not an event: if the score falls away again
before the player taps Progress, the button goes back to grey. Keep each
evaluation under about 10 ms on a mid-range phone; if not, drop to 240 px.

## The Progress button, and what the screen shows

While a `match` lens is open, a panel at the bottom that never hides:

- A horizontal bar for the smoothed score, 0 to 1, with a tick at the
  threshold. The bar turns green above the threshold.
- The numbers, small and monospaced: `score 0.41 · on 0.63 · off 0.22`.
- **Progress.** Grey and disabled while `gate` is true and not matched. Lit
  and enabled when matched, or when `gate` is false, or when `fallback_s` has
  run out. Green when matched in every case. Tapping it: **haptic tick**, the
  lens closes, the stop continues to its `after` blocks. With `gate` true, a
  small counter beside it shows seconds tried.
- A **Log** button. Each press appends one line to a per-hunt log in
  localStorage: stop id, ISO time, score, on, off, the transform (x, y, scale,
  rotation), matched yes/no, and the current GPS accuracy if known. A **Copy
  log** action in the menu puts the whole log on the clipboard as plain text.
  This is how the owner collects calibration samples on site.

The bar, numbers and Progress are not a testing-mode feature. They are always
on for any lens with a `match`, because calibrating in the field is the point.

## Haptics

One function, `haptic()`, in the player. Silently does nothing where
unsupported. No library.

- **Android:** `navigator.vibrate(15)`.
- **iPhone, iOS 17.4 and later:** Safari has no vibration API. Keep one
  `<input type="checkbox" switch>` in the DOM, visually hidden but **not**
  `display: none` (position it off-screen). Flipping it programmatically fires
  the system's light haptic tick. Flip it once per call.
- **Both:** the call must happen synchronously inside the tap handler. Never
  after an `await`, a timer, or a geolocation callback; on iPhone those fire
  nothing.

**The rule that follows:** anything that succeeds asynchronously does not
tick itself. It lights a button, and the tap on that button ticks. So:

| Event | How it arrives | Haptic |
|---|---|---|
| Correct answer | Synchronous, in the submit tap | `haptic()` in the submit handler, immediately on a correct check |
| Location gate passes | Async, after the fix window | "You're here." plus a lit **Continue** button; `haptic()` on its tap |
| Match passes | Async, on a timer | Progress lights; `haptic()` on its tap |
| Wrong answer | Synchronous | No haptic. The shake is enough |

The location gate's Continue button is new: today the gate flows straight
into the next part. Add the button so the tick has a tap to live on. It is
enabled only once the gate has passed; it is not a skip.

## The placeholder stencil

Generate `app/img/placeholder-stencil.png`: transparent background, a black
3 px outline of a landscape rectangle with a smaller rectangle inside it, about
600 × 400 px. It roughly matches a doorway, a window or a notice board, so the
owner can test on almost any wall before real stencils exist.

Document in the README how a real one is supplied: a PNG with a transparent
background and dark lines 2–4 px wide at roughly 600–800 px on the long side,
drawn from a head-on photo of the target at the framing a phone gets from
three to five metres. Big distinctive edges only: the outline and two or three
strong internal lines. A stencil that traces every engraved letter fails in
glare; one that is only a rectangle matches anything.

## Fixture

Add a sixth stop to `content/fixture.json`: a location gate with compass off,
radius 40 m, then a stencil lens with `auto: true` and
`match: {threshold: 0.35, hold_ms: 600, gate: false, fallback_s: null}`, using
the placeholder stencil. The text says plainly it is a calibration stop.

Also add a seventh, identical but with `gate: true` and `fallback_s: 45`, so
the gated behaviour and the fallback can be seen without editing content.

## Working method

As before: `main`, small commits, push, no pull requests. When it is live, tell
the owner in two lines what to do on the phone: open stop six, pass the gate
with the simulator, point the camera at a doorway, line the rectangle up, watch
the bar, press Log at good and bad alignments, tap Progress and feel the tick,
then Copy log and paste it back.

## Acceptance

1. Passing the gate on stop six opens the camera with the stencil, unprompted.
2. The bar and numbers update several times a second and hold steady when the
   phone is still.
3. Lining the rectangle up on a real doorway raises the score visibly; a blank
   wall drops it near zero; a slightly-off alignment still scores because of
   the search in step 5.
4. On stop six, Progress is available at once and turns green on a match. On
   stop seven it is grey until the bar has been green for 600 ms, goes grey
   again if the match is lost, and lights by itself after 45 s.
5. Tapping Progress ticks on an iPhone running iOS 17.4 or later and on
   Android, and does nothing harmful elsewhere.
6. A correct answer ticks immediately on submit. Passing a location gate shows
   a Continue button whose tap ticks. Wrong answers do not tick.
7. Log appends a line per press; Copy log yields plain text with every field.
8. Everything in handoff 1 still works.
