import requests
import re
import os
import datetime
import pandas as pd
from bs4 import BeautifulSoup

# 保存路径
BASE_PATH = "./generate_docs/github_trends"
os.makedirs(BASE_PATH, exist_ok=True)

# 获取当前日期
TODAY = datetime.datetime.today().strftime("%Y%m%d")

# AI关键词列表（可扩展）
AI_KEYWORDS = ['ai', 'artificial intelligence', 'machine learning', 'deep learning',
               'neural', 'nlp', 'transformer', 'llm', 'chatgpt', 'gpt']

# GitHub Trending 时间维度
TRENDS = {
    "daily": "今日",
    "weekly": "近7日",
    "monthly": "近30日"
}


def parse_star_count(star_str):
    """将 GitHub star 数格式如 '3.5k' 转为整数"""
    star_str = star_str.strip().lower().replace(',', '')
    if 'k' in star_str:
        return int(float(star_str.replace('k', '')) * 1000)
    elif 'm' in star_str:
        return int(float(star_str.replace('m', '')) * 1000000)
    return int(star_str)


def fetch_trending(since='daily'):
    url = f"https://github.com/trending?since={since}&spoken_language_code=en"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    articles = soup.find_all('article', class_='Box-row')
    result = []

    for article in articles:
        # 获取 repo 名称
        header = article.h2
        if not header:
            continue

        repo_link = header.find('a')
        if not repo_link:
            continue

        repo = repo_link.get('href').strip('/')  # /owner/repo => owner/repo
        author, name = repo.split('/')

        # 获取描述
        desc_tag = article.find('p')
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # 获取 star 数
        star_tag = article.find('a', href=lambda x: x and x.endswith('/stargazers'))
        stars = parse_star_count(star_tag.text.strip()) if star_tag else 0

        full_url = f"https://github.com/{repo}"
        result.append({
            "repository": repo,
            "author": author,
            "name": name,
            "description": description,
            "url": full_url,
            "stars": stars
        })

    return result


def is_ai_project(description):
    desc = description.lower()
    return any(keyword in desc for keyword in AI_KEYWORDS)


def save_to_csv_md(data_by_trend):
    csv_rows = []
    md_lines = ["# 📊 GitHub AI 项目趋势汇总（" + TODAY + "）\n"]

    for trend_key, trend_label in TRENDS.items():
        data = data_by_trend.get(trend_key, [])
        if not data:
            continue

        md_lines.append(f"## ⭐ {trend_label}趋势\n")
        md_lines.append("| 项目 | ⭐Stars | 描述 | 链接 |")
        md_lines.append("|------|---------|------|------|")

        for row in data:
            csv_rows.append({
                "趋势": trend_label,
                "项目": row["repository"],
                "Stars": row["stars"],
                "描述": row["description"],
                "链接": row["url"]
            })
            md_lines.append(
                f"| `{row['repository']}` | {row['stars']} | {row['description'] or '无'} | [🔗链接]({row['url']}) |"
            )

        md_lines.append("\n")

    # 保存 CSV
    csv_path = os.path.join(BASE_PATH, f"github_trends_{TODAY}.csv")
    df = pd.DataFrame(csv_rows)
    df.to_csv(csv_path, index=False)
    print(f"✅ 已保存 CSV：{csv_path}")

    # # 保存 Markdown
    # md_path = os.path.join(BASE_PATH, f"github_trends_{TODAY}.md")
    # with open(md_path, "w", encoding="utf-8") as f:
    #     f.write("\n".join(md_lines))
    # print(f"✅ 已保存 MD：{md_path}")


def main():
    print("📡 正在抓取 GitHub Trending 页面...")
    data_by_trend = {}

    for trend_key in TRENDS.keys():
        trending = fetch_trending(trend_key)
        ai_related = [r for r in trending if is_ai_project(r['description'])]
        # 按 stars 排序
        ai_related.sort(key=lambda r: r.get("stars", 0), reverse=True)
        data_by_trend[trend_key] = ai_related
        print(f"🧠 {TRENDS[trend_key]}：共发现 AI 项目 {len(ai_related)} 个")

    save_to_csv_md(data_by_trend)


if __name__ == "__main__":
    main()