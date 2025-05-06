import atexit
import os
from flask import Flask
from flask_mail import Mail
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from app.price_alert_checker import check_price_alerts

# Move mail initialization here
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'Shubhojit2021@gift.edu.in')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'jyuc xvhg zkrl cdxl')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'comparekart@example.com')
    app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5000')

    mail.init_app(app)

    # Start scheduler only if not in debug mode or in main thread
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            lambda: app.app_context().push() or check_price_alerts(app),
            'interval',
            minutes=15
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app