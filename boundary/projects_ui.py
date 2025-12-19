import logging
from flask import Blueprint, render_template, request, redirect, url_for
from Controller.projects_controller import projects_controller

logger = logging.getLogger(__name__)

projects_bp = Blueprint("projects", __name__)


@projects_bp.get("/projects")
def projects_dashboard():
    query = request.args.get("q")
    logger.info("Projects dashboard accessed (query=%s)", query)
    data = projects_controller.view_all(query)
    return render_template("projects_dashboard.html", **data)


@projects_bp.get("/projects/create")
def projects_create_get():
    logger.info("Create project page accessed")
    return render_template("projects_create.html")


@projects_bp.post("/projects/create")
def projects_create_post():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        return render_template("projects_create.html", error="Project name is required.")
    projects_controller.create(name, description)
    return redirect(url_for("projects.projects_dashboard"))


@projects_bp.get("/projects/open/<int:pid>")
def projects_open(pid: int):
    logger.info("Open project id=%s", pid)
    projects_controller.open(pid)
    return redirect(url_for("projects.projects_dashboard"))


@projects_bp.post("/projects/rename/<int:pid>")
def projects_rename(pid: int):
    new_name = request.form.get("new_name", "").strip()
    if new_name:
        projects_controller.rename(pid, new_name)
    return redirect(url_for("projects.projects_dashboard"))


@projects_bp.post("/projects/archive/<int:pid>")
def projects_archive(pid: int):
    projects_controller.archive(pid)
    return redirect(url_for("projects.projects_dashboard"))


@projects_bp.post("/projects/delete/<int:pid>")
def projects_delete(pid: int):
    projects_controller.delete(pid)
    return redirect(url_for("projects.projects_dashboard"))


@projects_bp.get("/projects/api-keys")
def api_keys():
    logger.info("API Keys page accessed")
    return render_template("api_keys.html")


@projects_bp.get("/projects/sna")
def project_sna():
    logger.info("Project SNA page accessed")
    return render_template("project_sna.html")


@projects_bp.get("/projects/sentiment-analysis")
def sentiment_analysis():
    logger.info("Sentiment Analysis page accessed")
    return render_template("sentiment_analysis.html")


@projects_bp.get("/projects/detect-communities")
def detect_communities():
    logger.info("Detect Communities page accessed")
    return render_template("detect_communities.html")


@projects_bp.get("/projects/data-monitoring")
def data_monitoring():
    logger.info("Data Monitoring page accessed")
    return render_template("data_monitoring.html")


@projects_bp.get("/projects/historical-analysis")
def historical_analysis():
    logger.info("Historical Analysis page accessed")
    return render_template("historical_analysis.html")


@projects_bp.get("/projects/identify-influencers")
def identify_influencers():
    logger.info("Identify Influencers page accessed")
    return render_template("identify_influencers.html")