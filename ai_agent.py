from dotenv import load_dotenv
import os
from openai import OpenAI

# .env から API キー読み込み
load_dotenv()
api_key = os.getenv("TNSYSTEM1")  # ここは .env に合わせてキー名を統一
print("API Key読み込み:", "成功" if api_key else "失敗")

client = OpenAI(api_key=api_key)

def chat_with_ai(user_input, chat_history, recent_learning, latest_research=None):
    """
    チャットAI：
    - 市場調査アシスタントとして会話する
    - 必要に応じて最新の市場調査結果を参照
    """
    messages = [
        {
            "role": "system",
            "content": (
                "あなたは冷静で戦略的な市場調査アシスタントです。"
                "ユーザーの相談内容に対して、トレンドデータや市場調査結果を踏まえ、"
                "どんな方向性・ビジュアル・訴求が有効かを具体的に助言してください。"
                "ただし画像生成は行わず、助言・分析のみに集中してください。"
            ),
        }
    ]

    # 過去の会話履歴
    for m in chat_history:
        messages.append({"role": m["role"], "content": m["content"]})

    # 学習データ（過去のやり取り）
    for entry in recent_learning:
        messages.append({"role": "assistant", "content": entry.get("bot_response", "")})

    # 最新市場調査データを追加
    if latest_research:
        messages.append({
            "role": "system",
            "content": f"最新の市場調査結果は以下です:\n{latest_research}"
        })

    # 現在のユーザー入力
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=600,
        messages=messages
    )

    return response.choices[0].message.content

