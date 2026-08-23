import os

from dotenv import load_dotenv
from flask import Flask

from src.auth.controllers import auth_bp

load_dotenv()
app = Flask(__name__)

app.register_blueprint(auth_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    is_debug = os.environ.get("FLASK_ENV") == "development"

    app.run(debug=is_debug, port=port)
