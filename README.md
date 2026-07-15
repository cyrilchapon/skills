# Skills

Personal collection of [Claude](https://claude.com) skills, versioned here
instead of living only inside claude.ai's skill editor.

Skills are grouped into plugins when they form a coherent workflow. The
first group, **screen-drafting**, bundles four skills for taking an app/
product screen from a design discussion to a documented, wireframed,
viewable deliverable. **data-model-diagram** is a second, independent
plugin for modeling entities/relationships as a Mermaid diagram. More
skills/plugins will be added over time.

## Plugin: screen-drafting

| Skill | Produces | Triggers on |
|---|---|---|
| [`draft-screen`](plugins/screen-drafting/skills/draft-screen) | The full package below, for one or more screens | "draft/design/spec out a screen", requests for a screen end-to-end rather than one artifact of it |
| [`draft-screen-markdown`](plugins/screen-drafting/skills/draft-screen-markdown) | A structured `.md` doc (purpose, entities, states, actions, relations, open questions) | "document/spec out this screen", "write up what we designed" |
| [`draft-screen-excalidraw`](plugins/screen-drafting/skills/draft-screen-excalidraw) | One or more `.excalidraw` wireframes, contextualized with realistic content | "mock up/wireframe/prototype/sketch this screen" |
| [`render-excalidraw`](plugins/screen-drafting/skills/render-excalidraw) | Standalone `.svg` renders of `.excalidraw` files | Any time an `.excalidraw` file needs to be viewed, shared, or embedded |

### How they relate

These skills are **not** technically importable by one another — Claude
Code plugins have no dependency/import mechanism between skills, only
natural-language references that resolve if the referenced skill happens to
be loaded in the same conversation. So:

- `draft-screen` is an orchestrator: it calls `draft-screen-markdown`, then
  `draft-screen-excalidraw`, then `render-excalidraw`, in that order, for
  each screen requested.
- `draft-screen-excalidraw` produces `.excalidraw` scene files but doesn't
  render them to an image itself; it hands off to `render-excalidraw` for
  that (either directly, or via `draft-screen`).
- `draft-screen-markdown` and `draft-screen-excalidraw` are usable
  independently of each other and of `draft-screen`, if only one artifact
  is wanted.

Because of this, **all four skills are bundled into a single plugin** and
should be installed together — installing a subset (e.g. only
`draft-screen`) leaves its references to the others unresolved, and Claude
would have to improvise a worse version of what they'd actually do.

### Design stance: agnostic on purpose

These skills don't assume any particular product domain, design system, or
brand. Wireframes stay on a neutral grayscale palette with semantic tones
reserved for state (success/warning/danger/info), not brand color; example
content in the skill instructions is generic and meant to be replaced with
whatever's realistic for the product being worked on. The goal is a skill
set that works the same way on any project, not one tuned to a specific
app.

## Plugin: data-model-diagram

| Skill | Produces | Triggers on |
|---|---|---|
| [`data-model-diagram`](plugins/data-model-diagram/skills/data-model-diagram) | A Mermaid `erDiagram` (rendered inline, or exported as `.mmd`/`.md`) built up conversationally, in simplified or detailed form | "design/model the data model", "ER diagram", "entity-relationship diagram", "schema diagram", requests to add to or evolve a data model already under discussion |

Independent of the screen-drafting skills — no cross-references either way.
Works iteratively: proposes entities/relationships in prose for confirmation
before rendering, slices large domains into confirmed layers, and defaults
to a simplified (attribute-free) diagram unless a detailed one is requested.
See its `SKILL.md` for the modeling conventions it surfaces (pivot entities,
catalog-vs-enum, derived vs. stored fields, etc.) and
`references/worked-example.md` for a full walkthrough on a sample domain.

## Repo structure: one subdirectory per plugin

Each plugin lives in its own directory under `plugins/`, with its own
`.claude-plugin/plugin.json` and its own `skills/`:

```
plugins/
├── screen-drafting/
│   ├── .claude-plugin/plugin.json
│   └── skills/draft-screen/, draft-screen-markdown/, draft-screen-excalidraw/, render-excalidraw/
└── data-model-diagram/
    ├── .claude-plugin/plugin.json
    └── skills/data-model-diagram/
```

The root `.claude-plugin/marketplace.json` just lists each plugin with a
`source` pointing at its own directory — no two plugins share a `source`.

This wasn't the first layout tried. An earlier version kept a single flat
`skills/` directory at the repo root shared by every plugin, with each
marketplace entry declaring its own subset via a `skills: [...]` field
(`source: "./"`, `strict: false`) — the schema explicitly supports this, and
it has the advantage of staying compatible with tools that expect a plain
`skills/<name>/SKILL.md` convention beyond Claude Code (skills.sh's default
scan, Codex CLI, Gemini CLI, Copilot CLI). In practice, though, claude.ai's
plugin sync didn't respect that per-entry scoping — every plugin installed
from it showed *all* skills from the shared folder, not just its own. The
per-plugin-directory layout here doesn't depend on that scoping being
correctly honored: a plugin's boundary is which directory `source` points
to, which every surface has to get right for plugins to work at all.

The trade-off: skills.sh still resolves each skill correctly (it explicitly
parses `.claude-plugin/marketplace.json`/`plugin.json` and follows a
plugin's declared `source`, at any depth), but tools with no notion of a
Claude plugin manifest — Codex CLI, Gemini CLI, Copilot CLI — won't find
these skills via their own flat-`skills/`-at-root convention. That's an
accepted cost for now, in exchange for `claude.ai` actually working
correctly.

Adding a future, unrelated skill group means adding a new `plugins/<name>/`
directory with its own `plugin.json` and `skills/`, plus one new entry in
`marketplace.json` — no changes to existing plugins required.

## Installing

### Claude Code

```
/plugin marketplace add cyrilchapon/skills
/plugin install screen-drafting
/plugin install data-model-diagram
```

### claude.ai

Customize (sidebar) → Plugins → **+** (Personal plugins) → **Add
marketplace** → point it at `https://github.com/cyrilchapon/skills` →
Browse plugins → Install.

Note: claude.ai, Claude Code, and the API each maintain independent
skill/plugin state — installing here on one surface doesn't install it on
the others.

## `render-excalidraw` and Node

`render-excalidraw` renders scenes with Excalidraw's own `exportToSvg`,
running headlessly under Node/JSDOM. Its `node_modules/` is committed
(vendored) rather than installed on demand, because some surfaces that can
run a skill don't guarantee network access at execution time — vendoring
keeps the skill portable across Claude Code, claude.ai, and anywhere else a
skill might run. See that skill's `SKILL.md` for details.

## License

MIT — see [LICENSE](LICENSE).
