# articles/data/generate.py
from pathlib import Path
import json
import csv
from datetime import datetime as dt

# --- Paths (repo layout aware) ---
# This file is at: repo/articles/data/generate.py
ROOT = Path(__file__).resolve().parents[2]      # repo root
ARTICLES_DIR = ROOT / "articles"                # where we write generated pages
CONFIG_PATH = ARTICLES_DIR / "config.json"      # config lives in articles/
TOPICS_PATH = ARTICLES_DIR / "topics.csv"       # topics lives in articles/
INDEX_PATH = ROOT / "index.html"                # homepage is at repo root

def ts():
    return dt.utcnow().strftime("%Y-%m-%d %H:%M UTC")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_topics():
    # simple CSV: one topic per line
    topics = []
    with open(TOPICS_PATH, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            if not row:
                continue
            topic = row[0].strip()
            if topic:
                topics.append(topic)
    if not topics:
        raise ValueError("topics.csv est vide.")
    return topics

def render_html(title: str, intro: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{title}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
      .note {{ background: #f6f8fa; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <p><small>Generated {ts()}</small></p>
    <p class="note">Starter draft generated automatically.</p>

    <h2>What you'll find here</h2>
    <ul>
      <li>Clear, honest guidance for shoppers</li>
      <li>Editor-picked products with quick pros & cons</li>
      <li>Simple, scannable sections (no fluff)</li>
    </ul>

    <p><a href="../index.html">← Back to Home</a></p>
  </body>
</html>
"""

def ensure_li_link(index_path: Path, href: str, text: str):
    """
    Insert a <li><a href="...">text</a></li> into the first <ul> of index.html
    if not already present.
    """
    html = index_path.read_text(encoding="utf-8")
    li = f'<li><a href="{href}">{text}</a></li>'

    if li in html:
        return  # already linked

    # naive insert: after the first <ul> line, add our li
    lines = html.splitlines()
    for i, line in enumerate(lines):
        if "<ul>" in line:
            lines.insert(i + 1, f"  {li}")
            index_path.write_text("\n".join(lines), encoding="utf-8")
            return

    # if no <ul>, append a simple list block before </body>
    block = f"<ul>\n  {li}\n</ul>"
    if "</body>" in html:
        html = html.replace("</body>", block + "\n</body>")
    else:
        html += "\n" + block + "\n"
    index_path.write_text(html, encoding="utf-8")

def main():
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    cfg = load_config()
    topics = load_topics()

    # very simple: take the first topic and make a page name from it
    topic = topics[0]
    slug = "new-buyers-guide"  # you can slugify(topic) later if you want
    filename = f"{slug}.html"
    out_file = ARTICLES_DIR / filename

    # write article
    html = render_html("New Buyer's Guide", "Intro")
    out_file.write_text(html, encoding="utf-8")
    print(f"Wrote: {out_file}")

    # link from home (root index.html) to /articles/{filename}
    ensure_li_link(INDEX_PATH, href=f"articles/{filename}", text="New Buyers Guide")

if __name__ == "__main__":
    main()