from ai_agent import client

def generate_pdca_report(results):
    recent_history = []
    prompt = f"""
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

def summarize_reports(period="weekly"):
    return "集計まとめ処理（ファイル読み込みや分析）"
