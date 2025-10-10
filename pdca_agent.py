import json

LEARNING_FILE = "learning_data.json"

def generate_pdca_report(results, client):
    # 過去学習履歴を取得
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
