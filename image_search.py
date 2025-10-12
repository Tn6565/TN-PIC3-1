import os
import requests
from requests.utils import quote

PIXABAY_API_KEY = os.getenv("TNPIXABAY")
UNSPLASH_API_KEY = os.getenv("TNUNSPLASH")

def search_images(keyword):
    pixabay_url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={quote(keyword)}&image_type=photo"
    unsplash_url = f"https://api.unsplash.com/search/photos?query={quote(keyword)}"
    headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
    pixabay_res = requests.get(pixabay_url).json()
    unsplash_res = requests.get(unsplash_url, headers=headers).json()
    return {
        "pixabay_total": pixabay_res.get("totalHits", 0),
        "unsplash_total": unsplash_res.get("total", 0)
    }
