---
name: data-model-diagram
description: Use this skill whenever the user wants to design, evolve, review, or document a data model — entities, relationships, a database schema, a domain model — as a Mermaid diagram. Trigger on phrases like "let's design the data model", "model the entities for X", "ER diagram", "entity-relationship diagram", "schema diagram", "modèle de données", "diagramme d'entités", or any request to represent how entities in a product/domain relate to each other. Also trigger mid-project when the user wants to add a new slice/layer to a data model already under discussion, switch between a simplified and a detailed view of it, or export the current version as a Mermaid file. This skill governs both the modeling conversation (what entities/relationships/decisions to make) and the diagram output — use it even if the user only asks for the diagram and doesn't mention "modeling" explicitly.
---

# Data Model Diagram

A skill for building a data model **iteratively and conversationally**, represented as a Mermaid diagram, for any product or domain — not tied to any particular project, project tracker, or documentation system.

Input is whatever the user brings: a screen description, a set of user stories, existing docs, a rough verbal description of a domain, or nothing more than "we need a User and a Team". Output is a Mermaid diagram (rendered inline) and, on request, a `.mmd`/`.md` file containing it. Nothing in this skill assumes a specific downstream tool (no Linear, no Notion, no particular tracker) — if the user wants the result published somewhere, that's a separate, project-specific step outside this skill.

## Core loop

Data models are rarely right the first time, and dumping a fully-detailed schema in one shot invites the user to rubber-stamp something they haven't really scrutinized. Work in small, confirmed increments instead:

1. **Elicit before drawing.** From whatever input the user gives, extract a candidate list of entities and relationships in prose first — no diagram yet. Name the entities, state the relationships in a sentence each, and flag anywhere you made a judgment call (see "Domain-modeling decisions to surface" below). Let the user correct course before anything is rendered; a wrong diagram is more expensive to unwind than a wrong sentence.
2. **Scope in slices, not the whole model at once.** If the domain is more than a handful of entities, propose a natural slice (e.g. "identity & membership" before "the event/workflow loop" before "configuration"). Confirm one slice, render it, then move to the next. Merge slices into a combined diagram only when asked.
3. **Render, don't just describe.** Once entities/relationships for the current slice are confirmed, produce the Mermaid diagram (see "Rendering" below) rather than leaving it as a text description — the diagram itself is the artifact the user is validating.
4. **Keep a running model.** Track cumulatively, across the conversation, which entities/fields/relationships have been confirmed so far, so the user can ask for "layer 1 + layer 2", "just the last slice", "the detailed version of all of it", etc. without re-explaining the whole model.
5. **Default to simplified, expand on request.** See "Two output modes" below — don't show fields/attributes unless asked.

## Diagram type

Default to Mermaid's `erDiagram` — it's purpose-built for entities and relationships, supports cardinalities natively, and (importantly) can render an entity as a single title box with no visible attribute compartments simply by omitting its attribute block. That means both output modes (simplified and detailed, below) can stay in the **same diagram type** — don't switch to `classDiagram` or another type to get a "boxes only" look; that trades away ER cardinality notation for no real benefit and makes the two modes harder to keep consistent with each other.

Only reach for a different Mermaid diagram type if the domain genuinely isn't entity/relationship shaped (e.g. a state machine belongs in `stateDiagram`, a process flow in `flowchart`) — for a data model specifically, stay on `erDiagram`.

## Two output modes

Ask which is wanted only if truly ambiguous; otherwise default to **simplified** and let the user ask for **detailed** explicitly.

**Simplified (default):**
- Entity boxes carry only the entity name — no attribute block at all (`ENTITY_NAME {\n...\n}` is omitted entirely, not just emptied).
- Relationship lines keep Mermaid's cardinality notation (`||--o{`, `}o--o{`, etc.) — never drop this, it's the actual modeling content.
- Relationship labels are empty (`""`) by default.
- **Exception:** if two (or more) distinct relationships connect the *same pair* of entities, label each with a short verb so they're distinguishable (e.g. a `Membership` that both *declares* and *validates* a `MemberInstrument`, or is both *assigned to* and *confirms* an assignment). Every other relationship in the diagram stays unlabeled — don't let one disambiguating pair push you into verbalizing everything.

