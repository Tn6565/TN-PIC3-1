import json
from datetime import datetime

LEARNING_FILE = "learning_data.json"

def load_learning_data():
    try:
        with open(LEARNING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_learning_entry(user_input, bot_response):
    data = load_learning_data()
    data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input": user_input,
        "bot_response": bot_response
    })
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
