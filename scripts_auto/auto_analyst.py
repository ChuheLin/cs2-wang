import os
import datetime
import feedparser
import requests
from openai import OpenAI

# 从环境变量获取 Key (千万不要直接把 Key 写死在这里，容易泄露)
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"

def get_hltv_news():
    print("正在抓取 HLTV 新闻...")
    # HLTV RSS 源
    feed = feedparser.parse("https://www.hltv.org/rss/news")
    news_list = []
    # 只取前 5 条
    for entry in feed.entries[:5]:
        news_list.append(f"- {entry.title}: {entry.description}")
    return "\n".join(news_list)

def generate_report(news_context):
    if not API_KEY:
        print("错误：没有找到 API Key！")
        return None

    print("正在召唤 DeepSeek 分析师...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    日期: {today}
    【今日 CS2 新闻摘要】
    {news_context}

    请你扮演一位专业的 CS2 饰品市场分析师。基于以上新闻，写一篇简短犀利的"每日市场观察"。
    要求：
    1. 标题不包含 markdown 标记。
    2. 如果新闻跟饰品无关，就编撰一些关于"市场情绪平稳"的分析。
    3. 风格类似金融研报，包含"市场情绪"、"重点关注"、"投资建议"三个板块。
    4. 字数控制在 500 字以内。
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    return response.choices[0].message.content

def save_to_hexo(content):
    if not content:
        return
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建 Hexo 文章格式
    md_content = f"""---
title: {today} CS2 市场每日简报
date: {time_now}
tags: [自动化研报, CS2, 市场分析]
description: DeepSeek 自动生成的每日 CS2 市场深度分析。
---

{content}
"""
    # 自动保存到 Hexo 的文章目录下
    filename = f"source/_posts/{today}-report.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ 成功生成文章：{filename}")

if __name__ == "__main__":
    news = get_hltv_news()
    report = generate_report(news)
    save_to_hexo(report)