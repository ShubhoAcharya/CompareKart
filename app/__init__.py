import os
import threading
from flask import Flask
from flask_mail import Mail
from flask_cors import CORS

mail = Mail()

def create_app():
    app = Flask(__name__)

    CORS(app)

    # Configuration from environment variables with defaults
    app.config.update(
        MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
        MAIL_USERNAME=os.getenv('MAIL_USERNAME', 'Shubhojit2021@gift.edu.in'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD','jyuc xvhg zkrl cdxl'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', 'comparekart@example.com'),
        BASE_URL=os.getenv('BASE_URL', 'http://localhost:5000'),
        SQLALCHEMY_POOL_SIZE=10,
        SQLALCHEMY_MAX_OVERFLOW=20,
        SQLALCHEMY_POOL_TIMEOUT=30
    )

    mail.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Only start background thread in production
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from app.background_updater import start_background_updater
        start_background_updater(app)

    return app