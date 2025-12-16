import logging
from dataclasses import dataclass, field

from flask import Blueprint, render_template, request, redirect, url_for, session

logger = logging.getLogger(__name__)

# User data model
@dataclass
class RegisteredUser:
    id: int
    username: str
    email: str
    password_hash: str
    remember_me: bool = field(default=False)


demo_user = RegisteredUser(
    id=1,
    username="john_doe",
    email="john@example.com",
    password_hash="hashedPassword"
)


def get_current_user():
    """Retrieves the current logged-in user from session."""
    user_id = session.get("user_id")
    if user_id == demo_user.id:
        return demo_user
    return None


user_bp = Blueprint('user', __name__)


# ---------- LOG IN + REMEMBER ME ----------
@user_bp.get("/login")
def login_get():
    """Displays the login page."""
    logger.info("Login page accessed")
    return render_template("login.html")


@user_bp.post("/login")
def login_post():
    """Handles login form submission with optional remember me functionality."""
    username = request.form.get("username")
    password = request.form.get("password")
    remember_me = request.form.get("remember_me")

    if username != demo_user.username:
        logger.warning(f"Failed login attempt with username: {username}")
        return render_template("login.html", error="Invalid username or password.")

    session["user_id"] = demo_user.id
    demo_user.remember_me = remember_me is not None
    session.permanent = demo_user.remember_me
    logger.info(f"User {username} logged in successfully")

    return redirect(url_for("user.profile"))


# ---------- VIEW PERSONAL PROFILE ----------
@user_bp.get("/profile")
def profile():
    """Displays the user's personal profile page."""
    user = get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    message = request.args.get("message")
    logger.info(f"Profile page accessed by user: {user.username}")
    return render_template("profile.html", user=user, message=message)


# ---------- RESET PASSWORD ----------
@user_bp.get("/reset-password")
def reset_password_get():
    """Displays the reset password page."""
    logger.info("Reset password page accessed")
    return render_template("reset_password.html")


@user_bp.post("/reset-password")
def reset_password_post():
    """Handles password reset form submission."""
    email = request.form.get("email")
    if email == demo_user.email:
        message = "A password reset link has been sent to your email."
        logger.info(f"Password reset requested for email: {email}")
    else:
        message = "If this email exists, a reset link has been sent."
        logger.warning(f"Password reset requested for non-existent email: {email}")
    return render_template("reset_password.html", message=message)


# ---------- CHANGE USERNAME ----------
@user_bp.get("/change-username")
def change_username_get():
    """Displays the change username page."""
    user = get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    logger.info(f"Change username page accessed by user: {user.username}")
    return render_template("change_username.html", current_username=user.username)


@user_bp.post("/change-username")
def change_username_post():
    """Handles username change form submission."""
    user = get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))

    new_username = request.form.get("new_username")
    old_username = user.username
    user.username = new_username
    logger.info(f"Username changed from '{old_username}' to '{new_username}'")

    return redirect(url_for("user.profile", message="Username updated successfully."))


# ---------- CHANGE PASSWORD ----------
@user_bp.get("/change-password")
def change_password_get():
    """Displays the change password page."""
    user = get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    logger.info(f"Change password page accessed by user: {user.username}")
    return render_template("change_password.html")


@user_bp.post("/change-password")
def change_password_post():
    """Handles password change form submission."""
    user = get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")

    user.password_hash = "hashed:" + new_password
    logger.info(f"Password changed for user: {user.username}")
    return redirect(url_for("user.profile", message="Password changed successfully."))


# ---------- LOG OUT ----------
@user_bp.get("/logout")
def logout():
    """Logs out the current user by clearing the session."""
    logger.info("User logged out")
    session.clear()
    return redirect(url_for("user.login_get"))
