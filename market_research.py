import os
import requests
from requests.utils import quote
from pytrends.request import TrendReq

PIXABAY_API_KEY = os.getenv("TNPIXABAY")
UNSPLASH_API_KEY = os.getenv("TNUNSPLASH")

TARGET_KEYWORDS = ["fitness", "eco", "travel"]

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
