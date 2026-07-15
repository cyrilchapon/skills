---
name: draft-screen-markdown
description: Writes a structured, agent-readable markdown (.md) document describing a single app/product screen — its purpose, the data it touches (succinct, just enough to later extrapolate a data model, not a full schema), its states, its user-triggered actions, and its relations to other screens. Use this whenever the user has been discussing or negotiating a screen's design and wants it written down, whenever the user explicitly asks to "document" or "spec out" a screen, and any time a screen is being drafted alongside a visual prototype (an .excalidraw wireframe, a screenshot, a Figma/Canva link) that needs a companion description. Trigger this even if the user doesn't say "markdown" explicitly — "write up what we just designed", "can you document this screen", "spec this out for the data model later" all call for this skill.
---

# Draft Screen Markdown

## Why this exists

A screen's visual prototype (wireframe, screenshot, Figma frame) shows what
it looks like but not what it *means*: which entities it touches, what a
user can do on it, what happens in its empty/loading/error states, how it
connects to the rest of the product. That's the gap this document fills.
It's written to be read by an agent doing follow-up work later — extending
the screen, designing the data model, building the next related screen —
so structure and precision matter more than prose polish.

This is deliberately **not** a full data-model design pass. Naming an
entity and its key fields is enough for someone to extrapolate the rest
later; don't invent constraints, indexes, or relationships the
conversation didn't establish.

## Template

Use this structure. Omit a section entirely rather than leaving it with
placeholder content if it doesn't apply to the screen at hand — a missing
section reads as "not applicable"; an empty or vague one reads as
"forgotten". Headers are shown in English below; see "Language and tone"
for when to translate them.

```markdown
# Screen — <Screen name>

## Purpose
<1 short paragraph. What is this screen for? In what situation does someone
land here? What does "done" look like from the user's point of view?>

## Entities & fields involved
<Bulleted list. For each entity touched: its name (bold) and the handful of
fields that matter for THIS screen — not every field the entity might ever
have. Call out anything a future data modeler would otherwise have to
re-derive from context: scoping rules ("always scoped to the current
workspace, never global"), static vs. computed fields, fields that are
read-only here vs. editable elsewhere.>

## States & lifecycle
<Only if the screen has meaningfully different states to handle: empty
state copy, loading, error, a multi-step lifecycle. Say what each state
looks like and what triggers the transition. Omit if the screen doesn't
have interesting state beyond "shows data or doesn't".>

## Actions
<Bulleted list of things a user can actually do here — taps, submissions,
navigations triggered from this screen (not navigations arriving at it;
that's the relations section).>

## Relations to other screens
<Bulleted list: which screens this one links to or from, which flows it
reuses (e.g. "reopens the onboarding screen"), what's explicitly out of
scope and tracked as a separate, already-identified screen/ticket.>

## Open questions
<Optional. If the negotiation surfaced a real unresolved question — a
variant nobody picked yet, a rule someone said "we'll figure out later" —
name it here explicitly instead of letting it evaporate. Delete this
section if there's nothing genuinely open.>

## Fidelity note
<If there's a companion visual prototype: name the file/link and clarify
what's fixed (layout, content, states shown) vs. not fixed (colors, exact
spacing, iconography) at this stage.>
```

## How to write each section well

- **Purpose**: answer "why does this screen exist", not "what's on it" —
  the fields/actions sections already cover the what.
- **Entities & fields involved**: think about what the NEXT screen's
  author, or a data-model design pass, would need from this doc without
  re-reading the whole conversation. That's the bar for "enough detail" —
  past that point you're doing data modeling prematurely, which the person
  hasn't asked for and may want to do differently later.
- **States & lifecycle**: this section catches the details that are easy
  to lose — explicit empty-state text, what happens while data is loading,
  what an error looks like. If the conversation settled on specific
  wording for an empty state (e.g. "You're all caught up"), quote it;
  these decisions get lost fast otherwise.
- **Open questions**: negotiations naturally surface things like "we'll
  need a variant for X but let's not design it now." Writing that down
  explicitly (rather than burying it as an aside inside a field
  description) means it doesn't get silently dropped, and someone reading
  the doc later immediately sees it's still open rather than assuming it
  was a deliberate omission.

## Language and tone

Write in whatever language the conversation and project have actually been
using for this kind of document — check for existing sibling documents in
the same project first (e.g. other screen docs already in the repo/tracker)
and match their language and section-header wording exactly, even if it
differs from the language used for other technical artifacts in the same
project (code, issue titles). Translate the section headers above to that
language rather than leaving them in English if the project's convention is
another language. Consistency across the set of screen docs matters more
than any single stated convention. If there's no precedent to match,
default to the language the person is currently writing in.

Keep prose genuinely short — a few sentences per section, bullets over
paragraphs wherever possible. This document should be quick to scan.

## Output

Save as a `.md` file. Suggest a filename that matches the screen (e.g. the
screen's identifier/ticket if there is one, otherwise a short kebab-case
name derived from the screen's title) unless the person specifies one.
