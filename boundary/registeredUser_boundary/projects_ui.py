import logging
from flask import Blueprint, render_template, request, redirect, url_for, session

logger = logging.getLogger(__name__)

projects_bp = Blueprint("projects", __name__)


def get_user_id():
    """Get current user ID from session"""
    return session.get("user_id")


def create_projects_controller():
    """Create a projects controller for the current user"""
    from controller.registeredUser_controller.projects_controller import ProjectsController
    user_id = get_user_id()
    if not user_id:
        return None
    return ProjectsController(user_id)


@projects_bp.get("/dashboard")
def dashboard():
    logger.info("Dashboard accessed (recent projects)")
    
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    controller = create_projects_controller()
    if not controller:
        return redirect(url_for("user.login_get"))
    
    data = controller.view_recent()
    return render_template("projects_dashboard.html", **data)


@projects_bp.get("/projects")
def projects_list():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    query = request.args.get("q")
    logger.info("Projects list accessed (query=%s)", query)
    
    controller = create_projects_controller()
    if not controller:
        return redirect(url_for("user.login_get"))
    
    data = controller.view_all(query)
    return render_template("projects_dashboard.html", **data)


@projects_bp.get("/projects/create")
def projects_create_get():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Create project page accessed")
    return render_template("projects_create.html")


@projects_bp.post("/projects/create")
def projects_create_post():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    
    if not name:
        return render_template("projects_create.html", error="Project name is required.")
    
    controller = create_projects_controller()
    if not controller:
        return redirect(url_for("user.login_get"))
    
    controller.create(name, description)
    return redirect(url_for("projects.projects_list"))


@projects_bp.get("/projects/open/<int:pid>")
def projects_open(pid: int):
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Open project id=%s", pid)
    
    controller = create_projects_controller()
    if not controller:
        return redirect(url_for("user.login_get"))
    
    controller.open(pid)
    # Changed from redirect to data_import to direct redirect to project_sna
    return redirect(url_for("projects.project_sna"))


@projects_bp.post("/projects/rename/<int:pid>")
def projects_rename(pid: int):
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    new_name = request.form.get("new_name", "").strip()
    if new_name:
        controller = create_projects_controller()
        if controller:
            controller.rename(pid, new_name)
    return redirect(url_for("projects.projects_list"))


@projects_bp.post("/projects/archive/<int:pid>")
def projects_archive(pid: int):
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    controller = create_projects_controller()
    if controller:
        controller.archive(pid)
    return redirect(url_for("projects.projects_list"))


@projects_bp.post("/projects/delete/<int:pid>")
def projects_delete(pid: int):
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    controller = create_projects_controller()
    if controller:
        controller.delete(pid)
    return redirect(url_for("projects.projects_list"))


@projects_bp.get("/projects/api-keys")
def api_keys():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("API Keys page accessed")
    return render_template("api_keys.html")


@projects_bp.get("/projects/sna")
def project_sna():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Project SNA page accessed")
    return render_template("project_sna.html")


@projects_bp.get("/projects/sentiment-analysis")
def sentiment_analysis():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Sentiment Analysis page accessed")
    return render_template("sentiment_analysis.html")


@projects_bp.get("/projects/detect-communities")
def detect_communities():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Detect Communities page accessed")
    return render_template("detect_communities.html")


@projects_bp.get("/projects/data-import")
def data_import():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Data Import page accessed")
    return render_template("data_import.html")


@projects_bp.get("/projects/data-monitoring")
def data_monitoring():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Data Monitoring page accessed")
    return render_template("data_monitoring.html")


@projects_bp.get("/projects/historical-analysis")
def historical_analysis():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Historical Analysis page accessed")
    return render_template("historical_analysis.html")


@projects_bp.get("/projects/identify-influencers")
def identify_influencers():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Identify Influencers page accessed")
    return render_template("identify_influencers.html")