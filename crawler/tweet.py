import os
import tweepy
import pandas as pd
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from pathlib import Path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords

# 初始化 NLTK
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# === Step 1: API 初始化 ===
BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')
if not BEARER_TOKEN:
    raise RuntimeError("❌ TWITTER_BEARER_TOKEN 环境变量未设置")

client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# === Step 2: 配置 ===
QUERY = (
    '(large language model OR multimodal OR computer vision OR NLP OR ASR '
    'OR speech recognition OR transformers OR generative AI) '
    '(-is:retweet lang:en)'
)

USER_WHITELIST = {
    'MetaAI', 'OpenAI', 'DeepMind',
    'ilyasut', 'sama', 'ylecun', 'AndrewYNg', 'JeffDean'
}

utc_now = datetime.now(timezone.utc)
three_days_ago = utc_now - timedelta(days=3)
date_str = datetime.now().strftime('%Y-%m-%d')
formatted_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

SAVE_DIR = Path('./generate_docs/x')
SAVE_DIR.mkdir(parents=True, exist_ok=True)
csv_path = SAVE_DIR / f'x_{date_str}.csv'
md_path = SAVE_DIR / f'x_{date_str}.md'
wordcloud_path = SAVE_DIR / f'x_{date_str}_wordcloud.png'

# === Step 3: 推文抓取 ===
MAX_TWEETS = 100
MAX_RESULTS_PER_PAGE = 100
tweet_count = 0
next_token = None
all_data = []

while tweet_count < MAX_TWEETS:
    response = client.search_recent_tweets(
        query=QUERY,
        tweet_fields=['created_at', 'author_id', 'text', 'attachments'],
        user_fields=['username', 'name'],
        expansions=['author_id', 'attachments.media_keys'],
        media_fields=['url', 'preview_image_url', 'type'],
        max_results=MAX_RESULTS_PER_PAGE,
        next_token=next_token
    )

    if not response.data:
        break

    users = {u['id']: u for u in response.includes.get('users', [])}
    media_map = {m['media_key']: m for m in response.includes.get('media', [])}

    for tweet in response.data:
        created_time = tweet.created_at.replace(tzinfo=timezone.utc)
        # if created_time < three_days_ago:
        #     continue

        author = users.get(tweet.author_id)
        author_name = author.username if author else 'unknown'
        is_priority = author_name in USER_WHITELIST

        date_fmt = format_datetime(created_time)
        title = tweet.text[:50].replace('\n', ' ')
        description = tweet.text.replace('\n', ' ')
        link = f"https://twitter.com/{author_name}/status/{tweet.id}"

        media_links = []
        if 'attachments' in tweet.data and 'media_keys' in tweet.data['attachments']:
            for key in tweet.data['attachments']['media_keys']:
                media = media_map.get(key)
                if media:
                    media_links.append(media.get('url') or media.get('preview_image_url'))

        all_data.append({
            'Date': date_fmt,
            'Title': title,
            'Authors': author_name,
            'Categories': 'LLM, AI Research',
            'Description': description,
            'Link': link,
            'Media': ', '.join(media_links),
            'is_priority_author': is_priority
        })

        tweet_count += 1
        if tweet_count >= MAX_TWEETS:
            break

    next_token = response.meta.get('next_token')
    if not next_token:
        break

# === Step 4: 排序 & 输出 CSV ===
df = pd.DataFrame(all_data)
df = df.sort_values(by='is_priority_author', ascending=False).drop(columns='is_priority_author')
df.to_csv(csv_path, index=False, encoding='utf-8-sig')

# === Step 5: 输出 Markdown 文件 ===
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f"# 推文摘要报告 - {date_str}\n\n")
    for _, row in df.iterrows():
        f.write(f"## {row['Title']}\n")
        f.write(f"**作者**: {row['Authors']}  \n")
        f.write(f"**时间**: {row['Date']}  \n")
        f.write(f"**分类**: {row['Categories']}  \n")
        f.write(f"**链接**: [{row['Link']}]({row['Link']})  \n")
        if row['Media']:
            for link in row['Media'].split(','):
                f.write(f"![media]({link.strip()})  \n")
        f.write(f"\n{row['Description']}\n\n---\n\n")

# === Step 6: 关键词词云生成 ===
# 合并所有描述文本
text_blob = ' '.join(df['Description'].tolist())

# 简单文本清理
tokens = [
    word.lower() for word in text_blob.split()
    if word.isalpha() and word.lower() not in stop_words
]
clean_text = ' '.join(tokens)

# 生成词云图
wordcloud = WordCloud(width=1200, height=800, background_color='white').generate(clean_text)
plt.figure(figsize=(12, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.tight_layout()
plt.savefig(wordcloud_path)
plt.close()

# === 完成提示 ===
print(f"✅ 完成！共抓取 {len(df)} 条推文")
print(f"📄 CSV 文件保存于：{csv_path}")
print(f"📝 Markdown 文件保存于：{md_path}")
print(f"🌥️ 词云图保存于：{wordcloud_path}")