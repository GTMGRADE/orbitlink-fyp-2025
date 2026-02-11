import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
from flask import jsonify
from datetime import datetime
from Controller.registeredUser_controller.youtube_analysis_controller import YouTubeAnalysisController
from Controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController

logger = logging.getLogger(__name__)

projects_bp = Blueprint("projects", __name__)


def get_user_id():
    """Get current user ID from session"""
    return session.get("user_id")


def get_current_user():
    """Get current user object from session"""
    from Controller.registeredUser_controller.user_controller import user_controller
    return user_controller.get_user(session.get("user_type"), session.get("user_id"))


def create_projects_controller():
    """Create a projects controller for the current user"""
    from Controller.registeredUser_controller.projects_controller import ProjectsController
    user_id = get_user_id()
    if not user_id:
        return None
    return ProjectsController(user_id)


@projects_bp.get("/dashboard")
def dashboard():
    logger.info("Dashboard accessed - redirecting to projects list")
    # Redirect to projects list to show all projects instead of just 3 recent
    return redirect(url_for("projects.projects_list"))


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
    
    # Get current user for username display
    logger.info("Session data: user_type=%s, user_id=%s", session.get("user_type"), session.get("user_id"))
    user = get_current_user()
    logger.info("User object retrieved: %s", user)
    if user:
        logger.info("User has username attribute: %s", hasattr(user, 'username'))
        if hasattr(user, 'username'):
            data['username'] = user.username
            logger.info("Username passed to template: %s", user.username)
        else:
            logger.warning("User object exists but has no username attribute")
    else:
        logger.warning("Could not get current user for username display")
    
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
    
    logger.info(f"[CREATE PROJECT] Attempting to create project: name='{name}', user_id={get_user_id()}")
    
    if not name:
        return render_template("projects_create.html", error="Project name is required.")
    
    controller = create_projects_controller()
    if not controller:
        return redirect(url_for("user.login_get"))
    
    project = controller.create(name, description)
    if not project:
        logger.warning(f"[CREATE PROJECT] Failed - duplicate name '{name}' for user {get_user_id()}")
        return render_template("projects_create.html", 
                             error=f"A project named '{name}' already exists. Please choose a different name.",
                             name=name,
                             description=description)
    
    logger.info(f"[CREATE PROJECT] Success - created project '{name}' with id {project.id}")
    return redirect(url_for("projects.projects_list"))

@projects_bp.post("/projects/rename/<pid>")
def projects_rename(pid: str):
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    new_name = request.form.get("new_name", "").strip()
    if new_name:
        controller = create_projects_controller()
        if controller:
            result = controller.rename(pid, new_name)
            if not result:
                flash(f"A project named '{new_name}' already exists. Please choose a different name.", "error")
            else:
                flash(f"Project renamed to '{new_name}' successfully.", "success")
    return redirect(url_for("projects.projects_list"))


@projects_bp.post("/projects/archive/<pid>")
def projects_archive(pid: str):
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    controller = create_projects_controller()
    if controller:
        controller.archive(pid)
    return redirect(url_for("projects.projects_list"))


@projects_bp.post("/projects/unarchive/<pid>")
def projects_unarchive(pid: str):
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    controller = create_projects_controller()
    if controller:
        controller.unarchive(pid)
    return redirect(url_for("projects.projects_archived"))


@projects_bp.get("/projects/archived")
def projects_archived():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    controller = create_projects_controller()
    if not controller:
        return redirect(url_for("user.login_get"))
    
    data = controller.view_archived()
    
    # Get current user for username display
    logger.info("Archived page - Session data: user_type=%s, user_id=%s", session.get("user_type"), session.get("user_id"))
    user = get_current_user()
    logger.info("Archived page - User object retrieved: %s", user)
    if user:
        logger.info("Archived page - User has username attribute: %s", hasattr(user, 'username'))
        if hasattr(user, 'username'):
            data['username'] = user.username
            logger.info("Username passed to archived template: %s", user.username)
        else:
            logger.warning("Archived page - User object exists but has no username attribute")
    else:
        logger.warning("Could not get current user for username display in archived")
    
    return render_template("projects_archived.html", **data)


@projects_bp.post("/projects/delete/<pid>")
def projects_delete(pid: str):
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
    return render_template("sentiment_analysis.html", sentiment=sentiment)


@projects_bp.get("/projects/detect-communities")
def detect_communities():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Detect Communities page accessed")
    return render_template("detect_communities.html")


