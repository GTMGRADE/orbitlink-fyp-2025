from flask import Flask
from boundary.landing_ui import landing_bp
from boundary.reviews_ui import reviews_bp
from boundary.register_ui import register_bp

from boundary.user_ui import user_bp
from boundary.projects_ui import projects_bp
from boundary.admin_api_boundary import admin_api_bp
from boundary.admin_ui_boundary import admin_ui_bp
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
    app.run(debug=True)

    logging.info("Application started")
    logging.warning("This is a warning")
    logging.error("An error occurred")
