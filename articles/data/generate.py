# articles/data/generate.py
import json, os, datetime, csv, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
CONFIG_PATH = os.path.join(ROOT, "config.json")
TOPICS_PATH = os.path.join(ROOT, "topics.csv")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_topics():
    topics = []
    if not os.path.exists(TOPICS_PATH):
        raise FileNotFoundError(f"topics.csv introuvable: {TOPICS_PATH}")
    with open(TOPICS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            line = (row[0] or "").strip() if row else ""
            if line:
                topics.append(line)
    if not topics:
        raise ValueError("topics.csv est vide.")
    return topics

def slugify(title: str) -> str:
    s = "".join(c.lower() if c.isalnum() else "-" for c in title)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")

def render_html(title: str, intro: str) -> str:
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>body{{font:16px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial,sans-serif;max-width:760px;margin:40px auto;padding:0 16px;}}h1{{font-size:32px;margin:0 0 8px}}.note{{background:#f4f6f8;border:1px solid #e5e7eb;padding:12px 14px;border-radius:8px;margin:12px 0}}</style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p class="note">Generated {ts}</p>
  <p>{html.escape(intro)}</p>
  <hr>
  <p><a href="../index.html">← Back to Home</a></p>
</body>
</html>
"""

def ensure_li_link(index_path: str, href: str, text: str):
    """Ajoute <li><a …>…</a></li> dans index.html si le lien n'y est pas déjà."""
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"index.html introuvable: {index_path}")

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    li_line = f'<li><a href="{href}">{html.escape(text)}</a></li>'
    if li_line in content:
        return  # déjà présent, on ne duplique pas

    # On insère juste avant la fermeture de la liste </ul> si trouvée, sinon avant </body>
    if "</ul>" in content:
        content = content.replace("</ul>", f"  {li_line}\n</ul>")
    else:
        content = content.replace("</body>", f"{li_line}\n</body>")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    cfg = load_config()
    topics = load_topics()

    # On prend le 1er sujet comme démo (tu peux choisir autrement si tu veux)
    topic = topics[0]
    title = cfg.get("site_title_prefix", "New Buyer’s Guide").strip() or "New Buyer’s Guide"
    intro = cfg.get("intro", "Starter draft generated automatically.")

    # Chemins
    out_dir = os.path.join(ROOT, "articles")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{slugify('new-buyers-guide')}.html"
    out_file = os.path.join(out_dir, filename)

    # Écrit la page
    html_text = render_html(title, intro)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_text)
    print(f"Wrote: {out_file}")

    # Ajoute le lien dans la home automatiquement
    index_path = os.path.join(ROOT, "index.html")
    ensure_li_link(index_path, href=f"articles/{filename}", text="New Buyers Guide")
    print("Home updated with link.")

if __name__ == "__main__":
    main()