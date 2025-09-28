import schedule, time, threading
from market_research import run_market_research
from pdca_agent import generate_pdca_report, summarize_reports

def scheduled_tasks():
    schedule.every().friday.at("00:00").do(run_market_research)
    schedule.every().friday.at("00:05").do(lambda: generate_pdca_report(run_market_research()))
    schedule.every().friday.at("00:10").do(lambda: summarize_reports("30days"))

    while True:
        schedule.run_pending()
        time.sleep(60)

t = threading.Thread(target=scheduled_tasks, daemon=True)
t.start()
