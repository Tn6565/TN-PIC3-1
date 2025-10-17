from dotenv import load_dotenv
import os
from openai import OpenAI

# .env から API キー読み込み
load_dotenv()
api_key = os.getenv("TNSYSTEM1")
print("API Key読み込み:", "成功" if api_key else "失敗")

client = OpenAI(api_key=api_key)

def generate_pdca_report(results):
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
