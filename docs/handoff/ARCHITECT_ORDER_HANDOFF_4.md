# The Architect Order — handoff 4: opening, first stop script, test controls

Builds on handoffs 1–3. Read them first. This one changes the opening screen,
strips the stop card down, adds a hidden reveal-skip, a test-mode threshold
slider, a pause block, and the full script for the first stop.

## 1 · Opening screen

- **No stop count anywhere.** Nothing under the title says how many stops
  there are. The progress bar is the only indication.
- The intro is two text blocks, revealed word by word like everything else:

      If you're reading this it means we have triggered a distress signal
      which sent the link that brought you here.

      As you know, we recovered Arthur's diary which holds the key to all of
      this. In case anything should happen to us, I'm digitising important
      elements of it here so you can follow. You'll need to continue your
      research to piece it together, I just hope we've got far enough that
      you can finish the job and solve it. Everything is behind real world
      location and image gates; it's our only remaining way to document our
      findings and still keep it hidden from them.

- Under it, one button: **Begin.** Tapping it calls `haptic()` and opens the
  first stop. Same tick as a correct answer.

## 2 · The stop card, stripped

- **No "Stop 1", "Stop 1 of 6", or any numbering.** A stop card shows its
  chapter header, and a title only if the content gives one. `title` is now
  optional.
- **Remove the visible "tap to see this text all at once" hint.** The
  finish-the-reveal action stays but is hidden: **three taps within 1.5
  seconds** on the revealing text finish it. One or two taps do nothing.
- **The location gate shows only:** the compass point (beyond 500 m), the
  live distance, the **Check location** button, and **Skip** in test mode.
  Remove the gate prompt line and remove the "Read once when you tap it,
  never tracked" note. `gate.prompt` becomes optional and is ignored if
  present.
- **Reveal on pass.** `reveal.at_m: 0` means "reveal when the gate passes"
  rather than at a distance. The first stop uses it.

## 3 · Test mode, one flag

Rename the hunt-level `skips` flag to **`test_mode`**. When true it turns on
every player-facing testing affordance; when false none of them exist:

- the **Skip** buttons on gates, matches and questions (as before);
- **the threshold slider** in the lens, below.

`#testing` in the URL is separate and unchanged: that is the position
simulator, a developer tool, and it stays as london-noticing built it.

## 4 · The threshold slider

In the lens panel, only when `test_mode` is true: a slider from 0.05 to
0.95 in steps of 0.01, starting at the stop's `match.threshold`, with its
value shown beside it. Moving it moves the tick on the score bar and changes
the pass test immediately. The value persists per stop in localStorage while
test mode is on, so the owner can walk about with a setting. Every **Log**
line now also records the threshold in force when it was pressed.

## 5 · Pause block

A new block type, allowed in any block list:

    {"type": "pause", "ms": 1000}

Blocks reveal in order; a pause block delays the start of the next block by
`ms`. Validation: 100 ≤ ms ≤ 5000. It renders nothing.

## 6 · The first stop, complete

Replace the first stop in `content/architect-order.json` with this. Text is
verbatim; do not edit it.

    {
      "id": "first",
      "chapter": "Location one",
      "reveal": {"at_m": 0, "chapter": "Westminster"},
      "body": [
        {"type": "text",
         "text": "Go to the place where fire burned the length of England. Then find this building."},
        {"type": "image", "src": "img/jewel-tower-sketch.png",
         "alt": "A pen sketch of a building, torn from a notebook", "caption": ""}
      ],
      "gate": {"lat": 51.4984528, "lon": -0.1260286, "radius_m": 40},
      "compass": true,
      "distance": true,
      "question": null,
      "lens": {
        "kind": "stencil",
        "src": "img/jewel-tower-stencil.png",
        "note": "Line the drawing up with the building.",
        "auto": true,
        "match": {"threshold": 0.35, "hold_ms": 600, "gate": true, "fallback_s": null}
      },
      "after": [
        {"type": "text",
         "text": "In 1834 the Palace of Westminster burned down. The brass bar that defined the length of England's unit of measure, the imperial yard, was lost in the fire. The building in front of you is the Jewel Tower. From 1869 this is where the nation's weights and measures were tested against the new standards, until the vibration of traffic made precise measurement impossible.\n\nForty bronze bars were cast to replace what had burned. The best became the standard and the rest were sent out across the world, so that this could never happen again. One is bricked into the wall of the Palace across the road. Not all of the others can be accounted for."},
        {"type": "pause", "ms": 1000},
        {"type": "text",
         "text": "It is said that the fire was started by the Clerk of Works burning two cartloads of old willow tally sticks in stoves meant for coal, but this is not true. The fire was set deliberately, and something else was lost that night that is not documented."}
      ]
    }

After the last block, **Next** goes to the outro placeholder for now.

The hunt-level flag in the same file becomes `"test_mode": true`.

## 7 · What the player sees, in order

1. Title. Two intro paragraphs. **Begin**, which ticks.
2. Header **Location one**. The clue sentence, then the sketch.
3. Compass point while far, live distance all the way, **Check location**,
   Skip. On pass the header becomes **Westminster**, "You're here." and a lit
   **Continue**, which ticks.
4. The camera opens with the orange stencil. Score bar, numbers, threshold
   slider, **Log**, **Skip**, **Progress** grey until matched. Progress
   ticks.
5. The first after-paragraph, a one-second pause, the second. **Next.**

## Acceptance

1. No number of stops appears anywhere in the opening or on cards.
2. Begin ticks on an iPhone (iOS 17.4+) and on Android.
3. A single tap on revealing text does nothing; three taps inside 1.5 s
   finish it.
4. The gate shows no prompt and no privacy note; the header flips to
   Westminster on pass, not before.
5. With `test_mode` true, the slider appears in the lens, moving it moves the
   tick and changes when Progress lights, and Log lines carry the threshold.
   With `test_mode` false, neither the slider nor any Skip exists.
6. The after-text pauses for one second between the two paragraphs.
7. Everything in handoffs 1–3 still works, and `/fixture/` still plays.
