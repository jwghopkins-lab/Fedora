# The Architect Order — handoff 6: the third stop

Builds on handoffs 1–5. Adds one stop after the Abbey, with no location gate,
a camera match, a question and an after-text, and one ordering rule.

## Assets

Copy from the Fedora clone, `docs/handoff/assets/`, into `app/img/`:

| File | What it is |
|---|---|
| `elizabeth-tower-stencil.png` | Stencil of the Elizabeth Tower from Parliament Square, 566 × 800, transparent, orange 3 px lines. |
| `elizabeth-tower-stencil-preview.jpg` | The stencil over the reference photo. README only. |

## Ordering rule

On a stop with **no gate** and an **auto lens**, the lens takes the gate's
slot: body → **Open the camera** → match → **Progress** → question → after →
**Next**. Stop 2 has no question so nothing changes there; this stop has one.

## The stop

Append to `stops` after the second stop. Text is verbatim.

    {
      "id": "third",
      "chapter": "Location three",
      "reveal": {"chapter": "Elizabeth Tower"},
      "body": [
        {"type": "text",
         "text": "George Airy. Astronomer Royal for forty-six years. Arthur's notes come back to him more than to anyone else."},
        {"type": "text",
         "text": "After the fire, Airy chaired the commission that decided what the new yard would be. When they built this tower, Airy wrote the specification for its clock: the first stroke of every hour true to within one second, checked twice a day by telegraph to his observatory at Greenwich. It is kept to time with old pennies laid on the pendulum. One penny is worth two fifths of a second a day. And at Greenwich, in 1851, he set the instrument that fixes the line the world's time is measured from."},
        {"type": "pause", "ms": 1000},
        {"type": "text",
         "text": "The yard, the clock, and the line. One man held all three. Arthur wanted to know what he did with them.\n\nCross the square and find the clock."}
      ],
      "gate": null,
      "lens": {
        "kind": "stencil",
        "src": "img/elizabeth-tower-stencil.png",
        "note": "Line the drawing up with the tower.",
        "auto": true,
        "match": {"threshold": 0.35, "hold_ms": 600, "gate": true, "fallback_s": null}
      },
      "question": {
        "ask": "What do they lay on the pendulum to keep it to time?",
        "answers": ["PENNIES", "PENNY", "OLD PENNIES", "PENCE", "COINS", "COPPERS"],
        "guesses": 3
      },
      "after": [
        {"type": "text",
         "text": "Twice a day, this clock's performance went down the wire to Greenwich, where Airy's line runs through the floor of his observatory. Since 1884 the world has measured its time from that line. Arthur went there. We haven't, yet."}
      ]
    }

## What the player sees

1. Header **Location three**. Two paragraphs, a one-second pause, a third.
2. **Open the camera**, lit when the text finishes. The tower stencil, score
   bar, slider in test mode, Log, Skip, Progress.
3. Progress ticks; header becomes **Elizabeth Tower**.
4. The question, three guesses, a correct answer ticks.
5. The after paragraph. **Next**, to the outro placeholder until stop four.

## Acceptance

1. Stops 1 and 2 unchanged.
2. On stop 3 the camera opens only from the tap; the question appears only
   after Progress; the after-text only after the question resolves.
3. "pennies", "penny", "pence", "coins" and a one-letter typo of any of them
   are accepted; three misses mark it wrong and show the answer.
4. The header reads Elizabeth Tower after Progress, not before.
5. `/fixture/` still plays.
