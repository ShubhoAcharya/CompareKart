from flask import Flask
from flask_mail import Mail

mail = Mail()  # Initialize Mail object globally

def create_app():
    app = Flask(__name__)

    # ✅ Configure Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'shubhojit2021@gift.edu.in'  # Replace
    app.config['MAIL_PASSWORD'] = 'jyuc xvhg zkrl cdxl'     # Replace
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    mail.init_app(app)  # Initialize Flask-Mail with the app

    # ✅ Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
