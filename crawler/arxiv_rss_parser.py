import feedparser
from datetime import datetime
import csv
import os
from html import unescape
import re
import requests
from io import BytesIO

if __name__ == "__main__":
    print("🚀 开始解析 RSS...")
    # ========== 设置路径 ==========
    output_dir = "./generate_docs/archive"
    os.makedirs(output_dir, exist_ok=True)
    csv_filename = f"arxiv_ai_{datetime.now().strftime('%Y%m%d')}.csv"
    output_path = os.path.join(output_dir, csv_filename)

    # ========== 解析 RSS ==========
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
    }
    RSS_URL = "https://export.arxiv.org/rss/cs.AI"
    response = requests.get(RSS_URL, headers=headers)
    feed = feedparser.parse(BytesIO(response.content))

    def clean_html(text):
        text = unescape(text)
        text = re.sub(r'<.*?>', '', text)
        return text.strip()

    papers = []
    for entry in feed.entries:
        title = entry.title.strip()
        link = entry.link
        published = entry.published

        # ✅ 修复：从 entry.authors 中提取作者名
        if "authors" in entry:
            authors = ", ".join([a.get("name", "") for a in entry.authors])
        else:
            authors = "Unknown"

        # ✅ 抽取摘要
        abstract = clean_html(entry.description)

        # ✅ 提取类别
        categories = ", ".join(tag.term for tag in entry.tags) if "tags" in entry else "cs.AI"

        papers.append({
            "Date": published,
            "Title": title,
            "Authors": authors,
            "Categories": categories,
            "Abstract": abstract,
            "Link": link
        })

    # ========== 写入 CSV ==========
    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Date", "Title", "Authors", "Categories", "Abstract", "Link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)

    print(f"✅ 已保存至：{output_path}")