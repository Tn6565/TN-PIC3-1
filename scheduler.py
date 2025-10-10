import schedule
import time
from market_research import run_market_research
from pdca_agent import generate_pdca_report

PDCA_DIR = "pdca_reports"

def daily_task():
    results = run_market_research()
    pdca_text = generate_pdca_report(results)
    filename = f"{PDCA_DIR}/report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 市場調査レポート\n\n")
        f.write(str(results)+"\n\n")
        f.write(pdca_text)
    print(f"✅ レポート保存: {filename}")

def start_scheduler():
    schedule.every().friday.at("00:00").do(daily_task)
    while True:
        schedule.run_pending()
        time.sleep(60)
