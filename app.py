from flask import Flask
from boundary.landing_ui import landing_bp
from boundary.admin_ui_boundary import admin_ui_bp
from boundary.admin_api_boundary import admin_api_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-here' 

app.register_blueprint(landing_bp)
app.register_blueprint(admin_ui_bp)
app.register_blueprint(admin_api_bp)

if __name__ == '__main__':
    app.run(debug=True)