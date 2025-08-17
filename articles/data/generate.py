import os, json, csv, re, datetime, pathlib
from textwrap import dedent
from urllib.parse import urlencode, quote_plus
from openai import OpenAI

ROOT = pathlib.Path(__file__).parent.resolve()
ART = ROOT / "articles"
ART.mkdir(exist_ok=True)
CFG = json.loads((ROOT/"config.json").read_text())

def slugify(s):
    s = re.sub(r"[^a-z0-9\- ]", "", s.lower())
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:80]

def ama_url(asin, tag):
    # construit une URL affiliée Amazon courte
    return f"https://www.amazon.com/dp/{quote_plus(asin)}?{urlencode({'tag': tag})}"

def write_html(slug, title, body):
    html = f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {CFG['site_name']}</title>
<link rel="canonical" href="{CFG['base_url']}/articles/{slug}.html">
<meta name="description" content="{title} – curated picks and buyer’s guide.">
<style>body{{font-family:system-ui,Segoe UI,Arial;margin:24px;line-height:1.55;max-width:900px}} .btn{{display:inline-block;padding:.6rem 1rem;border:1px solid #222;border-radius:8px;text-decoration:none}} .card{{border:1px solid #eee;border-radius:12px;padding:18px;margin:16px 0}} .tag{{font-size:12px;background:#f2f2f2;border-radius:6px;padding:2px 8px}}</style>
</head><body>
<a href="../index.html" class="btn">← Home</a>
<h1>{title}</h1>
<p class="tag">Updated {datetime.date.today().isoformat()}</p>
{body}
<hr><p style="font-size:12px;color:#666">Affiliate disclosure: we may earn commissions from links.</p>
</body></html>"""
    (ART/f"{slug}.html").write_text(html, encoding="utf-8")

def update_index(new_links):
    idx = ROOT/"index.html"
    html = idx.read_text(encoding="utf-8") if idx.exists() else "<!doctype html><html><head><meta charset='utf-8'><title>{}</title></head><body><h1>{}</h1><ul></ul></body></html>".format(CFG["site_name"], CFG["site_name"])
    # insère <li><a ...> si non présent
    for a in new_links:
        if a not in html:
            html = html.replace("</ul>", f"  {a}\n</ul>")
    idx.write_text(html, encoding="utf-8")

def update_sitemap():
    base = CFG["base_url"]
    urls = [f"{base}/", *(f"{base}/articles/{p.name}" for p in sorted(ART.glob("*.html")))]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    today = datetime.date.today().isoformat()
    for u in urls:
        xml += [f"<url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq></url>"]
    xml += ["</urlset>"]
    (ROOT/"sitemap.xml").write_text("\n".join(xml), encoding="utf-8")
    (ROOT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")

def pick_topics(n):
    with open(ROOT/"data/topics.csv") as f:
        topics = [r.strip() for r in f if r.strip()]
    # prend les premiers non publiés
    done = {p.stem for p in ART.glob("*.html")}
    queue = [t for t in topics if slugify(t) not in done]
    return queue[:n]

def gen_article(client, topic):
    prompt = dedent(f"""
    You are a senior commerce writer. Write a 1200-word, SEO-optimized buyer’s guide on: "{topic}".
    Structure:
    - Intro 2–3 paragraphs.
    - “Top Picks” list with 5 products. For each: name, 3 bullets (pros), who it’s for, and a placeholder ASIN like ASIN:XXXX.
    - Comparison table (HTML <table>) with the 5 products and key specs (weight/ANC/battery/wireless/price range).
    - How to choose (criteria).
    - FAQ (5 Q/A).
    Important:
    - DO NOT invent prices. Use ranges (e.g., “~$80–120”).
    - When you output ASIN placeholders, format exactly ASIN:XXXXXXXXXX (10 chars). We will convert them to affiliate links.
    - Output valid HTML fragments only for the BODY (no <html> or <head>).
    """)
    resp = client.chat.completions.create(
        model="gpt-5-mini",  # coût bas, bon pour génération
        messages=[{"role":"user","content":prompt}],
        temperature=0.4
    )
    return resp.choices[0].message.content

def replace_asins_with_links(html, tag):
    # remplace ASIN:XXXXXXXXXX par un bouton affilié
    def repl(m):
        asin = m.group(1)
        url = ama_url(asin, tag)
        return f'<p><a class="btn" href="{url}" target="_blank" rel="nofollow sponsored">View on Amazon</a></p>'
    return re.sub(r"ASIN:([A-Z0-9]{10})", repl, html)

def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    topics = pick_topics(CFG["articles_per_run"])
    new_index_links = []
    for topic in topics:
        slug = slugify(topic)
        body = gen_article(client, topic)
        body = replace_asins_with_links(body, CFG["associate_tag"])
        write_html(slug, topic.title(), body)
        new_index_links.append(f'<li><a href="articles/{slug}.html">{topic.title()}</a></li>')
    if new_index_links:
        update_index(new_index_links)
        update_sitemap()
        print(f"Generated {len(new_index_links)} article(s).")
    else:
        print("No new topics to generate.")

if __name__ == "__main__":
    main()