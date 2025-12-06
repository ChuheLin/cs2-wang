import os
import json
import datetime
import requests
import feedparser
from openai import OpenAI

# ================= 配置区域 =================
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
BULK_API_URL = "http://csgobackpack.net/api/GetItemsList/v2/?currency=CNY"

# 【量化筛选参数】
MIN_VOLUME_SOLD = 15      # 24小时销量至少要卖出15个 (过滤掉没人买的冷门垃圾)
MIN_PRICE_CNY = 10        # 价格至少10元 (过滤掉几分钱的垃圾饰品)
MAX_PRICE_CNY = 20000     # 价格上限 (太贵的通常数据不准)

# ================= 1. 获取全网数据 (大数据) =================
def get_bulk_data():
    print("🌍 正在连接全球饰品数据库 (数据量较大，请耐心等待)...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0"
    }
    try:
        response = requests.get(BULK_API_URL, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('items_list', {})
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
    return {}

# ================= 2. 全市场量化扫描 (核心算法) =================
def scan_whole_market(items):
    print(f"🔍 正在扫描 {len(items)} 个饰品，寻找价值洼地...")
    
    undervalued_list = [] # 被低估的 (跌破均线)
    overheated_list = []  # 过热的 (远超均线)
    
    for name, details in items.items():
        try:
            # 1. 安全性检查：数据是否完整
            if 'price' not in details or '24_hours' not in details['price'] or '30_days' not in details['price']:
                continue
            
            # 2. 提取核心指标
            price_now = details['price']['24_hours'].get('average', 0)
            if price_now == 0: price_now = details['price']['24_hours'].get('median', 0)
            
            price_30d = details['price']['30_days'].get('average', 0)
            volume = details['price']['24_hours'].get('sold', 0)
            
            # 如果是字符串类型的销量，尝试转成数字
            if isinstance(volume, str):
                volume = int(volume.replace(',', '')) if volume.isdigit() else 0

            # 3. 过滤器 (只看流动性好的资产，不看死盘)
            if volume < MIN_VOLUME_SOLD or price_now < MIN_PRICE_CNY or price_now > MAX_PRICE_CNY:
                continue
            
            if price_30d <= 0: continue

            # 4. 计算价值偏离度 (段永平逻辑：价格回归均值)
            # 负数代表当前价格低于30日均价 (低估)
            # 正数代表当前价格高于30日均价 (高估)
            deviation = ((price_now - price_30d) / price_30d) * 100
            
            item_info = {
                "name": name,
                "price": price_now,
                "avg_30d": price_30d,
                "deviation": deviation,
                "volume": volume
            }
            
            if deviation < -5: # 跌幅超过 5%
                undervalued_list.append(item_info)
            elif deviation > 10: # 涨幅超过 10%
                overheated_list.append(item_info)
                
        except Exception:
            continue

    # 5. 排序：找出偏离最严重的 Top 10
    # 按跌幅排序 (越小越前)
    top_undervalued = sorted(undervalued_list, key=lambda x: x['deviation'])[:8]
    # 按涨幅排序 (越大越前)
    top_overheated = sorted(overheated_list, key=lambda x: x['deviation'], reverse=True)[:8]
    
    return top_undervalued, top_overheated

# ================= 3. 格式化数据给 AI =================
def format_data_for_ai(undervalued, overheated):
    report = "【全市场量化扫描结果】\n\n"
    
    report += "📉 **深度低估区 (黄金坑?)** - 价格严重低于30日均线:\n"
    for i in undervalued:
        report += f"- {i['name']}: 现价¥{i['price']:.1f} (较均线 {i['deviation']:.1f}%) | 日销量 {i['volume']}\n"
        
    report += "\n🔥 **极度过热区 (风险警示)** - 价格远超30日均线:\n"
    for i in overheated:
        report += f"- {i['name']}: 现价¥{i['price']:.1f} (较均线 +{i['deviation']:.1f}%) | 日销量 {i['volume']}\n"
        
    return report

# ================= 4. 获取新闻 =================
def get_news():
    try:
        feed = feedparser.parse("https://www.hltv.org/rss/news")
        return "\n".join([f"- {entry.title}" for entry in feed.entries[:3]])
    except:
        return "暂无重大新闻"

# ================= 5. DeepSeek 价值投资分析 =================
def run_ai_analysis(news, market_data_str):
    if not API_KEY: return "Error: No API Key"
    print("🧠 DeepSeek 正在分析全市场异动...")
    
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    system_prompt = """
    你是一位不仅精通 CS2 市场，更深谙"段永平/巴菲特"价值投资哲学的顶级分析师。
    你的数据来源是全市场扫描，你需要从"存量增量"和"均值回归"的角度撰写研报。

    **分析逻辑：**
    1. **对于低估区 (Undervalued)**：
       - 分析是"错杀"还是"价值毁灭"？如果是个好东西（比如热门AK），现在打折就是买入机会（击球区）。
       - 如果是冷门垃圾，提醒用户不要接飞刀。
    2. **对于过热区 (Overheated)**：
       - 提醒风险。引用段永平的话："太贵的东西，再好我也不买"。
       - 分析是否是因为短期炒作（如职业选手带货）。
    
    **文章结构要求：**
    1. **【今日市场体温】**：基于涨跌榜单，判断市场情绪是贪婪还是恐慌。
    2. **【捡钱时刻：被低估的优质资产】**：从低估名单里挑 1-2 个你觉得也是"好生意"的饰品进行深度点评。
    3. **【风险预警：击鼓传花】**：点评过热名单，警告追高风险。
    4. **【大道至简】**：一段关于"长期持有"或"不做空"的投资哲学感悟。
    5. **【免责声明】**。
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"日期: {today}\n新闻:\n{news}\n\n{market_data_str}"}
        ],
        stream=False
    )
    return response.choices[0].message.content

# ================= 6. 保存 =================
def save(content):
    if not content: return
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"""---
title: {today} 全市场量化扫描：寻找被错杀的黄金资产
date: {time_now}
tags: [量化分析, 价值投资, CS2大数据]
categories: 深度研报
description: Python 脚本遍历全网 20,000+ 饰品，基于 30 日均线偏离度，筛选出今日最具性价比的"击球区"资产。
---

{content}
"""
    filename = f"source/_posts/{today}-quant-report.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"✅ 研报生成完毕: {filename}")

if __name__ == "__main__":
    # 1. 下载全网数据
    all_items = get_bulk_data()
    # 2. 跑量化筛选算法
    undervalued, overheated = scan_whole_market(all_items)
    # 3. 格式化数据
    data_str = format_data_for_ai(undervalued, overheated)
    # 4. 抓新闻
    news = get_news()
    # 5. AI 写文章
    report = run_ai_analysis(news, data_str)
    # 6. 保存
    save(report)