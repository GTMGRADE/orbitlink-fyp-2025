# boundary/registeredUser_boundary/review_ui.py
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from Controller.registeredUser_controller.review_controller import ReviewController
from Controller.registeredUser_controller.user_controller import user_controller

logger = logging.getLogger(__name__)

review_bp = Blueprint("review", __name__)

def get_user_id():
    """Get current user ID from session"""
    return session.get("user_id")

def get_current_user():
    """Get current user from session and database"""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_controller.get_user(session.get("user_type"), user_id)

@review_bp.route("/review")
def review_page():
    """Review submission page for registered users"""
    user_id = get_user_id()
    
    if not user_id:
        return redirect(url_for("user.login_get"))
    
    # Get current user from database to get username
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("user.login_get"))
    
    controller = ReviewController(user_id, current_user.username)
    data = controller.get_review_page_data()
    
    return render_template("review_submit.html", **data)

@review_bp.route("/review/submit", methods=["POST"])
def submit_review():
    """Handle review submission"""
    user_id = get_user_id()
    
    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login to submit a review"
        }), 401
    
    # Get current user from database
    current_user = get_current_user()
    if not current_user:
        return jsonify({
            "success": False,
            "message": "Please login to submit a review"
        }), 401
    
    rating = request.form.get("rating")
    comment = request.form.get("comment", "").strip()
    
    if not rating:
        return jsonify({
            "success": False,
            "message": "Please select a rating"
        }), 400
    
    controller = ReviewController(user_id, current_user.username)
    success, message = controller.submit_review(rating, comment)
    
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "redirect": url_for("review.review_page")
        })
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 400
    
