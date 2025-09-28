import os
import json
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from pytrends.request import TrendReq
from requests.utils import quote
from openai import OpenAI
import schedule
import time
import matplotlib.pyplot as plt
import numpy as np
import threading

# =============================
# 環境変数読み込み
# =============================
load_dotenv()
PIXABAY_API_KEY = os.getenv("TNPIXABAY")
UNSPLASH_API_KEY = os.getenv("TNUNSPLASH")
OPENAI_API_KEY = os.getenv("TNSYSTEM1")
client = OpenAI(api_key=OPENAI_API_KEY)

# =============================
# ディレクトリと学習データ
# =============================
PDCA_DIR = "pdca_reports"
SUMMARY_DIR = "summary_reports"
LEARNING_FILE = "learning_data.json"
os.makedirs(PDCA_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)
if not os.path.exists(LEARNING_FILE):
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

# =============================
# 市場調査対象キーワード
# =============================
TARGET_KEYWORDS = ["fitness", "eco", "travel"]

# =============================
# APIデータ取得
# =============================
def get_pixabay_count(keyword: str) -> int:
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={quote(keyword)}&image_type=photo"
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
        return res.json().get("totalHits", 0)
    return 0

def get_unsplash_count(keyword: str) -> int:
    url = f"https://api.unsplash.com/search/photos?query={quote(keyword)}"
    headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code == 200:
        return res.json().get("total", 0)
    return 0

def get_trends_score(keyword: str) -> int:
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
    data = pytrends.interest_over_time()
    if not data.empty:
        return int(data[keyword].mean())
    return 50

# =============================
# 市場調査実行
# =============================
def run_market_research(keywords=TARGET_KEYWORDS):
    results = []
    for kw in keywords:
        pixabay_hits = get_pixabay_count(kw)
        unsplash_hits = get_unsplash_count(kw)
        trends_score = get_trends_score(kw)
        competition_score = min(100, (pixabay_hits + unsplash_hits) // 1000)
        final_score = max(0, min(100, trends_score - competition_score/2))
        results.append({
            "keyword": kw,
            "pixabay_hits": pixabay_hits,
            "unsplash_hits": unsplash_hits,
            "trends_score": trends_score,
            "competition_score": competition_score,
            "final_score": final_score
        })
    return results

# =============================
# PDCA生成
# =============================
def generate_pdca_report(results):
    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        learning_data = json.load(f)
    recent_history = learning_data[-5:] if len(learning_data) >= 5 else learning_data

    prompt = f"""
あなたは市場調査AIアシスタントです。
過去の学習履歴:
{recent_history}

最新調査結果:
{results}

この情報からPDCAサイクルを生成してください。
出力形式:
原因:
結果:
考察:
改善案:
具体的な行動計画:
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[
            {"role": "system", "content": "あなたは冷静で論理的な市場分析アシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# =============================
# 学習履歴保存
# =============================
def save_learning_entry(user_input, bot_response):
    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input": user_input,
        "bot_response": bot_response
    })
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =============================
# レポート自動保存
# =============================
def daily_task():
    results = run_market_research()
    pdca_text = generate_pdca_report(results)
    filename = f"{PDCA_DIR}/report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 日次市場調査レポート\n\n")
        f.write(str(results)+"\n\n")
        f.write(pdca_text)
    print(f"✅ 日次レポート保存: {filename}")

def summarize_reports(period="monthly"):
    files = sorted(os.listdir(PDCA_DIR))
    if not files:
        print("⚠️ まとめるレポートなし")
        return
    target_files = files[-30:]  # 過去30日分
    content = ""
    for f in target_files:
        with open(os.path.join(PDCA_DIR, f), "r", encoding="utf-8") as file:
            content += f"\n\n=== {f} ===\n\n" + file.read()
    prompt = f"直近の{period}レポートを読み込み、傾向・成果・課題・改善案・行動計画をまとめてください。\n{content}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        messages=[
            {"role": "system", "content": "あなたは冷静で論理的な市場分析アシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )
    summary_text = response.choices[0].message.content
    summary_filename = f"{SUMMARY_DIR}/{period}_{datetime.now().strftime('%Y%m%d')}.md"
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"✅ {period}レポート保存: {summary_filename}")

# =============================
# グラフ化
# =============================
def plot_scores(results):
    labels = [r["keyword"] for r in results]
    trends = [r["trends_score"] for r in results]
    competition = [r["competition_score"] for r in results]
    final = [r["final_score"] for r in results]
    x = np.arange(len(labels))
    plt.figure(figsize=(10,5))
    plt.plot(x, trends, marker='o', label='Trends Score')
    plt.plot(x, competition, marker='o', label='Competition Score')
    plt.plot(x, final, marker='o', label='Final Score')
    plt.xticks(x, labels)
    plt.ylim(0, 100)
    plt.title("市場調査スコア")
    plt.xlabel("キーワード")
    plt.ylabel("スコア")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# =============================
# スケジューラ
# =============================
def run_scheduler():
    # 毎週金曜日 0:00 のみ
    schedule.every().friday.at("00:00").do(daily_task)
    schedule.every(30).days.at("23:55").do(lambda: summarize_reports("monthly"))
    while True:
        schedule.run_pending()
        time.sleep(60)

# バックグラウンドでスケジューラ起動
threading.Thread(target=run_scheduler, daemon=True).start()

# =============================
# Streamlit UI
# =============================
st.set_page_config(page_title="📊 市場調査AIアシスタント", page_icon="📈")
st.title("📊 市場調査 AI チャットボット")

user_input = st.text_input("指示を入力してください:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 会話生成
    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        recent_learning = json.load(f)[-5:]

    conversation_context = st.session_state.chat_history + recent_learning
    prompt_messages = [{"role": "system", "content": "あなたは市場調査アシスタントです。"}]
    for m in conversation_context:
        content = m.get("content") if m.get("content") is not None else ""
        role = "user" if m.get("role")=="user" else "assistant"
        prompt_messages.append({"role": role, "content": content})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=prompt_messages
    )
    bot_output = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": bot_output})
    save_learning_entry(user_input, bot_output)

# 会話表示
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**あなた:** {msg['content']}")
    else:
        st.markdown(f"**ボット:** {msg['content']}")

# 手動で市場調査 & グラフ表示
if st.button("🔹 手動で市場調査実行"):
    manual_results = run_market_research()
    st.write(manual_results)
    plot_scores(manual_results)
    pdca_text = generate_pdca_report(manual_results)
    st.text_area("PDCA分析", pdca_text, height=300)
