import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from src.admin_management.controllers import admin_bp
from src.auth.controllers import auth_bp
from src.common.exceptions import register_error_handlers
from src.cv_management.controllers import cv_bp
from src.cv_screening.controllers import screening_bp
from src.job_management.controllers import job_bp
from src.ung_vien.controllers import ung_vien_bp

load_dotenv()
app = Flask(__name__)

register_error_handlers(app)

@app.errorhandler(404)
def page_not_found(e):
    # API endpoints
    if request.path.startswith("/api/"):
        return jsonify({"message": "Not Found"}), 404
    # Web views
    return render_template("404.html"), 404

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(cv_bp)
app.register_blueprint(ung_vien_bp)
app.register_blueprint(job_bp)
app.register_blueprint(screening_bp)


@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools_json():
    return "", 204


from flask import send_from_directory

@app.route("/favicon.ico")
def favicon():
    # Giả sử file favicon.ico nằm trong src/static/img/
    return send_from_directory(os.path.join(app.root_path, "static", "img"), "favicon.ico", mimetype="image/vnd.microsoft.icon")


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


@app.route("/jobs/<int:tin_id>")
def job_detail_page(tin_id: int):
    return render_template("job-detail.html", tin_id=tin_id)


@app.route("/lich-su-ung-tuyen")
def applied_jobs_page():
    return render_template("applied-jobs.html")


@app.route("/screening")
def screening_page():
    return render_template("cv-screening.html")


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
