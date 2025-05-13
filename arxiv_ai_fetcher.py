import feedparser
from datetime import datetime
import csv
import re
from html import unescape
import os

def clean_html(text):
    text = unescape(text)
    text = re.sub(r'<.*?>', '', text)
    return text.strip()

feed = feedparser.parse("https://export.arxiv.org/rss/cs.AI")
papers = []

for entry in feed.entries:
    title = entry.title.strip()
    link = entry.link
    published = entry.published

    if "authors" in entry:
        authors = ", ".join([a.get("name", "") for a in entry.authors])
    else:
        authors = "Unknown"

    abstract = clean_html(entry.description)
    categories = ", ".join(tag.term for tag in entry.tags) if "tags" in entry else "cs.AI"

    papers.append({
        "Date": published,
        "Title": title,
        "Authors": authors,
        "Categories": categories,
        "Abstract": abstract,
        "Link": link
    })

# 保存 CSV
today = datetime.now().strftime("%Y%m%d")
os.makedirs("output", exist_ok=True)
with open(f"output/arxiv_ai_{today}.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=papers[0].keys())
    writer.writeheader()
    for p in papers:
        writer.writerow(p)

print("✅ CSV saved to output/")