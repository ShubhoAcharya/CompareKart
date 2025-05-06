import time
from apscheduler.schedulers.background import BackgroundScheduler
from app import create_app
from app.price_alert_checker import check_price_alerts

def start_scheduler():
    app = create_app()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: app.app_context().push() or check_price_alerts(),
        'interval',
        minutes=15
    )
    scheduler.start()
    
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()