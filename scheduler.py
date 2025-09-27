import schedule
import time
from datetime import datetime
from app import run_market_research, summarize_reports

# 日次・週次・月次スケジュール
schedule.every().day.at("00:00").do(run_market_research)
schedule.every().friday.at("23:55").do(lambda: summarize_reports("weekly"))
schedule.every(30).days.at("23:55").do(lambda: summarize_reports("monthly"))

print("🚀 AI市場調査エージェントスケジューラ起動")

while True:
    schedule.run_pending()
    time.sleep(60)
