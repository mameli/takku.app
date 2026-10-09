"""Draws public/og.png, the 1200×630 preview shown when takku.app is shared, with Google Chrome:
the same sheet, title and drawing as the page.

    python3 tools/og.py
"""
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

drawing = re.search(r"<svg viewBox.*?</svg>", (PUBLIC / "index.html").read_text(), re.S).group(0)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="{(PUBLIC / 'style.css').as_uri()}">
<style>
  :root {{ --pad: 40px; --margin: 64px; --gutter: 36px; }}
  html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: var(--paper); }}
  .sheet {{ width: 1200px; height: 630px; max-width: none; margin: 0; padding: 0; }}
  .frame {{ inset: 14px; }}
  .ruler-top {{ top: 24px; left: 60px; right: 60px; }}
  .ruler-left {{ top: 60px; bottom: 60px; left: 24px; }}
  .og {{
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 420px;
    gap: 40px;
    align-items: center;
    height: 100%;
    padding: 40px 72px 40px calc(var(--pad) + var(--margin) + var(--gutter));
  }}
  h1 {{ font-size: 8.5rem; margin-bottom: 28px; }}
  h1 img {{ width: 128px; height: 128px; }}
  .lead {{ font-size: 2.125rem; line-height: 48px; max-width: none; margin: 0 0 28px; }}
  .url {{ font-family: var(--hand); font-size: 1.75rem; color: var(--pencil); transform: rotate(-2deg); transform-origin: left; }}
  .schematic {{ grid-column: 2; width: 420px; margin: 0; }}
  .trace {{ animation: none !important; stroke-dasharray: none !important; stroke-dashoffset: 0 !important; opacity: 1 !important; }}
</style>
</head>
<body>
<div class="sheet">
  <span class="frame"></span>
  <span class="ruler ruler-top"></span>
  <span class="ruler ruler-left"></span>
  <span class="margin-rule"></span>
  <span class="hole hole-tl"></span>
  <span class="hole hole-tr"></span>
  <span class="hole hole-bl"></span>
  <span class="hole hole-br"></span>
  <div class="og">
    <div>
      <h1><img src="{(PUBLIC / 'icon.png').as_uri()}" alt="">Takku</h1>
      <p class="lead">Records your meetings, transcribes them on your Mac and writes the notes into your Obsidian vault.</p>
      <p class="url">takku.app</p>
    </div>
    <figure class="schematic">{drawing}</figure>
  </div>
</div>
</body>
</html>"""

with tempfile.TemporaryDirectory() as tmp:
    html = Path(tmp) / "og.html"
    html.write_text(page)
    subprocess.run(
        [
            CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
            "--force-prefers-reduced-motion", "--virtual-time-budget=4000", "--allow-file-access-from-files",
            "--window-size=1200,630", f"--screenshot={PUBLIC / 'og.png'}", html.as_uri(),
        ],
        check=True,
        capture_output=True,
    )
print(f"og.png: {(PUBLIC / 'og.png').stat().st_size // 1024} KB")
