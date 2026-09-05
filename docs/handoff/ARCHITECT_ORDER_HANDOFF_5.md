# The Architect Order — handoff 5: the second stop

Builds on handoffs 1–4. This adds one stop after the Jewel Tower, with no
location gate, and one rule about how the camera opens.

## Assets

Copy from the Fedora clone, `docs/handoff/assets/`, into `app/img/`:

| File | What it is |
|---|---|
| `abbey-west-front-stencil.png` | Stencil of the west front of Westminster Abbey, 471 × 800, transparent, orange 3 px lines. Both towers with their pinnacles, the belfry openings, the clock and the rose, the balustrades, the gable, the great west window, the two window tiers, the lower band and the west door. |
| `abbey-west-front-stencil-preview.jpg` | The stencil over the reference photo, for the README and for judging alignment. Not shipped to the player. |

## One rule: the camera always opens from a tap

iOS will refuse the camera unless the request comes from a user gesture, and
the fix window and the reveal timer are not gestures. So `auto: true` never
opens the lens by itself. It means: **at the moment the lens would have
opened, show a lit button, `Open the camera`, and the tap opens it.** After a
location gate that is the existing Continue button, which now opens the lens
directly when the stop has an auto lens. On a stop with no gate, the button
appears when the body reveal finishes, including when a triple tap finishes
it. Apply this to stop 1 as well.

## Reveal on a stop with no gate

`reveal` with no gate on the stop applies when **Progress** is pressed on the
match.

## The stop

Append to `stops` in `content/architect-order.json`, after the first stop.
Text is verbatim.

    {
      "id": "second",
      "chapter": "Location two",
      "reveal": {"chapter": "Westminster Abbey"},
      "body": [
        {"type": "text",
         "text": "The only public copy of Sir Isaac Newton's private notes on the Great Pyramid and the sacred cubit."},
        {"type": "text",
         "text": "Arthur's recovered notes contain Newton's private working papers from the 1680s, cross-referencing John Greaves's Pyramidographia. Rather than mystical prophecies, they show a rigorous, obsessive attempt to reverse-engineer the ancient Egyptian Memphis cubit and the Jewish sacred cubit using raw architectural dimensions. The missing folios detail calculations converting pyramid chamber heights into English inches, hunting for a mathematical link between ancient temple layouts and contemporary mint standards."},
        {"type": "text",
         "text": "Newton is buried here, in the Abbey, a few hundred yards from where you stand. He lies in the nave against the choir screen. His monument was unveiled in 1731. He reclines beneath a globe of the heavens, and the globe rests on a pyramid. On the carving below him, boys handle a telescope and a prism, and one of them weighs the sun and the planets on a steelyard. The men who buried him put a pyramid and a balance on his tomb."},
        {"type": "text",
         "text": "He lay in state in the Jerusalem Chamber, at the west end, before they carried him in. The two towers above it were finished eighteen years after he was buried. He never saw them. Go round to the west front, and look up."}
      ],
      "gate": null,
      "question": null,
      "lens": {
        "kind": "stencil",
        "src": "img/abbey-west-front-stencil.png",
        "note": "Line the drawing up with the front of the Abbey.",
        "auto": true,
        "match": {"threshold": 0.35, "hold_ms": 600, "gate": true, "fallback_s": null}
      },
      "after": []
    }

With `after` empty, pressing Progress closes the lens and shows **Next**
straight away; Next goes to the outro placeholder until the third stop exists.

## What the player sees

1. Header **Location two**. Four paragraphs, revealed in turn.
2. **Open the camera**, lit when the last paragraph finishes. Tap.
3. The camera with the orange west-front stencil. Score bar, numbers, the
   test-mode slider, **Log**, **Skip**, **Progress** grey until matched.
4. Progress ticks, the header becomes **Westminster Abbey**, and **Next**
   appears.

## Acceptance

1. Stop 1 still plays; its Continue after the gate now opens the camera
   directly.
2. Stop 2 has no location gate: no compass, no distance, no Check location.
3. The camera opens only from the tap, on iPhone and Android alike.
4. Lining the stencil up on the preview image on another screen lifts the
   score; Progress lights after 600 ms above the threshold and ticks.
5. The header reads Westminster Abbey after Progress, not before.
6. `/fixture/` still plays.
