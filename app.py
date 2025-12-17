from flask import Flask
from boundary.landing_ui import landing_bp
from boundary.reviews_ui import reviews_bp
from boundary.register_ui import register_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Needed for flash messages

app.register_blueprint(landing_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(register_bp)

if __name__ == '__main__':
    app.run(debug=True)