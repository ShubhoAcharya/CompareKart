from diagrams import Diagram
from diagrams.onprem.client import User
from diagrams.programming.framework import Flask
from diagrams.programming.language import Python
from diagrams.aws.database import RDS
from diagrams.custom import Custom

with Diagram("CompareKart Architecture", show=False, filename="comparekart", direction="TB"):
    # User Interface
    user = User("End User")
    frontend = Custom("React UI", "https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg")
    
    # Backend
    backend = Flask("Flask API\n(Python)")
    routes = Python("routes.py\n/process_url\n/set_price_alert")
    
    # Scrapers
    selenium = Custom("Selenium", "https://upload.wikimedia.org/wikipedia/commons/d/d5/Selenium_Logo.png")
    scrapers = [Python("product_data.py"), Python("buyhatke_url.py")]
    
    # Database
    db = RDS("PostgreSQL")
    tables = Custom("Tables\nproducts\nprice_alerts", "https://upload.wikimedia.org/wikipedia/commons/2/29/Postgresql_elephant.svg")
    
    # Workers
    alert_checker = Python("price_alert_checker.py\n(APScheduler)")
    updater = Python("background_updater.py")
    
    # Email
    email = Custom("Email Service", "https://upload.wikimedia.org/wikipedia/commons/4/4c/Mail_Icon.png")
    
    # Connections
    user >> frontend >> backend
    backend >> selenium >> scrapers >> db
    backend >> db
    db >> alert_checker >> email >> user
    db >> updater >> selenium