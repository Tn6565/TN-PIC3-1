import os, json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

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
            {"role": "system", "content": "冷静で論理的な市場分析アシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def summarize_reports(period="30days"):
    report_dir = "pdca_reports"
    files = sorted([f for f in os.listdir(report_dir) if f.endswith(".json")])
    if not files:
        print("⚠️ レポートなし")
        return

    if period == "30days":
        target_files = files[-30:]
    else:
        target_files = files

    combined = []
    for f in target_files:
        with open(f"{report_dir}/{f}", "r", encoding="utf-8") as file:
            combined += json.load(file)

    summary_filename = f"summary_reports/summary_{datetime.now().strftime('%Y%m%d')}.md"
    os.makedirs("summary_reports", exist_ok=True)

    prompt = f"""
あなたは市場調査の分析アシスタントです。
直近{period}の調査結果を基に、総合的にPDCAを回してください。
{combined}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        messages=[
            {"role": "system", "content": "冷静で論理的な市場分析アシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )
    summary_text = response.choices[0].message.content
    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"✅ PDCAまとめを保存: {summary_filename}")
    return summary_text
