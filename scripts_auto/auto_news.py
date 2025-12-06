import os
import datetime
import feedparser
import asyncio
import edge_tts
import re
from email.utils import parsedate_to_datetime
from openai import OpenAI

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
AUDIO_DIR = "source/audio"

if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

# 1. 抓取 HLTV 24h 新闻
def get_news():
    print("📰 正在抓取 HLTV...")
    try:
        feed = feedparser.parse("https://www.hltv.org/rss/news")
        recent = []
        now = datetime.datetime.now(datetime.timezone.utc)
        
        for e in feed.entries:
            try:
                pub = parsedate_to_datetime(e.published)
                if (now - pub).total_seconds() <= 86400: # 24小时内
                    recent.append(f"- {e.title}: {e.description}")
            except: continue
        return "\n".join(recent)
    except: return None

# 2. AI 总结
def ai_summary(news_txt):
    if not API_KEY or not news_txt: return None
    print("🧠 主编正在审稿...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    prompt = f"""
    你是由 HLTV 认证的 CS2 电竞主编。请把以下英文快讯总结成一份中文"CS2 日报"。
    快讯：\n{news_txt}
    
    要求：
    1. 分板块：【赛事战报】、【战队变动】、【社区资讯】。
    2. 语气专业、干练。
    3. 适合做成广播稿朗读。
    """
    
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    return resp.choices[0].message.content

# 3. TTS
async def gen_audio(text, filename):
    print("🎙️ 生成日报语音...")
    clean = re.sub(r'[\*\#\-]', '', text)
    tts = edge_tts.Communicate(f"大家好，这里是 CS2 全球战报。{clean}", "zh-CN-YunxiNeural")
    await tts.save(f"{AUDIO_DIR}/{filename}")

# 4. 保存
def save_file(content, audio_name):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    player = f"""
<div style="background:#eef2ff;padding:12px;border-radius:8px;margin-bottom:20px;">
  <div style="font-weight:bold;margin-bottom:8px;">📻 电竞日报 (点击收听)</div>
  <audio controls style="width:100%;"><source src="/audio/{audio_name}" type="audio/mpeg"></audio>
</div>"""

    md = f"""---
title: {today} CS2 全球战报：HLTV 每日速递
date: {now}
tags: [电竞新闻, CS2资讯, 播客]
description: 过去24小时圈内大事一览。DeepSeek 自动聚合生成。
---
{player}
{content}
"""
    fname = f"source/_posts/{today}-news.md"
    with open(fname, 'w', encoding='utf-8') as f: f.write(md)
    print(f"✅ 完成: {fname}")

async def main():
    news = get_news()
    if news:
        report = ai_summary(news)
        if report:
            audio_name = f"{datetime.datetime.now().strftime('%Y%m%d')}_news.mp3"
            await gen_audio(report, audio_name)
            save_file(report, audio_name)

if __name__ == "__main__":
    asyncio.run(main())