import os
import time
import datetime
import feedparser
from email.utils import parsedate_to_datetime
from openai import OpenAI

# ================= 配置区域 =================
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"

# ================= 1. 抓取 24h 内的新闻 =================
def get_recent_news():
    print("📰 正在连接 HLTV 新闻中心...")
    try:
        # HLTV 全球新闻源
        feed = feedparser.parse("https://www.hltv.org/rss/news")
        
        recent_news = []
        now = datetime.datetime.now(datetime.timezone.utc)
        
        for entry in feed.entries:
            # 解析发布时间
            try:
                # 尝试解析 RSS 的时间格式
                published_time = parsedate_to_datetime(entry.published)
                
                # 计算时间差
                time_diff = now - published_time
                
                # 【核心逻辑】只取过去 24 小时内的新闻
                if time_diff.total_seconds() <= 24 * 3600:
                    recent_news.append({
                        "title": entry.title,
                        "summary": entry.description,
                        "link": entry.link,
                        "time": published_time.strftime("%H:%M") # 只保留时分
                    })
            except:
                continue

        return recent_news
    except Exception as e:
        print(f"❌ 获取新闻失败: {e}")
        return []

# ================= 2. 格式化给 AI =================
def format_for_ai(news_list):
    if not news_list:
        return None
    
    text = f"【过去 24 小时共有 {len(news_list)} 条重要新闻】\n"
    for item in news_list:
        text += f"- [{item['time']}] {item['title']}: {item['summary']} (原文: {item['link']})\n"
    return text

# ================= 3. DeepSeek 主编总结 =================
def generate_news_report(news_context):
    if not news_context:
        print("📭 过去 24h 没有新闻，跳过生成。")
        return None
        
    if not API_KEY: return "Error: No API Key"
    
    print("🧠 DeepSeek 主编正在审稿...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    system_prompt = """
    你是由 HLTV 和 完美世界电竞 联合培养的资深 CS2 新闻主编。
    你的任务是将碎片化的快讯整合成一篇**"CS2 日报"**。
    
    **写作要求：**
    1. **分类汇总**：不要流水账！必须将新闻分为【赛事战报】、【战队转会】、【版本更新】、【社区杂谈】等板块。
    2. **去伪存真**：去除无关紧要的小新闻，只保留大事件。
    3. **人话总结**：用简洁、专业的电竞媒体口吻（类似"从 HLTV 获悉..."）。
    4. **包含链接**：在每个大事件末尾，保留一个原文链接 [Link]。
    
    **文章结构：**
    - **【头条重磅】**：今日最重要的一件事（一定要有）。
    - **【分类资讯】**：分板块总结。
    - **【主编锐评】**：用一句话点评今日的圈子氛围（幽默或犀利）。
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"日期: {today}\n\n{news_context}"}
        ],
        stream=False
    )
    return response.choices[0].message.content

# ================= 4. 保存文章 =================
def save_news(content):
    if not content: return
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"""---
title: {today} CS2 全球战报：HLTV每日要闻速递
date: {time_now}
tags: [CS2新闻, 电竞资讯, 赛事战报]
categories: 每日日报
description: 过去24小时 CS2 圈发生了什么？DeepSeek 自动聚合 HLTV 最新资讯，为您带来最纯粹的电竞日报。
---

{content}
"""
    filename = f"source/_posts/{today}-daily-news.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"✅ 日报生成完毕: {filename}")

if __name__ == "__main__":
    recent_news = get_recent_news()
    context = format_for_ai(recent_news)
    if context:
        report = generate_news_report(context)
        save_news(report)