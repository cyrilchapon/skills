---
name: draft-screen
description: Full screen-drafting workflow — for one or more app/product screens, produces a complete package of a descriptive markdown doc, one or more .excalidraw wireframes, and their rendered .svg previews. Use this whenever the user wants to "draft", "design", or "spec out" a screen (or several) end to end, rather than just one artifact of it — e.g. "let's design the next screen", "draft the settings screen", "can you spec and mock up screens X, Y and Z". If the user asks for only the doc, or only the wireframe, use draft-screen-markdown or draft-screen-excalidraw directly instead — this skill is specifically for producing the full set together.
---

# Draft Screen

## What this does

Chains three sibling skills into one workflow so a screen goes from
"discussed" to "fully documented and mocked up, viewable" in one pass. For
each screen requested, it produces:

1. A `.md` document (via **draft-screen-markdown**) — purpose, data
   touched, states, actions, relations to other screens.
2. One or more `.excalidraw` wireframe(s) (via **draft-screen-excalidraw**)
   — precise, contextualized, showing the complete/complex case, with
   additional variant files only where the screen genuinely has distinct
   situations worth showing separately.
3. A rendered `.svg` for each `.excalidraw` file (via **render-excalidraw**)
   — a static, dependency-free image of the wireframe, viewable without an
   Excalidraw-compatible viewer.

## Before starting

This skill depends on **draft-screen-markdown**, **draft-screen-excalidraw**,
and **render-excalidraw** all being available. If any of them isn't
installed, say so before proceeding rather than improvising a worse
version of what they'd do — the person may want to install the missing
piece first.

## Workflow, per screen

Do these in order for each screen — writing the doc first means the
wireframe has a settled description to stay consistent with, rather than
the two drifting apart if built independently.

1. **Write the markdown doc first.** Follow `draft-screen-markdown`'s
   template and guidance in full. This is also where any genuinely open
   questions from the discussion get surfaced explicitly (its "Open
   questions" section) — settle or note them now, since the wireframe step
   needs to know what it's depicting.

2. **Build the wireframe(s) from that doc.** Follow
   `draft-screen-excalidraw`'s guidance, using the just-written doc as the
   source of truth for entities/states/actions so the two artifacts don't
   diverge. Decide here whether this screen needs one file or a small
   number of variants (per that skill's guidance on when variants are
   warranted vs. over-engineering).

3. **Render each `.excalidraw` to `.svg`** using `render-excalidraw`'s
   bundled script. Batch all files for this screen (and, if drafting
   several screens in one pass, consider batching across screens too) in
   a single invocation rather than one process launch per file.

4. **Name the output set so it reads as one unit.** For a screen called
   e.g. "Notification settings": `notification-settings.md`,
   `notification-settings.excalidraw` (+ `--variant-name.excalidraw` if
   applicable), and their matching `.svg`s. If several screens are being
   drafted in the same pass, group each screen's files together (a
   subfolder per screen is reasonable once there are more than a couple of
   screens) rather than dumping everything into one flat directory.

## Multiple screens in one request

When the person asks for several screens at once, run the full
per-screen workflow above for each one rather than doing all the docs
first and then all the wireframes — finishing one screen completely
before moving to the next means an early mistake (e.g. a data-model
assumption that turns out wrong) surfaces before it's been repeated across
every screen.

## Presenting the result

For each screen, share the `.md` and the rendered `.svg`(s) so the person
can review content and layout without needing an Excalidraw viewer; make
the `.excalidraw` file(s) available alongside for anyone who wants to open
and edit them directly. Briefly note anything flagged as an open question
in the doc's "Open questions" section — those are exactly the things worth
a quick check-in before considering the screen settled.
