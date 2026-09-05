# The Architect Order — handoff 3: the first real stop

Builds on handoffs 1 and 2. Read both first. This adds the first real stop,
two small behaviours, and the images for it. Nothing about the story is in
here beyond what the player sees.

## Assets

Copy from the Fedora clone, `docs/handoff/assets/`, into `app/img/`:

| File | What it is |
|---|---|
| `jewel-tower-sketch.png` | The drawing the player is shown to find the building. 800 × 916, transparent outside the paper. **Render it full width on the card with no border, background or shadow, so the torn paper floats on the card.** Do not alter it. |
| `jewel-tower-stencil.png` | The stencil for the camera match. 731 × 800, transparent, orange lines 3 px. The match mask reads alpha, exactly as handoff 2 says, so the colour is free and orange is chosen to be visible over stone. |
| `jewel-tower-stencil-preview.jpg` | The stencil drawn over the reference photo, so you can see what an aligned match looks like. Not shipped to the player. Use it in the README as the example of how a stencil is made. |

## Three small behaviours

**1. Skips, one flag.** Hunt-level `"skips": true`. When true, every location
gate, every match, and every question shows a plain **Skip** button that
resolves that part as skipped and moves on. When false, none of them exist.
One field, so the owner can turn them off with one edit before friends play.
Skipped parts count in the outro as skipped, not wrong.

**2. Live distance.** Per-stop `"distance": true`, only with a gate. While the
gate card is open, show the distance to the target from each fix, updated as
the compass is: "About 1.2 km", then "About 650 m", then "About 240 m".
Rounding: nearest 100 m at or above 1 km, nearest 50 m from 500 m to 1 km,
nearest 10 m below 500 m. Shown until the gate passes. The compass rule is
unchanged: bearing only beyond 500 m. The readout is informational; the
**Check location** button still does the formal check.

**3. A name that resolves.** Per-stop optional `reveal` block, only with a
gate:

    "reveal": {"at_m": 500, "chapter": "Westminster"}

Until revealed, the card shows the stop's `chapter` and `title` as written.
When a usable fix puts the phone within `at_m` of the target, the chapter
label changes to `reveal.chapter` (and the title to `reveal.title`, if given).
The change is one-way and is saved in state, so a wobbling fix never flips it
back, and the collapsed line for a finished stop shows the revealed name. If
the gate passes without a fix ever reading under `at_m` (the simulator jumping
straight in, say), reveal on the pass instead. `at_m` defaults to 500 so it
coincides with the compass dropping out; the two together are the moment the
place stops being a direction and becomes somewhere. Validation: `reveal`
requires a gate; at least one of `chapter` or `title` must be present.

## Build both hunts

`build.py` takes an output directory. The workflow builds
`content/architect-order.json` to the site root and `content/fixture.json` to
`site/fixture/`, so the real hunt is at the Pages URL and the fixture at
`/fixture/`. Two obvious variables at the top of the workflow.

## The content

`content/architect-order.json`. Placeholders in square brackets are the
owner's to replace later; leave them as written.

    {
      "id": "architect-order",
      "title": "The Architect Order",
      "skips": true,
      "diary_mm": {"w": 148, "h": 210},
      "intro": [
        {"type": "text", "text": "[Intro to come.]"}
      ],
      "outro": [
        {"type": "text", "text": "[Outro to come.]"}
      ],
      "stops": [
        {
          "id": "first",
          "chapter": "Location one",
          "title": "The first place",
          "reveal": {"at_m": 500, "chapter": "Westminster"},
          "body": [
            {"type": "text",
             "text": "Go to the place where fire burned the length of England. Then find this building."},
            {"type": "image", "src": "img/jewel-tower-sketch.png",
             "alt": "A pen sketch of a building, torn from a notebook", "caption": ""}
          ],
          "gate": {"lat": 51.4984528, "lon": -0.1260286, "radius_m": 40,
                   "prompt": "Are you standing in front of it?"},
          "compass": true,
          "distance": true,
          "question": null,
          "after": [
            {"type": "text", "text": "[After text to come.]"}
          ],
          "lens": {
            "kind": "stencil",
            "src": "img/jewel-tower-stencil.png",
            "note": "Line the drawing up with the building.",
            "auto": true,
            "match": {"threshold": 0.35, "hold_ms": 600, "gate": true, "fallback_s": null}
          }
        }
      ]
    }

The chapter label and title are deliberately blank of any place name until
the reveal. Nothing on screen may say where the building is before the player
is within 500 m of it.

## What the player sees, in order

1. The clue sentence, revealed word by word, then the sketch.
2. The gate prompt with **Check location**, a compass point while more than
   500 m away, and the live distance all the way in. **Skip** beside it.
   As the distance drops below 500 m, the compass goes and the label above
   the title changes from "Location one" to "Westminster".
3. On passing: "You're here." and a lit **Continue**, which ticks.
4. The camera opens by itself with the orange stencil. Score bar, numbers,
   **Log**, **Skip**, and **Progress**, grey until the match holds for 600 ms.
   Progress ticks on tap.
5. The after text, then **Next**, which for now ends the hunt at the outro.

## Acceptance

1. At the Pages root, the hunt opens on the clue and the sketch renders full
   width with no visible edge to the image.
2. With the simulator 800 m away, a compass point and a distance show and the
   label reads "Location one"; at 300 m the compass is gone, the distance
   remains, and the label now reads "Westminster" and stays so; inside 40 m
   the check passes and Continue ticks. Jumping the simulator straight from
   800 m to inside the radius also reveals the name.
3. The camera opens itself with the orange stencil after the gate. Lining it
   up on the preview image on another screen lifts the score; Progress lights
   after 600 ms above 0.35 and ticks on tap.
4. Skip is present on the gate, the match and (on the fixture) the questions,
   and vanishes everywhere when `skips` is false and the site is rebuilt.
5. `/fixture/` still plays in full. Give fixture stop two a `reveal` as well,
   so the behaviour can be seen there without the real hunt.
