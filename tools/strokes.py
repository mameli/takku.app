"""Generates the hand-drawn strokes of the page as SVG data URIs and writes them into style.css,
between the `strokes:start` and `strokes:end` comments.

Lines are tiles that repeat without seams: their wobble is a sum of sines with the tile's
length as period. Masks are black (the colour comes from CSS); the strokes used as backgrounds
of text, which a mask would hide, come in a light and a dark version.

    python3 tools/strokes.py
"""
import math
import random
import re
from pathlib import Path

random.seed(5)
CSS = Path(__file__).resolve().parent.parent / "style.css"


def uri(svg):
    svg = svg.replace("%", "%25").replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "'")
    return f'url("data:image/svg+xml,{svg}")'


def svg(width, height, body, extra=""):
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'{extra}>{body}</svg>"


def stroke(d, width, color="black"):
    return f"<path d='{d}' fill='none' stroke='{color}' stroke-width='{width}' stroke-linecap='round' stroke-linejoin='round'/>"


def periodic(length, amp):
    """A wobble that ends where it starts: sines whose periods divide the length."""
    waves = [(k, amp * a, random.uniform(0, 2 * math.pi)) for k, a in ((1, 0.55), (2, 0.3), (3, 0.2), (5, 0.12), (8, 0.06))]
    return lambda t: sum(a * math.sin(2 * math.pi * k * t / length + p) for k, a, p in waves)


def line(length, across, amp, vertical=False, step=4):
    off = periodic(length, amp)
    points = []
    for i in range(0, length + step, step):
        t = min(i, length)
        a = across + off(t)
        points.append((a, t) if vertical else (t, a))
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in points)


def loop(cx, cy, r, turn=1.08, wobble=0.06, step=6):
    """A circle drawn in one go: it starts somewhere top left and goes a little past its start."""
    start = random.uniform(-2.4, -1.7)
    phases = [random.uniform(0, 2 * math.pi) for _ in range(3)]
    points = []
    steps = int(360 * turn / step)
    for i in range(steps + 1):
        f = i / steps
        a = start + 2 * math.pi * turn * f
        rr = r * (1 + wobble * math.sin(2 * a + phases[0]) + wobble * 0.5 * math.sin(3 * a + phases[1])) + r * 0.08 * f
        points.append((cx + rr * math.cos(a), cy + rr * 0.96 * math.sin(a)))
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in points)


def ticks(length, vertical=False):
    """A ruler: a long tick, then short ones every 12px, none quite the same."""
    parts = []
    for i, x in enumerate(range(0, length, 12)):
        size = random.uniform(11, 13) if i == 0 else random.uniform(4.5, 7)
        lean = random.uniform(-0.7, 0.7)
        x += random.uniform(-0.6, 0.6) + 1
        parts.append(f"M{0.5:.1f} {x:.2f}L{size:.2f} {x + lean:.2f}" if vertical else f"M{x:.2f} 0.5L{x + lean:.2f} {size:.2f}")
    return "".join(parts)


def marker(width, height, top, bottom, step=5):
    """A highlighter stroke with uneven edges."""
    up, down = periodic(width, 1.6), periodic(width, 1.6)
    edge_top = [(x, top + up(x)) for x in range(0, width + step, step)]
    edge_bottom = [(x, bottom + down(x)) for x in range(width, -step, -step)]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in edge_top + edge_bottom) + "Z"


masks = {
    # Long lines: frame, boxes, table rules
    "h": svg(240, 6, stroke(line(240, 3, 1.2), 1.7)),
    "h2": svg(240, 6, stroke(line(240, 3, 1.2), 1.7)),
    "v": svg(6, 240, stroke(line(240, 3, 1.2, vertical=True), 1.7)),
    "v2": svg(6, 240, stroke(line(240, 3, 1.2, vertical=True), 1.7)),
    # The double red margin
    "rule": svg(10, 360, stroke(line(360, 2.5, 0.7, vertical=True), 1.5) + stroke(line(360, 7.2, 0.7, vertical=True), 1.5)),
    # Rulers
    "ruler-h": svg(60, 14, stroke(ticks(60), 1.2)),
    "ruler-v": svg(14, 60, stroke(ticks(60, vertical=True), 1.2)),
    # Holes in the corners
    "hole": svg(28, 28, stroke(loop(14, 14, 11, turn=1.06, wobble=0.04), 1.5) + stroke(loop(14, 14, 5.5, turn=1.1, wobble=0.05), 1.3)),
    # A dash for the lists
    "dash": svg(18, 8, stroke("M2.5 5c3.5-1.6 8-1.9 13-0.9", 2)),
}
# Circles around the step numbers, one per step
for n in range(1, 5):
    masks[f"circle-{n}"] = svg(56, 56, stroke(loop(28, 28, 22, turn=random.uniform(1.06, 1.14)), 2.3))

colours = {
    "light": {"pencil": "#3f58ae", "red": "#c23b2e", "mark": ("#ffd632", 0.55)},
    "dark": {"pencil": "#a9c2ff", "red": "#ff9a8c", "mark": ("#ffd632", 0.3)},
}
underline = line(160, 2.5, 0.6)
highlight = marker(200, 24, 4, 21)


def coloured(scheme):
    c = colours[scheme]
    mark, opacity = c["mark"]
    return {
        "u-link": svg(160, 5, stroke(underline, 1.4, c["pencil"])),
        "u-link-hover": svg(160, 5, stroke(underline, 1.4, c["red"])),
        "u-mark": svg(200, 24, f"<path d='{highlight}' fill='{mark}' fill-opacity='{opacity}'/>", " preserveAspectRatio='none'"),
    }


def props(values, indent):
    return "\n".join(f"{indent}--{name}: {uri(value)};" for name, value in values.items())


block = f"""/* strokes:start (generated by tools/strokes.py) */
:root {{
{props(masks, "  ")}
{props(coloured("light"), "  ")}
}}
@media (prefers-color-scheme: dark) {{
  :root {{
{props(coloured("dark"), "    ")}
  }}
}}
/* strokes:end */"""

css = CSS.read_text()
css, count = re.subn(r"/\* strokes:start.*?/\* strokes:end \*/", lambda _: block, css, flags=re.S)
assert count == 1, "markers not found in style.css"
CSS.write_text(css)
print(f"{len(block) // 1024} KB of strokes written to {CSS.name}")
