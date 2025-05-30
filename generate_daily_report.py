import os
import csv
import datetime
from markdown2 import markdown
from google import genai

# === 配置 ===
GENERATE_DOCS_DIR = "./generate_docs"
REPORTS_DIR = "./reports"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("请先设置 GEMINI_API_KEY 环境变量。")

# 初始化 Gemini
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
model_name = "gemini-2.0-flash"
# model_name = "gemini-2.5-flash-preview-05-20"

# === 获取当天日期字符串 ===
today_str = datetime.datetime.today().strftime("%Y%m%d")

def find_csv_files(base_dir, date_str):
    matched_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(f"{date_str}.csv"):
                matched_files.append(os.path.join(root, file))
    return matched_files

def classify_entries_by_type(file_paths):
    news_entries, paper_entries, code_entries = [], [], []

    for path in file_paths:
        file_name = os.path.basename(path)
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, [])  # 可选：读取表头
            for row in reader:
                entry = ", ".join(row)
                if file_name.startswith("arxiv"):
                    paper_entries.append(entry)
                elif file_name.startswith("github"):
                    code_entries.append(entry)
                else:
                    news_entries.append(entry)

    return news_entries, paper_entries, code_entries

def call_gemini_sdk(news_entries, paper_entries, code_entries):
    prompt = (
        "你是一名专业的信息分析助手，我将提供三类数据：新闻资讯、arXiv论文、GitHub代码仓，请你逐类分析并筛选推荐内容。"
        "最终以中文输出，不同类别请分别用markdown表格展示，表格之间换行。\n\n"

        "【新闻资讯】\n"
        "- 从以下新闻中选出你认为最重要的最多5条；\n"
        "- 输出格式：标题、推荐理由、内容概述（100字以内）、类别、链接；\n\n"
        + "\n".join(f"- {entry}" for entry in news_entries) + "\n\n"

        "【arXiv论文】\n"
        "- 从以下论文中筛选出最多5篇（如内容极其重要可略微超过），重点关注RAG、大模型、模型优化、知名作者或机构；\n"
        "- 输出格式：论文标题（原标题）、论文标题（中文标题）、推荐原因、论文概述（不超过100字，中文）、论文链接；\n\n"
        + "\n".join(f"- {entry}" for entry in paper_entries) + "\n\n"

        "【GitHub代码】\n"
        "- 分析以下代码仓的功能，筛选不超过5个值得推荐的项目；重点关注RAG工具、模型工具相关内容；\n"
        "- 输出格式：趋势、项目名、Star数、推荐理由、中文简要概述、项目链接；\n\n"
        + "\n".join(f"- {entry}" for entry in code_entries) + "\n\n"

        "请严格按顺序输出三个模块内容，全部使用中文，格式为美观的markdown表格，每类之间换行空行。\n"
    )

    response = gemini_client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    return response.text

def save_report(content_md, date_str):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    md_path = os.path.join(REPORTS_DIR, f"report_{date_str}.md")
    html_path = os.path.join(REPORTS_DIR, f"report_{date_str}.html")

    # 保存 Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content_md)
    print(f"✅ Markdown 报告已保存至: {md_path}")

    # 保存 HTML
    html_content = markdown(content_md)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ HTML 报告已保存至: {html_path}")

def main():
    csv_files = find_csv_files(GENERATE_DOCS_DIR, today_str)
    if not csv_files:
        print("⚠️ 未找到任何符合日期要求的CSV文件。")
        return

    print(f"📄 共找到 {len(csv_files)} 个CSV文件：\n", csv_files)
    news_entries, paper_entries, code_entries = classify_entries_by_type(csv_files)

    print("🔍 正在调用 Gemini 进行内容分析...")
    summary_md = call_gemini_sdk(news_entries, paper_entries, code_entries)

    print("💾 正在保存报告为 Markdown 和 HTML...")
    save_report(summary_md, today_str)

if __name__ == "__main__":
    main()