from flask import Flask
from boundary.landing_ui import landing_bp

app = Flask(__name__)
app.register_blueprint(landing_bp)

if __name__ == '__main__':
    app.run(debug=True)