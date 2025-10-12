import streamlit as st
from data_manager import load_learning_data, save_learning_entry
from report_generator import generate_pdca_report, summarize_reports
from trend_analysis import run_market_research, plot_scores
from ai_agent import chat_with_ai

st.set_page_config(page_title="📊 市場調査AIアシスタント", page_icon="📈")
st.title("📊 市場調査 AI チャットボット")

# ユーザー入力用
user_input = st.text_input("指示を入力してください:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    # 会話生成
    recent_learning = load_learning_data()[-5:]
    bot_output = chat_with_ai(user_input, st.session_state.chat_history, recent_learning)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_output})
    save_learning_entry(user_input, bot_output)

# 会話履歴表示
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**あなた:** {msg['content']}")
    else:
        st.markdown(f"**ボット:** {msg['content']}")

# 手動市場調査ボタン
if st.button("🔹 手動で市場調査実行"):
    results = run_market_research()
    st.write(results)
    plot_scores(results)
    pdca_text = generate_pdca_report(results)
    st.text_area("PDCA分析", pdca_text, height=300)
