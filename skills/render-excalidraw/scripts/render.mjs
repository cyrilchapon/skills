#!/usr/bin/env node
/**
 * Renders one or more .excalidraw scene files to standalone .svg files,
 * using the real Excalidraw rendering engine (@excalidraw/utils' exportToSvg)
 * running headlessly under JSDOM. No browser, no CDN, no network at render time.
 *
 * Usage:
 *   node render.mjs <file1.excalidraw> [file2.excalidraw ...] [--outdir <dir>] [--scale <n>] [--dark]
 *
 * By default each output SVG is written next to its input file, same
 * basename, .svg extension. Pass --outdir to write everything to one
 * folder instead (basenames are kept, so name collisions across input
 * directories will overwrite each other).
 */

import { JSDOM } from "jsdom";
import { readFile, writeFile, mkdir } from "fs/promises";
import path from "path";

function parseArgs(argv) {
  const inputs = [];
  let outdir = null;
  let scale = 2;
  let dark = false;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--outdir") { outdir = argv[++i]; }
    else if (a === "--scale") { scale = Number(argv[++i]) || 2; }
    else if (a === "--dark") { dark = true; }
    else { inputs.push(a); }
  }
  return { inputs, outdir, scale, dark };
}

// exportToSvg (and the font-metrics code it calls internally) expects a
// browser environment. JSDOM covers the DOM shape, but a handful of globals
// it doesn't implement have to be stubbed by hand. None of this touches
// rendering fidelity — it only satisfies feature-detection checks the
// library runs before it gets to the actual drawing.
function installBrowserShims() {
  const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>", { pretendToBeVisual: true });
  global.window = dom.window;
  global.document = dom.window.document;
  Object.defineProperty(global, "navigator", { value: dom.window.navigator, configurable: true });
  global.HTMLElement = dom.window.HTMLElement;
  global.SVGElement = dom.window.SVGElement;
  global.Element = dom.window.Element;
  global.getComputedStyle = dom.window.getComputedStyle;
  global.devicePixelRatio = 1;
  global.location = dom.window.location;
  global.requestAnimationFrame = (cb) => setTimeout(cb, 0);
  global.cancelAnimationFrame = (id) => clearTimeout(id);
  global.Image = dom.window.Image;
  global.CSS = dom.window.CSS || { supports: () => false };
  global.matchMedia = dom.window.matchMedia || (() => ({
    matches: false, addListener() {}, removeListener() {},
  }));

  // Real font loading (Excalifont / Virgil, the hand-drawn font) needs a
  // browser network stack we don't have here. Stub FontFace so Excalidraw's
  // font-face CSS generation doesn't throw; text still renders correctly,
  // just in a system font instead of the hand-drawn one.
  class FontFaceStub {
    constructor(family, source, descriptors) {
      this.family = family;
      this.source = source;
      this.descriptors = descriptors || {};
      this.unicodeRange = this.descriptors.unicodeRange || "U+0-10FFFF";
      this.status = "unloaded";
    }
    load() { this.status = "loaded"; return Promise.resolve(this); }
  }
  global.FontFace = FontFaceStub;
  dom.window.document.fonts = dom.window.document.fonts || {
    add() {}, forEach() {}, ready: Promise.resolve(),
  };
}

async function renderOne(inputPath, { outdir, scale, dark }, exportToSvg) {
  const raw = JSON.parse(await readFile(inputPath, "utf-8"));
  if (raw.type !== "excalidraw") {
    throw new Error(`${inputPath} does not look like an .excalidraw scene (missing "type": "excalidraw")`);
  }

  const svg = await exportToSvg({
    elements: raw.elements || [],
    appState: {
      ...(raw.appState || {}),
      exportBackground: true,
      exportWithDarkMode: dark,
      exportScale: scale,
    },
    files: raw.files || null,
  });

  const base = path.basename(inputPath, path.extname(inputPath));
  const dir = outdir || path.dirname(inputPath);
  await mkdir(dir, { recursive: true });
  const outPath = path.join(dir, `${base}.svg`);
  await writeFile(outPath, svg.outerHTML, "utf-8");
  return outPath;
}

async function main() {
  const { inputs, outdir, scale, dark } = parseArgs(process.argv.slice(2));
  if (inputs.length === 0) {
    console.error("Usage: node render.mjs <file1.excalidraw> [file2.excalidraw ...] [--outdir <dir>] [--scale <n>] [--dark]");
    process.exit(1);
  }

  installBrowserShims();
  // Import after shims are installed — the module reads some globals at
  // import time.
  const { exportToSvg } = await import("@excalidraw/utils");

  const results = [];
  for (const input of inputs) {
    try {
      const outPath = await renderOne(input, { outdir, scale, dark }, exportToSvg);
      results.push({ input, outPath, ok: true });
      console.log(`OK   ${input} -> ${outPath}`);
    } catch (err) {
      results.push({ input, error: err.message, ok: false });
      console.error(`FAIL ${input}: ${err.message}`);
    }
  }

  const failed = results.filter((r) => !r.ok);
  if (failed.length > 0) {
    process.exitCode = 1;
  }
}

main();
