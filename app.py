from flask import Flask
from boundary.guestUser_boundary.landing_ui import landing_bp
from boundary.guestUser_boundary.reviews_ui import reviews_bp
from boundary.guestUser_boundary.register_ui import register_bp

from boundary.registeredUser_boundary.user_ui import user_bp
from boundary.registeredUser_boundary.projects_ui import projects_bp
from boundary.admin_boundary.admin_api_boundary import admin_api_bp
from boundary.admin_boundary.admin_ui_boundary import admin_ui_bp
import logging
import sys 

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  

app.register_blueprint(landing_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(register_bp)

app.register_blueprint(user_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(admin_api_bp)
app.register_blueprint(admin_ui_bp)


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"

)



if __name__ == '__main__':
    print(" * Running on http://127.0.0.1:5000")
    app.run(debug=True)

    logging.info("Application started")
    logging.warning("This is a warning")
    logging.error("An error occurred")
