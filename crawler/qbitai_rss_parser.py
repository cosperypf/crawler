import feedparser
from datetime import datetime
import csv
import os
from html import unescape
import re
import requests
from io import BytesIO

if __name__ == "__main__":
    print("🚀 开始解析量子位 RSS...")
    # ========== 设置路径 ==========
    output_dir = "./generate_docs/qbitai"
    os.makedirs(output_dir, exist_ok=True)
    csv_filename = f"qbitai_{datetime.now().strftime('%Y%m%d')}.csv"
    output_path = os.path.join(output_dir, csv_filename)

    # ========== 解析 RSS ==========
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
    }
    RSS_URL = "https://www.qbitai.com/feed"
    response = requests.get(RSS_URL, headers=headers)
    feed = feedparser.parse(BytesIO(response.content))

    def clean_html(text):
        text = unescape(text)
        text = re.sub(r'<.*?>', '', text)
        return text.strip()

    articles = []
    for entry in feed.entries:
        title = entry.title.strip()
        link = entry.link
        published = entry.published

        # 提取作者信息
        if "dc_creator" in entry:
            authors = entry.dc_creator
        else:
            authors = "Qbitai"

        # 提取描述
        description = clean_html(entry.description)

        # 提取分类标签
        if "tags" in entry:
            categories = ", ".join(tag.term for tag in entry.tags)
        elif "category" in entry:
            categories = entry.category
        else:
            categories = "AI资讯"

        articles.append({
            "Date": published,
            "Title": title,
            "Authors": authors,
            "Categories": categories,
            "Description": description,
            "Link": link
        })

    # ========== 写入 CSV ==========
    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Date", "Title", "Authors", "Categories", "Description", "Link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)

    print(f"✅ 量子位资讯已保存至：{output_path}")