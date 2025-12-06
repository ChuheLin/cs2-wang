import os
import datetime
import requests
import json
import asyncio
import edge_tts
import re
from openai import OpenAI

# ================= 配置 =================
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
BULK_API = "http://csgobackpack.net/api/GetItemsList/v2/?currency=CNY"
AUDIO_DIR = "source/audio"

# 确保音频目录存在
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# 1. 获取全量数据
def get_bulk_data():
    print("🌍 正在下载全网数据 (约 10MB)...")
    try:
        resp = requests.get(BULK_API, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'): return data.get('items_list', {})
    except Exception as e:
        print(f"数据下载失败: {e}")
    return {}

# 2. 量化筛选 (30日均线回归逻辑)
def scan_market(items):
    print("🔍 正在进行价值扫描...")
    undervalued, overheated = [], []
    
    for name, details in items.items():
        try:
            if 'price' not in details or '30_days' not in details['price']: continue
            
            p_now = details['price']['24_hours'].get('average', 0)
            if p_now == 0: p_now = details['price']['24_hours'].get('median', 0)
            p_30 = details['price']['30_days'].get('average', 0)
            vol = details['price']['24_hours'].get('sold', 0)
            
            # 过滤：销量<10 或 价格<10 或 价格>20000 的不要
            if isinstance(vol, str): vol = int(vol.replace(',', '')) if vol.isdigit() else 0
            if vol < 10 or p_now < 10 or p_now > 20000 or p_30 <= 0: continue
            
            # 计算偏离度
            dev = ((p_now - p_30) / p_30) * 100
            
            item = {"name": name, "price": p_now, "dev": dev, "vol": vol}
            
            if dev < -8: undervalued.append(item) # 跌超8%
            elif dev > 15: overheated.append(item) # 涨超15%
        except: continue
        
    # 取 Top 6
    top_under = sorted(undervalued, key=lambda x: x['dev'])[:6]
    top_over = sorted(overheated, key=lambda x: x['dev'], reverse=True)[:6]
    return top_under, top_over

# 3. 格式化给 AI
def format_data(u, o):
    txt = "【量化扫描结果】\n📉 低估区 (击球区):\n"
    for i in u: txt += f"- {i['name']}: ¥{i['price']:.1f} (偏离 {i['dev']:.1f}%)\n"
    txt += "\n🔥 过热区 (风险区):\n"
    for i in o: txt += f"- {i['name']}: ¥{i['price']:.1f} (偏离 +{i['dev']:.1f}%)\n"
    return txt

# 4. DeepSeek 撰写
def write_report(data_str):
    if not API_KEY: return None
    print("🧠 AI 分析师正在撰写...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    你是一位推崇段永平价值投资的 CS2 分析师。请基于以下数据写一篇研报。
    数据：\n{data_str}
    
    要求：
    1. 标题不含 markdown。
    2. 分三部分：【市场情绪】、【价值洼地点评】(重点分析低估区)、【风险提示】。
    3. 引用一句投资名言（如段永平或巴菲特）结尾。
    4. 口语化一点，方便朗读。
    """
    
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    return resp.choices[0].message.content

# 5. 生成 TTS 音频
async def gen_audio(text, filename):
    print("🎙️ 正在生成语音...")
    # 清洗文本，去掉 markdown 符号
    clean = re.sub(r'[\*\#\-]', '', text)
    tts = edge_tts.Communicate(f"欢迎收听 CS2 价值研报。{clean}", "zh-CN-YunxiNeural")
    await tts.save(f"{AUDIO_DIR}/{filename}")

# 6. 保存
def save_file(content, audio_name):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    player = f"""
<div style="background:#f4f4f5;padding:12px;border-radius:8px;margin-bottom:20px;">
  <div style="font-weight:bold;margin-bottom:8px;">🎧 AI 语音分析 (点击播放)</div>
  <audio controls style="width:100%;"><source src="/audio/{audio_name}" type="audio/mpeg"></audio>
</div>"""

    md = f"""---
title: {today} 市场量化扫描：寻找价值洼地
date: {now}
tags: [价值投资, CS2量化, 播客]
description: AI 自动扫描全网饰品，分析今日均线偏离度。点击收听语音版。
---
{player}
{content}
"""
    fname = f"source/_posts/{today}-quant.md"
    with open(fname, 'w', encoding='utf-8') as f: f.write(md)
    print(f"✅ 完成: {fname}")

async def main():
    items = get_bulk_data()
    if not items: return
    u, o = scan_market(items)
    data_str = format_data(u, o)
    report = write_report(data_str)
    
    if report:
        audio_name = f"{datetime.datetime.now().strftime('%Y%m%d')}_quant.mp3"
        await gen_audio(report, audio_name)
        save_file(report, audio_name)

if __name__ == "__main__":
    asyncio.run(main())