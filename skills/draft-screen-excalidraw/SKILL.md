---
name: draft-screen-excalidraw
description: Produces one or more .excalidraw wireframe file(s) prototyping a single app/product screen — precise, populated with realistic contextual content (not lorem ipsum), showing the screen's most complete/complex case by default. Use this whenever the user wants a visual prototype/mockup/wireframe of a screen following a design discussion or negotiation, or explicitly asks for an "excalidraw", "wireframe", or "prototype" of a screen. Also use it any time draft-screen-markdown is being used for the same screen and a visual companion is wanted, or when the draft-screen skill orchestrates a full screen draft. Trigger even without the word "excalidraw" — "mock this screen up", "show me what this would look like", "sketch the dashboard screen" all call for this skill.
---

# Draft Screen Excalidraw

## Why this exists

A screen description in prose or a data model tells you what a screen
*does*; it doesn't settle layout, hierarchy, or what it feels like to
actually use. A wireframe does. This skill produces that wireframe as a
real `.excalidraw` scene file — not a picture, an editable scene — using a
bundled Python builder (`scripts/excalidraw_builder.py`) instead of
hand-writing element JSON, which is slow and error-prone (every element
needs ~20 fields in the right shape, and coordinates drift fast by hand).

The output is meant to be handed to whoever eventually implements the
screen with a real design system/brand — it should be precise and
realistic enough to design against, while staying neutral enough that it
doesn't fight whatever visual language gets applied later.

## Core principles

**Contextualize, don't placeholder.** Use plausible real content that fits
the product's actual domain: real-sounding names, dates, and counts drawn
from the entities the screen deals with ("7 of 12 seats filled", not "X/Y
items"). A screen full of "Lorem ipsum" or "Item 1, Item 2, Item 3" doesn't
tell an implementer anything about how the layout holds up under real
content lengths, states, or edge cases.

**Show the full/complex case by default.** A screen with every list empty
and every optional element hidden doesn't exercise the layout. Populate it
with enough content and state variety (a mix of statuses, a slightly-too
long title, a badge or two) that whoever looks at it can see how the
screen behaves when it's actually being used, not just when it's freshly
created. If the screen genuinely has meaningfully different situations
(e.g. an admin view vs. a member view, a populated dashboard vs. a
single-tenant one), a *second or third* variant file is the right call —
one file per genuinely distinct situation. Don't produce a variant for
every small permutation (each status value, each role) — that's
over-engineering, covered instead by describing the range in the companion
markdown doc if one exists. Two to three files per screen is a reasonable
ceiling; if you find yourself wanting more, the situations probably aren't
distinct enough to warrant separate files.

**Precise, not final-designed.** Get proportions, spacing, and information
hierarchy right — this needs to be workable, not just illustrative. But
stay on the neutral wireframe palette the builder provides (grayscale ink/
label/muted/border/surface, plus semantic tones for state — success/
warning/danger/info) rather than reaching for a specific brand's colors,
custom fonts, or a particular icon set. Color and iconography should
communicate meaning (this is confirmed, this is pending) not brand
identity — that part is deliberately left for whoever applies the real
design system later.

**Stay consistent with any companion markdown doc.** If a
`draft-screen-markdown` document exists (or is being written alongside)
for the same screen, the wireframe and the doc describe the same screen —
same entities, same states, same actions. Don't invent UI elements in the
wireframe that imply behavior the doc doesn't mention, and don't leave out
something the doc calls a primary action.

## How to use this

1. **Read `references/components.md`** before writing anything — it's the
   quick-reference vocabulary for every primitive the builder offers
   (`rect`, `ellipse`, `text`, `divider`, `phone_frame`, `top_bar`, `badge`,
   `avatar`, `card`, `button`, `input_field`, `list_row`, `bottom_nav`) and
   the shared palette (`PALETTE`), with the sizing/tone conventions used
   consistently across reference screens. Reuse these rather than
   reinventing layout math — they already produce valid, consistent
   Excalidraw elements. For the full implementation, `scripts/
   excalidraw_builder.py` is short and worth a skim too. Extend the module
   in place (same pattern as the existing methods) if a screen genuinely
   needs a primitive that isn't there yet.

2. **Plan the layout before coding it**: sketch (in your own reasoning, or
   briefly in prose to the person) what rows/sections the screen needs top
   to bottom, at what approximate y-coordinates, before writing the
   builder calls. This catches overlap and ordering mistakes before they're
   buried in coordinates.

3. **Write a small script** that imports the builder and constructs the
   scene:

   ```python
   import sys
   sys.path.insert(0, "<path to this skill's scripts/ folder>")
   from excalidraw_builder import Scene, PALETTE

   s = Scene(width=360, height=780)  # adjust for tablet/desktop if the
                                       # screen isn't mobile-first
   s.phone_frame()
   s.text(0, -34, "Screen name", size=18)
   # ... rows of content, using realistic data ...
   s.bottom_nav([("Home", None), ("Activity", None), ("Profile", None)],
                active_index=0)
   s.save("screen-name.excalidraw")
   ```

4. **Run it**, then sanity-check the output is valid JSON with a plausible
   element count before considering the file done (a quick
   `python3 -c "import json; json.load(open('...'))"` and eyeballing
   `len(elements)` catches most mistakes).

5. **Name variant files clearly** if producing more than one, e.g.
   `screen-name--admin-view.excalidraw` / `screen-name--member-view.excalidraw`
   rather than numbering them, so the distinction is legible from the
   filename alone.

## What this skill does not do

It does not render the scene to an image — the file is only truly
viewable inside an Excalidraw-compatible viewer. Pair with the
`render-excalidraw` skill to get a `.svg` for anything that needs to be
viewed inline, embedded elsewhere, or attached where an interactive
`.excalidraw` file isn't practical. The `draft-screen` skill already
chains both steps automatically for a full screen draft.
