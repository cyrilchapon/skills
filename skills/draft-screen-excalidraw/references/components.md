# Component vocabulary — `excalidraw_builder.py`

Import once per screen:

```python
import sys
sys.path.insert(0, "<path to this skill's scripts/ folder>")
from excalidraw_builder import Scene, PALETTE

s = Scene(width=360, height=780)   # standard mobile viewport; adjust if needed
```

Build top-to-bottom, left-to-right, tracking a `y` cursor yourself as you go
(the library doesn't do auto-layout — that's deliberate, it keeps you in
control of spacing decisions the way you would sketching by hand).

## Frame & structure

- `s.phone_frame(x=0, y=0, w=None, h=None)` — outer device outline. Defaults
  to the scene's full width/height. Purely a layout aid for the reader —
  the real app shell isn't this skill's concern.
- `s.divider(x, y, w=None, color=PALETTE["border"])` — thin horizontal rule.
  Use between sections instead of guessing whitespace.
- `s.card(x, y, w, h, fill=PALETTE["surface"])` — a filled rounded panel to
  group related content (a summary card, a stat block, etc.)

## Text

- `s.text(x, y, text, size=12, color=PALETTE["ink"], align="left")` —
  freeform label. Width auto-estimates from length × size; pass `width=`
  explicitly only if you need to override for alignment/wrapping reasons.
- Sizes used consistently across reference screens: `18` page title, `16`
  greeting/emphasis line, `12` body/row title, `10` metadata/subtitle,
  `9` nav labels / tiny badges.
- For icon-ish marks, use a plain unicode glyph in a `text` element (▾ ✓ ✕
  🔔 etc.) rather than inventing an icon shape — this stays graphically
  unopinionated and legible at wireframe fidelity.

## Status & category

- `s.badge(x, y, label, tone="surface")` — small pill. `tone` ∈ `surface`
  (neutral gray, default), `success`, `warning`, `danger`, `info`. Tie tone
  to what the label *means* (confirmed → success, pending → warning,
  declined/error → danger), never to decoration.
- `s.avatar(x, y, initials, diameter=44, tone="info")` — initials circle for
  a person. Same tone vocabulary as badges.

## Rows & lists

- `s.list_row(x, y, w, title, subtitle=None)` — one row's text (title +
  optional muted subtitle below it). Returns the y-coordinates used, so you
  can place a trailing badge/control at a matching height. Repeat with an
  incrementing `y` for a list; add a `s.divider(...)` between rows if the
  design calls for separated (not just spaced) rows.

## Controls

- `s.button(x, y, w, label, tone="surface_alt")` — outlined button.
- `s.input_field(x, y, w, placeholder)` — text input with placeholder.

## Navigation chrome

- `s.top_bar(x, y, w, title=None, left_label=None, right_glyph=None)` —
  header row. Any of the three parts can be omitted.
- `s.bottom_nav(items, active_index=0)` — `items` is a list of
  `(label, glyph_or_None)` tuples; draws a divider + evenly spaced labels,
  active one in ink, rest muted.

## Saving

```python
s.save("screen-name.excalidraw")
```

Writes valid `.excalidraw` JSON (schema: `type`, `version`, `source`,
`elements`, `appState`, `files`) — nothing further to wrap it in.

## When something isn't covered

Add a small function to `excalidraw_builder.py` following the existing
pattern (build the element dict(s), append to `self.elements`, return an id
or group id) rather than hand-writing raw element dicts inline — keeping
everything going through the builder is what keeps every generated screen
visually consistent with the others.
