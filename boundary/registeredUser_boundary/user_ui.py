import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from controller.registeredUser_controller.user_controller import user_controller

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__)


def _get_current_user():
    """Returns the current user object from the session, if present."""
    return user_controller.get_user(session.get("user_type"), session.get("user_id"))


@user_bp.get("/login")
def login_get():
    logger.info("Login page accessed")
    return render_template("login.html")


@user_bp.post("/login")
def login_post():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    remember_me_flag = request.form.get("remember_me") is not None

    # Auto-detect user type based on entered username/email
    login_result = user_controller.authenticate_auto(username, password, remember_me_flag)

    if login_result["status"] == "success":
        user = login_result.get("user")
        session["user_id"] = user.id if user else None
        session["user_type"] = login_result.get("user_type")
        session.permanent = login_result.get("remember", False)
        logger.info(
            "User %s (%s) logged in successfully (remember_me=%s)",
            username,
            session.get("user_type"),
            session.permanent,
        )
        if session.get("user_type") == "admin":
            return redirect(url_for("admin_ui.admin_users_page"))
        return redirect(url_for("projects.projects_list"))

    logger.warning("Failed login attempt with username: %s", username)
    return render_template("login.html", error=login_result.get("message"))

@user_bp.get("/profile")
def profile():
    # Check if user is logged in
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user.login_get"))
    
    # For admin users
    if session.get("user_type") == "admin":
        # Admin should use admin profile or redirect to admin home
        return redirect(url_for("admin_ui.admin_users_page"))
    
    # For regular users
    try:
        # Get user directly from database
        from db_config import get_connection
        from bson import ObjectId
        
        db = get_connection()
        if db is None:
            return redirect(url_for("user.login_get"))
        
        # Convert user_id to ObjectId if needed
        try:
            query_id = ObjectId(user_id)
        except:
            query_id = user_id
        
        user_doc = db.users.find_one({"_id": query_id})
        
        if not user_doc:
            return redirect(url_for("user.login_get"))
        
        # Convert to dictionary format expected by template
        user_data = {
            'id': str(user_doc['_id']),
            'username': user_doc.get('username', ''),
            'email': user_doc.get('email', ''),
            'created_at': user_doc.get('created_at'),
            'status': user_doc.get('status', 'active')
        }
        
        message = request.args.get("message")
        logger.info("Profile page accessed by user: %s", user_data['username'])
        return render_template("profile.html", user=user_data, message=message)
        
    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        return redirect(url_for("user.login_get"))


@user_bp.get("/reset-password")
def reset_password_get():
    logger.info("Reset password page accessed")
    return render_template("reset_password.html")


@user_bp.post("/reset-password")
def reset_password_post():
    email = request.form.get("email")
    reset_result = user_controller.reset_password(email)

    if reset_result["status"] == "success":
        user = reset_result.get("user")
        session["user_id"] = user.id if user else None
        session["user_type"] = reset_result.get("user_type")
        return redirect(url_for("user.profile", message=reset_result.get("message")))

    return render_template("reset_password.html", message=reset_result.get("message"))


@user_bp.get("/change-username")
def change_username_get():
    user = _get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    logger.info("Change username page accessed by user: %s", user.username)
    return render_template("change_username.html", current_username=user.username)


@user_bp.post("/change-username")
def change_username_post():
    user = _get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))

    new_username = request.form.get("new_username", "").strip()
    if new_username:
        user_controller.change_username(user, new_username)
        logger.info("Username changed for type %s", session.get("user_type"))
        return redirect(url_for("user.profile", message="Username updated successfully."))

    return render_template("change_username.html", current_username=user.username, error="Please enter a username.")


@user_bp.get("/change-password")
def change_password_get():
    user = _get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    logger.info("Change password page accessed by user: %s", user.username)
    return render_template("change_password.html")


@user_bp.post("/change-password")
def change_password_post():
    user = _get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    result = user_controller.change_password(user, current_password, new_password)

    if result["status"] == "success":
        return redirect(url_for("user.profile", message="Password changed successfully."))

    return render_template("change_password.html", error=result.get("message"))


@user_bp.get("/logout")
def logout():
    logger.info("User logged out")
    session.clear()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for("landing.landing_page"))


@user_bp.post("/delete-account")
def delete_account():
    """Delete the current user's account"""
    user = _get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    
    try:
        result = user_controller.delete_account(user)
        
        if result["status"] == "success":
            # Clear session after successful deletion
            session.clear()
            logger.info("Account deleted for user: %s", user.username)
            # Flash success message
            flash('Your account has been successfully deleted. We hope to see you again!', 'success')
            # Redirect to landing page
            return redirect(url_for("landing.landing_page"))
        else:
            # If deletion failed, redirect back to profile with error message
            logger.warning("Failed to delete account for user: %s - %s", user.username, result.get("message"))
            flash(f"Error: {result.get('message')}", 'error')
            return redirect(url_for("user.profile"))
    
    except Exception as e:
        logger.error(f"Error in delete account route: {str(e)}")
        flash(f"Error deleting account: {str(e)}", 'error')
        return redirect(url_for("user.profile"))