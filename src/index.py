import os

from dotenv import load_dotenv
from flask import Flask, render_template

from src.admin_management.controllers import admin_bp
from src.auth.controllers import auth_bp
from src.common.exceptions import register_error_handlers
from src.cv_management.controllers import cv_bp
from src.job_management.controllers import job_bp
from src.ung_vien.controllers import ung_vien_bp

load_dotenv()
app = Flask(__name__)

register_error_handlers(app)

app.register_blueprint(auth_bp)
app.register_blueprint(cv_bp)
app.register_blueprint(ung_vien_bp)
app.register_blueprint(job_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/cv")
def cv_management_page():
    return render_template("cv-management.html")


@app.route("/thong-tin-ca-nhan")
def profile_page():
    return render_template("profile.html")


@app.route("/cv/preview")
def cv_preview_page():
    return render_template("cv_preview.html")


@app.route("/jobs")
def job_management_page():
    return render_template("job-management.html")


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


if __name__ == "__main__":
    from livereload import Server

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    server = Server(app.wsgi_app)
    server.watch("src/**/*")

    port = int(os.environ.get("PORT", 5000))
    is_debug = os.environ.get("FLASK_ENV") == "development"

    server.serve(port=port)
