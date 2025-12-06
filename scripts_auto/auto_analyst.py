import os
import datetime
import requests
import json
import asyncio
import edge_tts
import re
from openai import OpenAI

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
BULK_API = "http://csgobackpack.net/api/GetItemsList/v2/?currency=CNY"
AUDIO_DIR = "source/audio"

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

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
            if isinstance(vol, str): vol = int(vol.replace(',', '')) if vol.isdigit() else 0
            if vol < 10 or p_now < 10 or p_now > 20000 or p_30 <= 0: continue
            dev = ((p_now - p_30) / p_30) * 100
            item = {"name": name, "price": p_now, "dev": dev, "vol": vol}
            if dev < -8: undervalued.append(item)
            elif dev > 15: overheated.append(item)
        except: continue
    top_under = sorted(undervalued, key=lambda x: x['dev'])[:6]
    top_over = sorted(overheated, key=lambda x: x['dev'], reverse=True)[:6]
    return top_under, top_over

def format_data(u, o):
    txt = "【量化扫描结果】\n📉 低估区 (击球区):\n"
    for i in u: txt += f"- {i['name']}: ¥{i['price']:.1f} (偏离 {i['dev']:.1f}%)\n"
    txt += "\n🔥 过热区 (风险区):\n"
    for i in o: txt += f"- {i['name']}: ¥{i['price']:.1f} (偏离 +{i['dev']:.1f}%)\n"
    return txt

def write_report(data_str):
    if not API_KEY: return None
    print("🧠 AI 分析师正在撰写...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    prompt = f"你是一位推崇段永平价值投资的 CS2 分析师。请基于以下数据写一篇研报。\n数据：\n{data_str}\n要求：标题不含markdown，分三部分（情绪、洼地、风险），结尾引用投资名言。"
    resp = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}], stream=False)
    return resp.choices[0].message.content

# TTS 容错版
async def gen_audio(text, filename):
    print("🎙️ 正在生成语音...")
    try:
        clean = re.sub(r'[\*\#\-]', '', text)
        tts = edge_tts.Communicate(f"欢迎收听 CS2 价值研报。{clean}", "zh-CN-YunxiNeural")
        await tts.save(f"{AUDIO_DIR}/{filename}")
        return True
    except Exception as e:
        print(f"⚠️ 语音生成失败: {e}")
        return False

def save_file(content, audio_name):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    player = ""
    if audio_name:
        player = f"""<div style="background:#f4f4f5;padding:12px;border-radius:8px;margin-bottom:20px;"><div style="font-weight:bold;margin-bottom:8px;">🎧 AI 语音分析 (点击播放)</div><audio controls style="width:100%;"><source src="/audio/{audio_name}" type="audio/mpeg"></audio></div>"""

    md = f"""---
title: {today} 市场量化扫描：寻找价值洼地
date: {now}
tags: [价值投资, CS2量化, 播客]
description: AI 自动扫描全网饰品，分析今日均线偏离度。
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
        success = await gen_audio(report, audio_name)
        final_audio_name = audio_name if success else None
        save_file(report, final_audio_name)

if __name__ == "__main__":
    asyncio.run(main())