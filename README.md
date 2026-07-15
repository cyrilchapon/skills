# Skills

Personal collection of [Claude](https://claude.com) skills, versioned here
instead of living only inside claude.ai's skill editor.

Skills are grouped into plugins when they form a coherent workflow. The
first group, **screen-drafting**, bundles four skills for taking an app/
product screen from a design discussion to a documented, wireframed,
viewable deliverable. More skills/plugins will be added over time.

## Plugin: screen-drafting

| Skill | Produces | Triggers on |
|---|---|---|
| [`draft-screen`](skills/draft-screen) | The full package below, for one or more screens | "draft/design/spec out a screen", requests for a screen end-to-end rather than one artifact of it |
| [`draft-screen-markdown`](skills/draft-screen-markdown) | A structured `.md` doc (purpose, entities, states, actions, relations, open questions) | "document/spec out this screen", "write up what we designed" |
| [`draft-screen-excalidraw`](skills/draft-screen-excalidraw) | One or more `.excalidraw` wireframes, contextualized with realistic content | "mock up/wireframe/prototype/sketch this screen" |
| [`render-excalidraw`](skills/render-excalidraw) | Standalone `.svg` renders of `.excalidraw` files | Any time an `.excalidraw` file needs to be viewed, shared, or embedded |

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

## Repo structure: one flat `skills/`, multiple plugins

All skills live directly under the top-level `skills/` directory, regardless
of which plugin they belong to — there's no per-plugin subfolder. This is
deliberate: a flat `skills/<name>/SKILL.md` layout is the convention several
tools beyond Claude Code rely on for discovery (skills.sh's default scan,
Codex CLI, Gemini CLI, Copilot CLI), so keeping it flat means this repo stays
usable outside the Claude plugin ecosystem too, not just inside it.

Plugin boundaries are expressed purely in `.claude-plugin/marketplace.json`:
each plugin entry sets `"source": "./"` (the shared repo root) and lists the
specific skill directories that belong to it via `"skills": [...]`. Because
several plugins can share one `source`, none of them can rely on a top-level
`.claude-plugin/plugin.json` for identity — that's why each entry sets
`"strict": false` and carries its own metadata (`version`, `author`,
`license`, `keywords`...) directly in the marketplace entry instead.

Adding a future, unrelated skill group means adding its skill directories
under `skills/` and a new entry to the `plugins` array listing them — no
restructuring of existing plugins required.

## Installing

### Claude Code

```
/plugin marketplace add cyrilchapon/skills
/plugin install screen-drafting
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
