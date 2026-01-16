from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

from db_config import init_db, check_database_status


# unregistered user boundaries
from boundary.guestUser_boundary.landing_ui import landing_bp
from boundary.guestUser_boundary.reviews_ui import reviews_bp
from boundary.guestUser_boundary.register_ui import register_bp

# registered user boundaries
from boundary.registeredUser_boundary.user_ui import user_bp
from boundary.registeredUser_boundary.projects_ui import projects_bp


# admin user boundaries
from boundary.admin_boundary.admin_api_boundary import admin_api_bp
from boundary.admin_boundary.admin_ui_boundary import admin_ui_bp

import logging
import sys 

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'orbitlinkteam@gmail.com')

mail = Mail(app)

app.register_blueprint(landing_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(register_bp)
app.register_blueprint(user_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(admin_api_bp)
app.register_blueprint(admin_ui_bp)

# YouTube API configuration
app.config['YOUTUBE_API_KEY'] = os.getenv('YOUTUBE_API_KEY')
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"

)

if __name__ == '__main__':
    print(" * Running on http://127.0.0.1:5000")
    app.run(debug=True)
    logging.info("Application started")
