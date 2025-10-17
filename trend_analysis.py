import requests
from pytrends.request import TrendReq
from requests.utils import quote
import matplotlib.pyplot as plt
import numpy as np
import os
import time

# === 設定 ===
PIXABAY_API_KEY = os.getenv("TNPIXABAY")
UNSPLASH_API_KEY = os.getenv("TNUNSPLASH")
TARGET_KEYWORDS = ["fitness", "eco", "travel"]

# === 画像数取得 ===
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

# === Googleトレンドスコア取得 ===
def get_trends_score(keyword: str) -> int:
    try:
        # リトライ + バックオフ付き
        pytrends = TrendReq(hl='en-US', tz=360, retries=5, backoff_factor=10)
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
        data = pytrends.interest_over_time()
        if not data.empty:
            return int(data[keyword].mean())
        return 50
    except Exception as e:
        print(f"[WARN] Google Trends取得失敗 ({keyword}): {e}")
        return 50

# === 市場調査の実行 ===
def run_market_research(keywords=TARGET_KEYWORDS):
    results = []
    for kw in keywords:
        print(f"🔍 調査中: {kw}")
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
        print(f"✅ 完了: {kw}（次のキーワードまで60秒待機）\n")
        time.sleep(60)  # ★ Google制限対策：1分待機
    return results

# === スコアグラフ ===
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
    plt.show()