**Detailed (on explicit request):**
- Full attribute blocks per entity: field name, type, `PK`/`FK` markers, and enum value lists inline where useful (Mermaid supports a quoted comment-like string after a field for this).
- Same cardinality + duplicate-link-verb rules as simplified.
- This is the version to use when the request is genuinely for a technical reference artifact (e.g. "document the model"), not for a conversational sanity-check of the shape.

## Domain-modeling decisions to surface

These recur across most domains. Surface them explicitly to the user rather than silently picking a default — each is a real fork, not a stylistic detail:

- **Explicit pivot/join entities vs. bare foreign keys.** When two entities have a many-to-many relationship that itself carries meaning or attaches further data (roles, timestamps, per-pair attributes), model the join as its own named entity (e.g. a `Membership` between `User` and `Team`) rather than an anonymous join table — it gives every "scoped to this pairing" concept a home instead of duplicating `(user_id, team_id)` pairs across several tables.
- **Catalog entity vs. enum.** When a set of values is specific to a parent record and likely to vary across instances (e.g. named categories, tags, or sections that differ per organization/store/band), model it as its own entity scoped to that parent, not a global hardcoded enum. Reserve real enums for values that are structurally fixed and shared everywhere (e.g. a status field with a small fixed set of lifecycle states).
- **YAGNI on not-yet-designed subsystems.** If part of the domain (e.g. a rules engine, a configuration cascade) hasn't been designed in detail yet, don't paper over the gap with an opaque blob field (JSON, freeform text) "to cover it for now." Represent only the part that's actually decided (e.g. a bare enum naming *which* mode applies), and leave the rest out of the diagram entirely until it's designed — note it as a known gap instead of inventing an untyped placeholder.
- **Derived/computed vs. stored.** Explicitly call out anything that looks like it could be a field but is actually computed at read time from other entities (counts, aggregates, dynamically-evaluated pairing/matching rules) and say so in the diagram's accompanying notes. This keeps an implementer from reflexively adding a column for something that should never be persisted.
- **Ownership/ordering vs. hierarchy/role.** Watch for domains where "who is responsible for tracking this record" is a distinct concept from "where this person sits in a structural hierarchy" (e.g. an event owner vs. a musical/organizational role). These are easy to conflate into a single "role" field; if the user's domain has both, model them as separate relationships.

When any of these come up, state the fork and your recommendation in one or two sentences, and let the user confirm or override — don't resolve it silently and reveal the choice only in the rendered diagram.

## Rendering

Prefer rendering the diagram inline as you go, not just handing back raw Mermaid text:

- If a Mermaid-rendering tool is available (e.g. an MCP Mermaid tool — check the current tool list, or use `tool_search`/`search_mcp_registry` with keywords like `["mermaid", "diagram"]` if deferred tools are in play), use it to render and validate the diagram at each step. This gives the user something to look at immediately and catches syntax errors before they pile up.
- If no such tool is available, fall back to a fenced ` ```mermaid ` code block — this renders natively in many chat UIs, editors, and markdown viewers, and is still a valid deliverable on its own.
- Either way, the underlying Mermaid source is the artifact — keep it as the single source of truth you edit incrementally, rather than regenerating from scratch each time a small change is requested.

## Producing the file

When the user asks to export or save the model (as opposed to just viewing it inline), write a `.mmd` file (raw Mermaid source) or a `.md` file (the same source wrapped in a ` ```mermaid ` fence, optionally with a short prose scope note above it) — ask which if it's not clear from context. Don't assume a destination system; if the user wants it published somewhere specific (a wiki, a tracker, a docs site), that integration is outside this skill's concern — just hand back the file.

## Quick reference

| Situation | What to do |
|---|---|
| New domain, first pass | Elicit entities/relationships in prose, confirm, then render simplified `erDiagram` |
| Large domain | Slice into layers, confirm and render one at a time, merge only on request |
| User says "detailed" / "with fields" | Add full attribute blocks; keep same cardinality + duplicate-link-verb rules |
| Two relationships, same entity pair | Label just that pair with short verbs; leave all other links unlabeled |
| Something looks like a field but is computed | Leave it off the diagram; note it as derived, not stored, in accompanying text |
| Part of the domain isn't designed yet | Represent only the decided sliver (e.g. a bare enum); don't add an opaque blob to cover the gap |
| User asks to save/export | Write `.mmd` or `.md` (fenced); don't assume any publishing destination |

See `references/worked-example.md` for a full walkthrough of these conventions applied to a sample domain, if a concrete illustration is useful before starting.
