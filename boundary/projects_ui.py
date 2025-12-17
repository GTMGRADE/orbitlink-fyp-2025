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
