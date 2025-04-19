from flask import Flask
from flask_mail import Mail
from flask_cors import CORS  # ⬅️ Add this line

mail = Mail()

def create_app():
    app = Flask(__name__)

    # ✅ Enable CORS
    CORS(app)  # ⬅️ This enables CORS for all routes

    # ✅ Flask-Mail config (already present)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'Shubhojit2021@gift.edu.in'
    app.config['MAIL_PASSWORD'] = 'jyuc xvhg zkrl cdxl'
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    mail.init_app(app)

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