@projects_bp.get("/projects/predictive-analysis")
def predictive_analysis():
    # Check if user is logged in
    if not get_user_id():
        return redirect(url_for("user.login_get"))
    
    logger.info("Predictive Analysis page accessed")
    return render_template("predictive_analysis.html")


@projects_bp.get("/projects/<project_id>/predictive-data")
def get_predictive_data(project_id: str):
    """Get predictive analysis data for a project"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        from services.predictive_analysis import PredictiveAnalysisService
        service = PredictiveAnalysisService(user_id, project_id)
        predictions = service.get_predictions()
        return jsonify(predictions), 200
    except Exception as e:
        logger.error(f"Error getting predictive data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@projects_bp.get("/projects/<project_id>/export-pdf")
def export_analysis_pdf(project_id: str):
    """Export all analyses as a PDF report"""
    user_id = get_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        from services.pdf_export import AnalysisPDFExporter
        from services.predictive_analysis import PredictiveAnalysisService
        from flask import send_file
        
        # Get current session data
        session_controller = AnalysisSessionController(user_id, project_id)
        session_data = session_controller.get_current_session()
        
        if not session_data or not session_data.get('analysis_data'):
            return jsonify({"success": False, "error": "No analysis data available. Please run an analysis first."}), 404
        
        analysis_data = session_data.get('analysis_data', {})
        project_title = session_data.get('channel_title', 'Analysis Report')
        
        # Get all analysis data
        export_data = {
            'sentiment_analysis': analysis_data.get('sentiment_analysis'),
            'influencers': analysis_data.get('influencers', []),
            'community_detection': analysis_data.get('community_detection'),
        }
        
        # Get predictive analysis
        try:
            predictive_service = PredictiveAnalysisService(user_id, project_id)
            predictive_data = predictive_service.get_predictions()
            if predictive_data.get('success'):
                export_data['predictive_analysis'] = predictive_data
        except Exception as e:
            logger.warning(f"Could not include predictive analysis: {str(e)}")
            export_data['predictive_analysis'] = {'has_data': False}
        
        # Generate PDF
        exporter = AnalysisPDFExporter()
        pdf_buffer = exporter.generate_report(project_title, export_data)
        
        # Send file
        filename = f"{project_title.replace(' ', '_')}_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


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

@projects_bp.get("/projects/<project_id>/youtube-analyses")
def get_youtube_analyses(project_id: str):
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
    
    
@projects_bp.get("/projects/<project_id>/current-session")
def get_current_session(project_id: str):
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

@projects_bp.post("/projects/<project_id>/clear-session")
def clear_current_session(project_id: str):
    """Clear current analysis session for a project"""
    logger.info(f"[CLEAR SESSION] Endpoint called for project_id={project_id}")
    user_id = get_user_id()
    if not user_id:
        logger.warning(f"[CLEAR SESSION] No user_id in session")
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        logger.info(f"[CLEAR SESSION] Clearing session for user={user_id}, project={project_id}")
        controller = AnalysisSessionController(user_id, project_id)
        success = controller.clear_session()
        logger.info(f"[CLEAR SESSION] Clear result: {success}")
        return jsonify({"success": success, "message": "Session cleared"}), 200
    except Exception as e:
        logger.error(f"[CLEAR SESSION] Error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@projects_bp.get("/projects/<project_id>/community-data")
def get_community_data(project_id: str):
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
    
# Add this function at the top of the file, after imports
def check_subscription_required():
    """Check if user needs to complete subscription before accessing dashboard"""
    user_id = get_user_id()
    
    if not user_id:
        return True, redirect(url_for("user.login_get"))
    
    # Check if user has subscription
    try:
        from db_config import get_connection
        from bson import ObjectId
        
        db = get_connection()
        if db is None:
            return False, None
        
        try:
            query_id = ObjectId(user_id)
        except:
            query_id = user_id
        
        user_doc = db.users.find_one(
            {"_id": query_id},
            {"subscription_active": 1, "role": 1}
        )
        
        # Admin users don't need subscription
        if user_doc and user_doc.get('role') == 'admin':
            return False, None
        
        # Regular users need subscription
        if user_doc and user_doc.get('subscription_active'):
            return False, None
        
        # User doesn't have subscription, redirect to payment
        return True, redirect(url_for("payment.payment_page"))
        
    except Exception as e:
        logger.error(f"Error checking subscription: {str(e)}")
        return False, None