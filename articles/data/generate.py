# articles/data/generate.py
# -----------------------------------------------------------------------------
# Génère un article HTML simple à partir de topics.csv et config.json.
# Emplacement des fichiers attendu :
#   - ce script : articles/data/generate.py
#   - config.json et topics.csv : à la RACINE du dépôt
#   - sortie : articles/<slug>.html
# -----------------------------------------------------------------------------

from pathlib import Path
import csv
import json
import re
from datetime import datetime

# 1) Localisation des chemins (ne rien changer ici)
#    Ce fichier est dans: articles/data/generate.py  -> racine = parents[2]
ROOT = Path(__file__).resolve().parents[2]
ARTICLES_DIR = ROOT / "articles"
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = ROOT / "config.json"
TOPICS_PATH = ROOT / "topics.csv"

# 2) Utilitaires
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")

def now_utc_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

# 3) Charger config + topics
def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"config.json introuvable: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

def load_topics():
    if not TOPICS_PATH.exists():
        raise FileNotFoundError(f"topics.csv introuvable: {TOPICS_PATH}")
    rows = list(csv.DictReader(TOPICS_PATH.open(encoding="utf-8")))
    if not rows:
        raise ValueError("topics.csv est vide.")
    return rows

# 4) Générer un HTML très simple (squelette)
def render_html(title: str, intro: str) -> str:
    ts = now_utc_iso()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} • True Buyers Guide</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; line-height: 1.6; padding: 2rem; max-width: 820px; margin: auto; }}
    h1 {{ font-size: 2rem; margin-bottom: .25rem; }}
    .meta {{ color: #555; margin-bottom: 1.5rem; }}
    a {{ color: #0a58ca; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .back {{ margin-top: 2rem; display: inline-block; }}
    .note {{ background:#f6f8fa; border:1px solid #e5e7eb; padding:.75rem 1rem; border-radius:.5rem; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">Generated {ts}</div>

  <p class="note">{intro}</p>

  <h2>What you'll find here</h2>
  <ul>
    <li>Clear, honest guidance for shoppers</li>
    <li>Editor-picked products with quick pros & cons</li>
    <li>Simple, scannable sections (no fluff)</li>
  </ul>

  <p class="back"><a href="./index.html">← Back to Home</a></p>
</body>
</html>
"""

def main():
    cfg = load_config()
    topics = load_topics()

    # On prend la première ligne comme sujet du jour (simple et déterministe)
    topic = topics[0]
    title = topic.get("title") or topic.get("Topic") or "New Buyer’s Guide"
    intro = topic.get("intro") or topic.get("Intro") or "Starter draft generated automatically."

    slug = topic.get("slug") or slugify(title)
    # file name simple : <slug>.html
    outfile = ARTICLES_DIR / f"{slug}.html"

    html = render_html(title, intro)
    outfile.write_text(html, encoding="utf-8")
    print(f"Written: {outfile}")

if __name__ == "__main__":
    main()