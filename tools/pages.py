"""Writes the secondary pages (public/<name>.html) from their content in pages/<name>.html,
with the same head, sheet and title block as the home page, puts the same title block,
with the list of sheets, into public/index.html, and lists the sheets in public/sitemap.xml.

    python3 tools/pages.py

A page in pages/ starts with a comment that gives its title and description:

    <!--
    title: Set up Takku
    description: Install Takku on your Mac, …
    -->
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
PAGES = ROOT / "pages"

# The sheets of the drawing, in order: (name, path, title in the title block)
SHEETS = [
    ("index", "/", "Takku"),
    ("setup", "/setup", "Setup"),
    ("credit", "/credit", "Credit"),
    ("guide", "/guide", "Guide"),
    ("hooks", "/hooks", "Hooks"),
    ("faq", "/faq", "FAQ"),
    ("privacy", "/privacy", "Privacy"),
    ("granola", "/granola", "Granola"),
]
# Pages that are not sheets: not in the title block, not in the sitemap, not indexed.
UNLISTED = {"404"}
SITE = "https://takku.app"

SHEET_DECORATIONS = """  <span class="frame" aria-hidden="true"></span>
  <span class="ruler ruler-top" aria-hidden="true"></span>
  <span class="ruler ruler-left" aria-hidden="true"></span>
  <span class="margin-rule" aria-hidden="true"></span>
  <span class="hole hole-tl" aria-hidden="true"></span>
  <span class="hole hole-tr" aria-hidden="true"></span>
  <span class="hole hole-bl" aria-hidden="true"></span>
  <span class="hole hole-br" aria-hidden="true"></span>
"""


def footer(current):
    sheets = []
    for number, (name, path, title) in enumerate(SHEETS, 1):
        if name == current:
            sheets.append(f'<span class="sheet-link" aria-current="page">{number} {title}</span>')
        else:
            sheets.append(f'<a class="sheet-link" href="{path}">{number} {title}</a>')
    return f"""  <footer class="row">
    <div class="main">
      <div class="title-block-wrap sketch">
      <table class="title-block">
        <tr>
          <th scope="row">Sheets</th>
          <td colspan="3"><nav aria-label="Pages" class="sheets">{" ".join(sheets)}</nav></td>
        </tr>
        <tr>
          <th scope="row">Project</th>
          <td>Takku, a menu bar app for macOS</td>
          <th scope="row">Drawn by</th>
          <td><a href="https://github.com/mameli">mameli</a></td>
        </tr>
        <tr>
          <th scope="row">Source</th>
          <td><a href="https://github.com/mameli/Takku">mameli/Takku</a></td>
          <th scope="row">License</th>
          <td>MIT</td>
        </tr>
        <tr>
          <th scope="row">Requires</th>
          <td>Apple Silicon, macOS 15 or later</td>
          <th scope="row">Releases</th>
          <td><a href="https://github.com/mameli/Takku/releases">all versions</a></td>
        </tr>
        <tr>
          <th scope="row">Support</th>
          <td colspan="3"><a href="https://buymeacoffee.com/mameli.dev">buy me a coffee</a>, it helps cover the costs of keeping Takku going</td>
        </tr>
      </table>
      </div>
    </div>
  </footer>
"""


def page(name, title, description, body):
    title_attr = html.escape(title, quote=True)
    description_attr = html.escape(description, quote=True)
    if name in UNLISTED:
        indexing = '<meta name="robots" content="noindex">'
    else:
        indexing = f'<link rel="canonical" href="{SITE}/{name}">'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{description_attr}">
  {indexing}
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#f1f3ee" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#1d3f73" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Takku">
  <meta property="og:title" content="{title_attr}">
  <meta property="og:description" content="{description_attr}">
  <meta property="og:url" content="https://takku.app/{name}">
  <meta property="og:image" content="https://takku.app/og.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="preload" href="/fonts/kalam-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/literata.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
<div class="sheet">
{SHEET_DECORATIONS}
{body.rstrip()}

{footer(name)}</div>
</body>
</html>
"""


for source in sorted(PAGES.glob("*.html")):
    text = source.read_text()
    meta = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
    assert meta, f"{source.name}: the page must start with its title and description"
    fields = dict(line.split(": ", 1) for line in meta.group(1).splitlines())
    name = source.stem
    assert name in {n for n, _, _ in SHEETS} | UNLISTED, f"{name} is not in SHEETS"
    (PUBLIC / f"{name}.html").write_text(page(name, fields["title"], fields["description"], text[meta.end():]))
    print(f"public/{name}.html")

index = PUBLIC / "index.html"
text, count = re.subn(r'  <footer class="row">.*?</footer>\n', lambda _: footer("index"), index.read_text(), flags=re.S)
assert count == 1
index.write_text(text)
print("public/index.html (title block)")

urls = "".join(f"  <url><loc>{SITE}{path}</loc></url>\n" for _, path, _ in SHEETS)
(PUBLIC / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n"
)
print("public/sitemap.xml")
