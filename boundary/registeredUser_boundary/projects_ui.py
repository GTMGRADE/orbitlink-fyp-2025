import logging
from flask import Blueprint, render_template, request, redirect, url_for, session
import json
from flask import jsonify
<<<<<<< HEAD
from controller.registeredUser_controller.youtube_analysis_controller import YouTubeAnalysisController
from controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController
=======
from Controller.registeredUser_controller.youtube_analysis_controller import YouTubeAnalysisController
from Controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController
>>>>>>> development

logger = logging.getLogger(__name__)

projects_bp = Blueprint("projects", __name__)


def get_user_id():
    """Get current user ID from session"""
    return session.get("user_id")


def create_projects_controller():
    """Create a projects controller for the current user"""
<<<<<<< HEAD
    from controller.registeredUser_controller.projects_controller import ProjectsController
=======
    from Controller.registeredUser_controller.projects_controller import ProjectsController
>>>>>>> development
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

<<<<<<< HEAD
@projects_bp.post("/projects/rename/<int:pid>")
def projects_rename(pid: int):
=======
@projects_bp.post("/projects/rename/<pid>")
def projects_rename(pid: str):
>>>>>>> development
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    new_name = request.form.get("new_name", "").strip()
    if new_name:
        controller = create_projects_controller()
        if controller:
            controller.rename(pid, new_name)
    return redirect(url_for("projects.projects_list"))


<<<<<<< HEAD
@projects_bp.post("/projects/archive/<int:pid>")
def projects_archive(pid: int):
=======
@projects_bp.post("/projects/archive/<pid>")
def projects_archive(pid: str):
>>>>>>> development
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    controller = create_projects_controller()
    if controller:
        controller.archive(pid)
    return redirect(url_for("projects.projects_list"))


<<<<<<< HEAD
@projects_bp.post("/projects/delete/<int:pid>")
def projects_delete(pid: int):
=======
@projects_bp.post("/projects/delete/<pid>")
def projects_delete(pid: str):
>>>>>>> development
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
    
<<<<<<< HEAD
    logger.info("Project SNA page accessed")
    return render_template("project_sna.html")
=======
    # Get project_id from query params if provided
    project_id = request.args.get("project_id") or request.args.get("pid")
    
    logger.info("Project SNA page accessed (project_id=%s)", project_id or "none")
    return render_template("project_sna.html", project_id=project_id)
>>>>>>> development


@projects_bp.get("/projects/sentiment-analysis")
def sentiment_analysis():
    # Check if user is logged in
<<<<<<< HEAD
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Sentiment Analysis page accessed")
    return render_template("sentiment_analysis.html")
=======
    user_id = get_user_id()
    if not user_id:
        return redirect(url_for("user.login_get"))

    # Try to fetch sentiment from current session for a given project
    pid = request.args.get("project_id") or request.args.get("pid")
    print(f"[ROUTE] Sentiment analysis requested for project_id: {pid}")
    
    sentiment = None
    if pid:
        try:
            controller = AnalysisSessionController(user_id, pid)
            session_data = controller.get_current_session()
            
            if session_data:
                print(f"[ROUTE] Session data found. Keys: {list(session_data.keys())}")
                if session_data.get("analysis_data"):
                    print(f"[ROUTE] Analysis data keys: {list(session_data['analysis_data'].keys())}")
                    sentiment = session_data["analysis_data"].get("sentiment_analysis")
                    if sentiment:
                        print(f"[ROUTE] Sentiment found. Keys: {list(sentiment.keys())}")
                        print(f"[ROUTE] Overall score: {sentiment.get('overall_score')}")
                        print(f"[ROUTE] Pie chart exists: {bool(sentiment.get('pie_chart'))}")
                        print(f"[ROUTE] Word cloud exists: {bool(sentiment.get('word_cloud'))}")
                        if sentiment.get('pie_chart'):
                            print(f"[ROUTE] Pie chart size: {len(sentiment.get('pie_chart', ''))} bytes")
                        if sentiment.get('word_cloud'):
                            print(f"[ROUTE] Word cloud size: {len(sentiment.get('word_cloud', ''))} bytes")
                    else:
                        print(f"[ROUTE] WARNING: No sentiment_analysis in analysis_data")
                else:
                    print(f"[ROUTE] WARNING: No analysis_data in session")
            else:
                print(f"[ROUTE] WARNING: No session data found for project {pid}")
        except Exception as e:
            logger.warning("Failed to load sentiment for project %s: %s", pid, e)
            print(f"[ROUTE] Exception: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"[ROUTE] WARNING: No project_id provided")

    logger.info("Sentiment Analysis page accessed (project_id=%s)", pid or "none")
    print(f"[ROUTE] Final sentiment object being passed to template: {sentiment is not None}")
    return render_template("sentiment_analysis.html", sentiment=sentiment)
>>>>>>> development


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

@projects_bp.post("/projects/analyze-youtube")
def analyze_youtube():
    """Handle YouTube channel or video analysis request"""
    # Check if user is logged in
    user_id = get_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    data = request.get_json()
    youtube_url = data.get('youtube_url') or data.get('channel_url')  # Support both field names
    project_id = data.get('project_id')
    
    if not youtube_url or not project_id:
        return jsonify({"success": False, "error": "Missing YouTube URL or project ID"}), 400
    
    try:
        controller = YouTubeAnalysisController(user_id, project_id)
        result = controller.analyze_youtube(youtube_url)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": "Analysis completed successfully",
                "data": result['data']
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Analysis failed')
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Analysis error: {str(e)}"
        }), 500

@projects_bp.get("/projects/<int:project_id>/youtube-analyses")
def get_youtube_analyses(project_id):
    """Get recent YouTube analyses for a project"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        controller = YouTubeAnalysisController(user_id, project_id)
        analyses = controller.get_recent_analyses()
        return jsonify({"success": True, "analyses": analyses}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
    
@projects_bp.get("/projects/<int:project_id>/current-session")
def get_current_session(project_id):
    """Get current analysis session for a project"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        controller = AnalysisSessionController(user_id, project_id)
        session = controller.get_current_session()
        return jsonify(session), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@projects_bp.post("/projects/<int:project_id>/clear-session")
def clear_current_session(project_id):
    """Clear current analysis session for a project"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        controller = AnalysisSessionController(user_id, project_id)
        success = controller.clear_session()
        return jsonify({"success": success}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

<<<<<<< HEAD
@projects_bp.get("/projects/open/<int:pid>")
def projects_open(pid: int):
=======
@projects_bp.get("/projects/<int:project_id>/community-data")
def get_community_data(project_id):
    """Get community detection data for a project"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        from services.community_detector import CommunityDetector
        detector = CommunityDetector()
        data = detector.get_community_data(project_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@projects_bp.get("/projects/open/<pid>")
def projects_open(pid: str):
>>>>>>> development
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Open project id=%s", pid)
    
    controller = create_projects_controller()
    if not controller:
        return redirect(url_for("user.login_get"))
    
    controller.open(pid)
    # Pass project_id when redirecting to project_sna
    return redirect(url_for("projects.project_sna", project_id=pid))
    
    