import streamlit as st
import os
import json
from dotenv import load_dotenv
from market_research import run_market_research
from pdca_agent import generate_pdca_report
from datetime import datetime
from openai import OpenAI

# =============================
# ページ設定（ファビコン）
# =============================
st.set_page_config(
    page_title="AI市場調査エージェント",
    page_icon="favicon.png",  # TN-PIC3-1/ に favicon.png を置いてください
    layout="wide"
)

# =============================
# 環境変数の読み込み
# =============================
load_dotenv()
OPENAI_API_KEY = os.getenv("TNSYSTEM1")
client = OpenAI(api_key=OPENAI_API_KEY)

# =============================
# チャット履歴をセッションに保存
# =============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =============================
# UI
# =============================
st.title("🤖 AI市場調査エージェント")
st.write("会話形式で市場調査をサポートします。")

# チャット表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 入力欄
if prompt := st.chat_input("メッセージを入力してください..."):
    # ユーザー入力を履歴に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # =============================
    # 特殊コマンド判定
    # =============================
    if "市場調査" in prompt:
        with st.chat_message("assistant"):
            st.markdown("市場調査を開始します...")

        # 市場調査を実行
        results = run_market_research()
        pdca_text = generate_pdca_report(results)

        # 結果をまとめる
        response_text = f"""
### 📊 市場調査結果
{json.dumps(results, ensure_ascii=False, indent=2)}

### 🔄 PDCA分析
{pdca_text}
"""
    else:
        # 通常の会話は OpenAI API に任せる
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=[
                {"role": "system", "content": "あなたは市場調査とマーケティングを支援するアシスタントです。"},
                *st.session_state.messages
            ]
        )
        response_text = response.choices[0].message.content

    # 応答を履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # 表示
    with st.chat_message("assistant"):
        st.markdown(response_text)

