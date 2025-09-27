import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("TNSYSTEM1")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_pdca_report(results):
    prompt = f"""
あなたは市場調査を行うAIアシスタントです。
以下の調査結果を基に、PDCAサイクルを回してください。

調査結果:
{results}

出力フォーマット:
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
