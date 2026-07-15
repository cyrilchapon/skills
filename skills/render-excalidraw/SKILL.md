---
name: render-excalidraw
description: Renders .excalidraw scene files into standalone .svg images using Excalidraw's own rendering engine (not a reinterpretation), running headlessly in Node — no browser, no CDN, works anywhere. Use this whenever the user has one or more .excalidraw files and wants to view, preview, share, embed, or convert them — e.g. "show me this wireframe", "what does this .excalidraw look like", "turn these into images", "attach the wireframe as an SVG", "I can't open .excalidraw files, can you show me what's in them". Also use proactively any time an .excalidraw file is uploaded or referenced and the user would benefit from actually seeing it rendered rather than just reading the raw JSON.
---

# Render Excalidraw

## Why this exists

`.excalidraw` files are JSON scene descriptions (elements + appState), not
images. There's no reliable way to preview them live in a sandboxed browser
artifact: current Excalidraw releases only ship an ESM bundle (the old
`<script src=...>` UMD build was dropped), which means rendering it live
needs an import-map-based ESM load from a CDN — and sandboxed artifact
environments typically only allow a narrow CDN allowlist that doesn't
include the CDNs (e.g. esm.sh) that this approach depends on. That path is
fragile and environment-dependent.

The reliable alternative: render the scene to a static SVG **once**, using
Excalidraw's actual export function (`exportToSvg` from `@excalidraw/utils`)
running headlessly in Node via JSDOM shims. This is the same function the
real Excalidraw app calls internally to export a scene, so the output is a
faithful rendering (correct shapes, positions, hand-drawn stroke style via
rough.js, colors, text) — not a guess or a reimplementation. The result is a
plain static SVG file with zero runtime dependencies: it can be viewed as an
image, embedded in a document, pasted mid-conversation, or opened directly
in a browser, with no CDN, no CSP concerns, and no build step.

## How to use this

1. Node dependencies are vendored in this skill's `node_modules/` — no
   `npm install` needed at runtime (see "Why dependencies are vendored"
   below). If `node_modules/` is ever missing (e.g. after a fresh checkout
   that excluded it), install once per session:
   ```bash
   cd <this skill's folder>
   npm install
   ```
   (Installs `@excalidraw/utils` and `jsdom` — small, no native
   compilation needed. If the pinned version in `package.json` ever fails
   to resolve, retry with `npm install @excalidraw/utils@latest jsdom@latest`.)

2. Run the bundled script on one or more input files:
   ```bash
   node scripts/render.mjs path/to/file1.excalidraw path/to/file2.excalidraw --outdir /path/to/output
   ```
   - Accepts any number of `.excalidraw` input paths (globs work if your
     shell expands them, e.g. `*.excalidraw`).
   - `--outdir <dir>` is optional — omit it to write each `.svg` next to its
     source file (same basename, `.svg` extension).
   - `--scale <n>` controls export resolution (default `2`, good for
     crisp viewing at typical zoom levels; bump it for large/detailed
     scenes you'll zoom into).
   - `--dark` exports using Excalidraw's dark mode color transform instead
     of the scene's stored background/colors.

3. Do something useful with the resulting `.svg` file(s) depending on
   context:
   - **Mid-conversation, no artifact needed**: just reference/attach the
     `.svg` file directly — it's a normal static image at that point.
   - **Multiple screens to browse**: consider building a simple static
     HTML page that inlines the SVGs with a `<select>` to switch between
     them (pure inline SVG + vanilla JS, no external script/style tags
     needed — this avoids any CDN/CSP problems entirely). Only do this if
     the user actually wants a single browsable artifact; for a single
     file or a quick look, the raw `.svg` is simpler and just as good.
   - **Needs a raster format** (PNG/JPEG) instead: convert the SVG with
     whatever's available in the environment (e.g. Python's `cairosvg`,
     or `rsvg-convert` if installed) rather than re-rendering from
     scratch.

## Why dependencies are vendored

`node_modules/` for this skill is committed alongside it rather than
installed on demand. Claude Code always has local Node/npm available, but
other surfaces that can run a skill (e.g. an uploaded skill or plugin on
claude.ai) run in a sandbox where network access at execution time isn't
guaranteed — an `npm install` there can simply fail. Vendoring removes that
dependency entirely and keeps this skill portable across every surface it
might run on.

## Known limitation: hand-drawn font

Excalidraw's signature hand-drawn look comes partly from its custom font
("Excalifont", formerly "Virgil"), loaded over the network in a real
browser. There's no network font loading in this headless setup, so
`FontFace` is stubbed out and text falls back to a generic system font.
Shapes, positions, colors, stroke style (rough.js hand-drawn strokes), and
layout are all rendered exactly as Excalidraw would — only the text
typeface differs slightly from what you'd see in the actual app. This is
a cosmetic difference, not a fidelity problem with the diagram itself.
If exact font fidelity ever matters, that would require bundling the
actual font file and registering it with the JSDOM environment — not
currently set up here since it hasn't been needed.

## Troubleshooting

- **`ReferenceError` for some browser global**: a future Excalidraw release
  may touch a browser API not yet stubbed in `scripts/render.mjs`
  (`installBrowserShims`). The error message names the missing global —
  add a minimal stub for it following the pattern already there (most of
  these are simple no-op stubs; the export code only feature-detects them,
  it doesn't need real behavior for a static SVG export).
- **A scene has embedded images** (`files` object non-empty, e.g. pasted
  screenshots): these are passed through to `exportToSvg` automatically
  and should render as long as the referenced file data is present in the
  source `.excalidraw` file's `files` field. If an image element renders
  as blank, check whether `files` was actually populated in the source.
- **Output looks empty / wrong size**: check that the input file's
  `elements` array isn't empty and that `appState.viewBackgroundColor` is
  set — `exportBackground: true` is hardcoded in the script so scenes
  always export with their background rather than transparent.
