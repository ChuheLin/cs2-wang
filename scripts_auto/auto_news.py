import os
import datetime
import feedparser
import asyncio
import re
from gtts import gTTS
from email.utils import parsedate_to_datetime
from openai import OpenAI

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
AUDIO_DIR = "source/audio"

if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

def get_news():
    print("📰 正在抓取 HLTV...")
    try:
        feed = feedparser.parse("https://www.hltv.org/rss/news")
        recent = []
        now = datetime.datetime.now(datetime.timezone.utc)
        for e in feed.entries:
            try:
                pub = parsedate_to_datetime(e.published)
                if (now - pub).total_seconds() <= 86400:
                    recent.append(f"- {e.title}: {e.description}")
            except: continue
        return "\n".join(recent)
    except: return None

def ai_summary(news_txt):
    if not API_KEY or not news_txt: return None
    print("🧠 主编正在审稿...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    prompt = f"你是由 HLTV 认证的 CS2 电竞主编。把以下快讯总结成中文日报。\n快讯：\n{news_txt}\n要求：分板块，语气专业，适合朗读。"
    resp = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}], stream=False)
    return resp.choices[0].message.content

# 核心修改：Google TTS
def gen_audio(text, filename):
    print("🎙️ Google 正在生成语音...")
    try:
        clean = re.sub(r'[\*\#\-]', '', text)
        tts = gTTS(text=f"这里是 CS2 全球战报。{clean}", lang='zh-cn')
        tts.save(f"{AUDIO_DIR}/{filename}")
        return True
    except Exception as e:
        print(f"⚠️ 语音生成失败: {e}")
        return False

def save_file(content, audio_name):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    player = ""
    if audio_name:
        player = f"""<div style="background:#eef2ff;padding:12px;border-radius:8px;margin-bottom:20px;"><div style="font-weight:bold;margin-bottom:8px;">📻 电竞日报 (Google引擎)</div><audio controls style="width:100%;"><source src="/audio/{audio_name}" type="audio/mpeg"></audio></div>"""
    md = f"""---
title: {today} CS2 全球战报：HLTV 每日速递
date: {now}
tags: [电竞新闻, CS2资讯, 播客]
description: 过去24小时圈内大事一览。
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
            # 去掉 await
            success = gen_audio(report, audio_name)
            final_audio_name = audio_name if success else None
            save_file(report, final_audio_name)

if __name__ == "__main__":
    asyncio.run(main())