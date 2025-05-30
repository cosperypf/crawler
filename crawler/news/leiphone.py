'''
书写一个python脚本，实现以下功能：
1. 从https://www.leiphone.com/feed拉取数据
2. 遍历所有的内容，按照这些标题进行整理汇总Date,Title,Authors,Categories,Description,Link
3. 输出为csv文件，存储到./generate_docs/leiphone文件夹下，文件名为leiphone_<日期>.csv其中日期为当前日期，格式类似20250530
'''

import os
import csv
import datetime
import feedparser
import requests
from io import BytesIO

# Step 1: 拉取雷锋网 RSS Feed 数据
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}
FEED_URL = "https://www.leiphone.com/feed"
response = requests.get(FEED_URL, headers=headers)
feed = feedparser.parse(BytesIO(response.content))

# Step 2: 创建输出目录
output_dir = "./generate_docs/leiphone"
os.makedirs(output_dir, exist_ok=True)

# Step 3: 设置文件名
today_str = datetime.datetime.now().strftime("%Y%m%d")
output_file = os.path.join(output_dir, f"leiphone_{today_str}.csv")

# Step 4: 提取字段并写入 CSV
with open(output_file, mode="w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Date", "Title", "Authors", "Categories", "Description", "Link"])
    
    for entry in feed.entries:
        date = entry.get("published", "")
        title = entry.get("title", "")
        authors = ", ".join([a.name for a in entry.get("authors", [])]) if "authors" in entry else ""
        categories = ", ".join([t.term for t in entry.get("tags", [])]) if "tags" in entry else ""
        description = entry.get("summary", "").replace('\n', ' ').replace('\r', '')
        link = entry.get("link", "")

        writer.writerow([date, title, authors, categories, description, link])

print(f"✅ 雷锋网 RSS 已保存到：{output_file}")