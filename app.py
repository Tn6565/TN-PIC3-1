import streamlit as st
from data_manager import load_learning_data, save_learning_entry
from report_generator import generate_pdca_report
from trend_analysis import run_market_research, plot_scores
from ai_agent import chat_with_ai

st.set_page_config(page_title="📊 市場調査AIアシスタント", page_icon="📈")
st.title("📊 市場調査 AI チャットボット")

# セッション状態初期化
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "latest_research" not in st.session_state:
    st.session_state.latest_research = None

# ユーザー入力
user_input = st.text_input("💬 あなたの質問や相談を入力してください:")

# チャット処理
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    recent_learning = load_learning_data()[-5:]
    latest_research = st.session_state.latest_research

    # 会話生成（市場調査結果をコンテキストに渡す）
    bot_output = chat_with_ai(
        user_input,
        st.session_state.chat_history,
        recent_learning,
        latest_research
    )

    st.session_state.chat_history.append({"role": "assistant", "content": bot_output})
    save_learning_entry(user_input, bot_output)

# チャット履歴表示
st.markdown("### 💬 会話履歴")
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**あなた:** {msg['content']}")
    else:
        st.markdown(f"**AI:** {msg['content']}")

# 手動市場調査ボタン
st.markdown("---")
st.markdown("### 🔍 市場調査の実行")
if st.button("🔹 手動で市場調査実行"):
    results = run_market_research()
    st.session_state.latest_research = results

    st.success("✅ 市場調査を完了しました。最新データをAIが参照できます。")
    st.write(results)
    plot_scores(results)

    pdca_text = generate_pdca_report(results)
    st.text_area("PDCA分析", pdca_text, height=300)
