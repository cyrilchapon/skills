#!/usr/bin/env python3
"""
excalidraw_builder.py — small helper library for constructing valid
.excalidraw scene files programmatically instead of hand-writing JSON.

Why this exists: .excalidraw files are JSON, and every element needs a
consistent set of ~20 fields (seed, versionNonce, roundness object shape,
etc.) to be valid. Hand-crafting this by prose/JSON-in-context is slow and
error-prone — coordinates drift, text overlaps its container, roundness
objects get malformed. This module wraps that boilerplate behind small,
composable functions so a screen can be built the same way you'd sketch it:
frame, then rows of content, then chrome (top bar / bottom nav).

Not a general-purpose Excalidraw SDK — just the vocabulary needed for
mobile-first app screen wireframes: frames, text, dividers, badges/pills,
cards, list rows, top bars, bottom navs, buttons, inputs, avatars, and a
couple of icon-ish glyphs. Extend it in place if a screen needs a shape
that isn't here yet; the pattern is the same for every element type.

Usage:
    from excalidraw_builder import Scene, PALETTE

    s = Scene()
    s.phone_frame()
    s.text(16, 20, "My screen", size=18)
    s.divider(0, 60)
    s.save("my-screen.excalidraw")
"""

import json
import random
import time


# ---------------------------------------------------------------------------
# Semantic palette. Keep UI chrome neutral/grayscale (unopinionated on brand)
# and reserve color for STATE, not decoration. Pick colors by meaning
# (confirmed/pending/error/info), not by "looks nice here".
# ---------------------------------------------------------------------------
PALETTE = {
    "ink": "#1e1e1e",          # primary stroke / primary text
    "label": "#5f5e5a",        # secondary text (section labels)
    "muted": "#8a8880",        # tertiary text (hints, metadata)
    "border": "#e0dfd8",       # divider lines
    "surface": "#F1EFE8",      # neutral card / pill background
    "surface_alt": "#ffffff",  # elevated surface (selected pill, sheet)
    "success_bg": "#EAF3DE", "success_text": "#173404",   # confirmed / done
    "warning_bg": "#FAEEDA", "warning_text": "#412402",   # pending / collecting
    "danger_bg": "#FCEBEB", "danger_text": "#501313",     # error / declined
    "info_bg": "#E6F1FB", "info_text": "#042C53",         # informational
}

FONT_FAMILY = 1  # Excalidraw's handwritten font (Virgil/Excalifont)


def _id():
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16))


def _seed():
    return random.randint(1, 2 ** 31 - 1)


def _now_ms():
    return int(time.time() * 1000)


def _text_width(text, size):
    """Rough proportional-font width estimate: good enough to size
    containers and avoid overlap. Not pixel-accurate — Excalidraw's actual
    font metrics differ per character — but consistent enough to lay out a
    screen without elements colliding."""
    return round(len(text) * size * 0.56, 2)


