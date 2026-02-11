import logging

from flask import Blueprint, render_template, request, redirect, url_for, session

from controller.user_controller import user_controller

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
    user = _get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    message = request.args.get("message")
    logger.info("Profile page accessed by user: %s", user.username)
    return render_template("profile.html", user=user, message=message, user_type=session.get("user_type"))


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
    return redirect(url_for("landing.landing_page"))