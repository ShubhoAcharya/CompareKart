# scheduler.py
import time
from apscheduler.schedulers.background import BackgroundScheduler
from app.price_alert_checker import check_price_alerts

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_price_alerts, 'interval', minutes=15)
    scheduler.start()
    
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()