class Scene:
    def __init__(self, width=360, height=780, background="#ffffff"):
        self.elements = []
        self.width = width
        self.height = height
        self.background = background

    # -- low-level primitives -------------------------------------------------

    def rect(self, x, y, w, h, stroke=PALETTE["ink"], fill="transparent",
             fill_style="solid", stroke_width=1, roughness=1.4, rounded=True,
             opacity=100, group_id=None):
        el = {
            "id": _id(), "type": "rectangle", "x": x, "y": y,
            "width": w, "height": h, "angle": 0,
            "strokeColor": stroke, "backgroundColor": fill,
            "fillStyle": fill_style, "strokeWidth": stroke_width,
            "strokeStyle": "solid", "roughness": roughness, "opacity": opacity,
            "groupIds": [group_id] if group_id else [], "frameId": None,
            "roundness": {"type": 3} if rounded else None,
            "seed": _seed(), "version": 1, "versionNonce": _seed(),
            "isDeleted": False, "boundElements": None, "updated": _now_ms(),
            "link": None, "locked": False,
        }
        self.elements.append(el)
        return el["id"]

    def ellipse(self, x, y, w, h, stroke=PALETTE["ink"], fill="transparent",
                fill_style="solid", stroke_width=1, roughness=1.4, opacity=100,
                group_id=None):
        el = {
            "id": _id(), "type": "ellipse", "x": x, "y": y,
            "width": w, "height": h, "angle": 0,
            "strokeColor": stroke, "backgroundColor": fill,
            "fillStyle": fill_style, "strokeWidth": stroke_width,
            "strokeStyle": "solid", "roughness": roughness, "opacity": opacity,
            "groupIds": [group_id] if group_id else [], "frameId": None,
            "roundness": None,
            "seed": _seed(), "version": 1, "versionNonce": _seed(),
            "isDeleted": False, "boundElements": None, "updated": _now_ms(),
            "link": None, "locked": False,
        }
        self.elements.append(el)
        return el["id"]

    def text(self, x, y, text, size=12, color=PALETTE["ink"], align="left",
              width=None, opacity=100, group_id=None):
        w = width if width is not None else _text_width(text, size)
        h = round(size * 1.25, 2)
        el = {
            "id": _id(), "type": "text", "x": x, "y": y,
            "width": w, "height": h, "angle": 0,
            "strokeColor": color, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 1.4, "opacity": opacity,
            "groupIds": [group_id] if group_id else [], "frameId": None,
            "roundness": None, "seed": _seed(), "version": 1,
            "versionNonce": _seed(), "isDeleted": False, "boundElements": None,
            "updated": _now_ms(), "link": None, "locked": False,
            "text": text, "fontSize": size, "fontFamily": FONT_FAMILY,
            "textAlign": align, "verticalAlign": "top", "baseline": size,
            "containerId": None, "originalText": text, "lineHeight": 1.25,
        }
        self.elements.append(el)
        return el["id"]

    def divider(self, x, y, w=None, color=PALETTE["border"]):
        w = w if w is not None else self.width
        return self.rect(x, y, w, 1, stroke=color, fill=color, roughness=0,
                          rounded=True)

    # -- composed components --------------------------------------------------

    def phone_frame(self, x=0, y=0, w=None, h=None):
        """Outer device outline. Purely a layout aid for the viewer — the
        implementing team's real shell/nav chrome will replace it."""
        w = w if w is not None else self.width
        h = h if h is not None else self.height
        return self.rect(x, y, w, h, rounded=True, roughness=1.6)

    def top_bar(self, x, y, w, title=None, left_label=None, right_glyph=None,
                height=40):
        """A header row: optional left label/back-affordance, optional
        title, optional single glyph on the right (bell, kebab, etc. — use
        a plain unicode glyph, not an icon asset)."""
        group = _id()
        ids = []
        if left_label:
            ids.append(self.text(x + 8, y + (height - 15) / 2, left_label,
                                  size=12, group_id=group))
        if title:
            ids.append(self.text(x + 8, y - 34, title, size=18, group_id=group))
        if right_glyph:
            ids.append(self.text(x + w - 30, y + (height - 17.5) / 2,
                                  right_glyph, size=14, group_id=group))
        return ids

    def badge(self, x, y, label, tone="surface", height=18, group_id=None):
        """Small pill used for status/category tags. tone is one of:
        surface (neutral), success, warning, danger, info."""
        bg = PALETTE.get(f"{tone}_bg", PALETTE["surface"]) if tone != "surface" else PALETTE["surface"]
        fg = PALETTE.get(f"{tone}_text", PALETTE["label"]) if tone != "surface" else PALETTE["label"]
        w = _text_width(label, 10) + 16
        group = group_id or _id()
        self.rect(x, y, w, height, stroke=bg, fill=bg, rounded=True,
                   roughness=0.6, group_id=group)
        self.text(x + 8, y + (height - 12.5) / 2, label, size=10, color=fg,
                   group_id=group)
        return group

    def avatar(self, x, y, initials, diameter=44, tone="info"):
        bg = PALETTE.get(f"{tone}_bg", PALETTE["surface"])
        fg = PALETTE.get(f"{tone}_text", PALETTE["ink"])
        group = _id()
        self.ellipse(x, y, diameter, diameter, stroke=bg, fill=bg,
                      roughness=0.6, group_id=group)
        tw = _text_width(initials, 14)
        self.text(x + (diameter - tw) / 2, y + (diameter - 17.5) / 2,
                   initials, size=14, color=fg, group_id=group)
        return group

    def card(self, x, y, w, h, fill=PALETTE["surface"], rounded=True):
        return self.rect(x, y, w, h, stroke=fill, fill=fill, roughness=0.5,
                          rounded=rounded)

    def button(self, x, y, w, label, tone="surface_alt", height=36):
        bg = PALETTE.get(f"{tone}_bg", PALETTE.get(tone, PALETTE["surface_alt"]))
        group = _id()
        self.rect(x, y, w, height, stroke=PALETTE["ink"], fill=bg,
                   roughness=0.6, group_id=group)
        tw = _text_width(label, 12)
        self.text(x + (w - tw) / 2, y + (height - 15) / 2, label, size=12,
                   group_id=group)
        return group

    def input_field(self, x, y, w, placeholder, height=36):
        group = _id()
        self.rect(x, y, w, height, stroke=PALETTE["border"],
                   fill=PALETTE["surface_alt"], roughness=0.6, group_id=group)
        self.text(x + 10, y + (height - 15) / 2, placeholder, size=12,
                   color=PALETTE["muted"], group_id=group)
        return group

    def list_row(self, x, y, w, title, subtitle=None, trailing=None,
                  title_size=12, subtitle_size=10):
        """One row of a list: title, optional muted subtitle below it,
        optional trailing element (badge id / short text) already placed —
        this just returns the y each line was drawn at so callers can place
        their own trailing badge/control at a matching y."""
        group = _id()
        self.text(x, y, title, size=title_size, group_id=group)
        if subtitle:
            self.text(x, y + title_size + 4, subtitle, size=subtitle_size,
                       color=PALETTE["muted"], group_id=group)
        return {"group": group, "title_y": y,
                "subtitle_y": y + title_size + 4 if subtitle else None}

    def bottom_nav(self, items, active_index=0, x=0, y=None, w=None,
                    height=52):
        """items: list of (label, glyph_or_none) tuples. Draws a divider
        above the bar and evenly-spaced labels; the active item is drawn in
        ink, the rest in muted."""
        y = y if y is not None else self.height - height
        w = w if w is not None else self.width
        self.divider(x, y)
        n = len(items)
        slot = w / n
        for i, (label, _glyph) in enumerate(items):
            color = PALETTE["ink"] if i == active_index else PALETTE["muted"]
            tw = _text_width(label, 9)
            cx = x + slot * i + (slot - tw) / 2
            self.text(cx, y + height / 2 - 5.6, label, size=9, color=color)
        return None

    # -- output ----------------------------------------------------------------

    def to_dict(self):
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {
                "gridSize": None,
                "viewBackgroundColor": self.background,
            },
            "files": {},
        }

    def save(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False)
        return path


if __name__ == "__main__":
    # Minimal smoke test / usage example.
    s = Scene()
    s.phone_frame()
    s.text(8, 10, "Example screen", size=16)
    s.divider(8, 40)
    s.badge(8, 56, "Confirmed", tone="success")
    s.badge(70, 56, "Pending", tone="warning")
    s.bottom_nav([("Home", None), ("Activity", None), ("Profile", None)],
                  active_index=0)
    s.save("/tmp/excalidraw_builder_smoketest.excalidraw")
    print("wrote /tmp/excalidraw_builder_smoketest.excalidraw with",
          len(s.elements), "elements")
