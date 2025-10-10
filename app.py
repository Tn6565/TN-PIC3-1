import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import numpy as np

# =============================
# 環境変数のロード
# =============================
load_dotenv()
OPENAI_API_KEY = os.getenv("TNSYSTEM1")
if not OPENAI_API_KEY:
    st.error("❌ .envにOPENAI_API_KEYが設定されていません。")
    st.stop()

# =============================
# クライアント設定
# =============================
client = OpenAI(api_key=OPENAI_API_KEY)

# =============================
# Streamlit UI
# =============================
st.set_page_config(page_title="市場調査エージェント", layout="wide")
st.title("📊 市場調査 × AIエージェント")

# =============================
# ファイル設定
# =============================
LEARNING_FILE = "learning_data.json"

# =============================
# 初期化
# =============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not os.path.exists(LEARNING_FILE):
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# =============================
# トレンド取得関数
# =============================
def fetch_trends(keyword, retries=5):
    pytrends = TrendReq(hl="ja-JP", tz=540)
    for i in range(retries):
        try:
            pytrends.build_payload([keyword], timeframe="today 3-m", geo="JP")
            data = pytrends.interest_over_time()
            if not data.empty:
                return data
        except Exception as e:
            if "429" in str(e):
                wait = 60
                st.warning(f"⚠️ TooManyRequestsError: {keyword}, {i+1}/{retries} リトライします {wait}秒待機...")
                time.sleep(wait)
            else:
                st.error(f"❌ {keyword} のトレンド取得エラー: {e}")
                break
    st.warning(f"⚠️ 最大リトライ回数に達しました: {keyword}")
    return None

# =============================
# AI応答関数
# =============================
def get_ai_response(user_input):
    # 過去データ読み込み
    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        recent_learning = json.load(f)[-5:]

    conversation_context = st.session_state.chat_history + recent_learning

    prompt_messages = [{"role": "system", "content": "あなたは市場調査アシスタントです。"}]

    # 空データやNoneを除外
    for m in conversation_context:
        role = m.get("role", "user")
        content = m.get("content", "")
        if isinstance(content, str) and content.strip():
            prompt_messages.append({"role": role, "content": content})

    # ユーザー入力を追加
    if isinstance(user_input, str) and user_input.strip():
        prompt_messages.append({"role": "user", "content": user_input})
    else:
        return "(入力が空です)"

    # OpenAI API呼び出し
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=800,
            messages=prompt_messages
        )
        bot_output = response.choices[0].message.content or "(応答がありません)"
        return bot_output
    except Exception as e:
        return f"⚠️ エラー: {e}"

# =============================
# 学習データ保存
# =============================
def save_learning(user, bot):
    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.append({"role": "user", "content": user})
    data.append({"role": "assistant", "content": bot})
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =============================
# Streamlit インターフェース
# =============================
st.sidebar.header("設定")
keyword = st.sidebar.text_input("調査キーワード", "フィットネス")
analyze_btn = st.sidebar.button("市場調査を実行")

if analyze_btn:
    st.session_state.chat_history.append({"role": "user", "content": f"「{keyword}」の市場動向を調べて"} )
    trends = fetch_trends(keyword)
    if trends is not None:
        st.line_chart(trends[keyword])
        ai_summary = get_ai_response(f"キーワード『{keyword}』のGoogleトレンドデータを解析し、トレンド変化の要因を説明して。")
        st.session_state.chat_history.append({"role": "assistant", "content": ai_summary})
        save_learning(f"{keyword}の市場動向分析", ai_summary)
        st.markdown("### 🤖 AI解析結果")
        st.write(ai_summary)
    else:
        st.warning("データ取得に失敗しました。")

# =============================
# チャットセクション
# =============================
st.markdown("---")
st.subheader("💬 戦略コミュニケーション")

user_input = st.text_input("あなたの質問や提案を入力してください:", key="chat_input")
if st.button("送信"):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response = get_ai_response(user_input)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    save_learning(user_input, response)
    st.markdown("**AI:** " + response)

# 履歴表示
st.markdown("### 📚 会話履歴")
for msg in st.session_state.chat_history[-10:]:
    role = "🧑 あなた" if msg["role"] == "user" else "🤖 AI"
    st.write(f"**{role}:** {msg['content']}")
