from flask import Flask
from boundary.landing_ui import landing_bp
from boundary.user_ui import user_bp

app = Flask(__name__, template_folder='templates')
app.secret_key = "change-this-secret-key"
app.register_blueprint(landing_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)