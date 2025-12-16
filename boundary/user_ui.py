import logging
from dataclasses import dataclass, field

from flask import Blueprint, render_template, request, redirect, url_for, session

logger = logging.getLogger(__name__)


# -------------------- DOMAIN MODEL --------------------
@dataclass
class RegisteredUser:
    id: int
    username: str
    email: str
    password_hash: str  # demo only: using plain text for simplicity
    remember_me: bool = field(default=False)


# Demo credentials per actor from the diagrams
DEMO_USERS = {
    "business": RegisteredUser(
        id=1,
        username="regbusiness",
        email="business@example.com",
        password_hash="bizpass",
    ),
    "influencer": RegisteredUser(
        id=2,
        username="reginfluencer",
        email="influencer@example.com",
        password_hash="influencerpass",
    ),
}


def get_current_user():
    """Retrieves the current logged-in user from session based on actor type."""
    user_type = session.get("user_type")
    user_id = session.get("user_id")
    user = DEMO_USERS.get(user_type)
    if user and user.id == user_id:
        return user
    return None


def get_user_by_email(email: str) -> tuple[str, RegisteredUser] | tuple[None, None]:
    for utype, u in DEMO_USERS.items():
        if u.email == email:
            return utype, u
    return None, None


# -------------------- BUSINESS LAYER --------------------
class BusinessUserService:
    """Encapsulates user authentication and account operations per actor."""

    def __init__(self, users: dict[str, RegisteredUser]):
        self.users = users

    def _get_user(self, user_type: str) -> RegisteredUser | None:
        return self.users.get(user_type)

    def authenticate(self, user_type: str, username: str, password: str) -> bool:
        user = self._get_user(user_type)
        return bool(user and username == user.username and password == user.password_hash)

    def authenticate_with_remember(self, user_type: str, username: str, password: str, remember_me: bool) -> bool:
        user = self._get_user(user_type)
        if not user:
            return False
        authenticated = self.authenticate(user_type, username, password)
        user.remember_me = remember_me if authenticated else False
        return authenticated


# -------------------- CONTROLLER LAYER --------------------
class UserLoginController:
    """Controller mirrors the login sequence diagrams."""

    def __init__(self, user_service: BusinessUserService):
        self.user_service = user_service

    def authenticate(self, user_type: str, username: str, password: str) -> dict:
        if self.user_service.authenticate(user_type, username, password):
            return {"status": "success", "persistent_session": False}
        return {"status": "failure", "message": "Invalid username or password."}

    def handle_login(self, user_type: str, username: str, password: str, remember_me: bool = False) -> dict:
        if self.user_service.authenticate_with_remember(user_type, username, password, remember_me):
            return {
                "status": "success",
                "user_type": user_type,
                "persistent_session": remember_me,
                "message": "Logged in successfully.",
            }
        return {"status": "failure", "message": "Invalid username or password."}


user_service = BusinessUserService(DEMO_USERS)
login_controller = UserLoginController(user_service)


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
    user_type = request.form.get("user_type", "business")
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    remember_me_flag = request.form.get("remember_me") is not None

    login_result = login_controller.handle_login(user_type, username, password, remember_me_flag)

    if login_result["status"] == "success":
        matched_user = DEMO_USERS.get(user_type)
        session["user_id"] = matched_user.id if matched_user else None
        session["user_type"] = user_type
        session.permanent = login_result.get("persistent_session", False)
        logger.info(
            "User %s (%s) logged in successfully (remember_me=%s)",
            username,
            user_type,
            session.permanent,
        )
        # Diagram: redirect to dashboard after successful login; using profile as dashboard placeholder
        return redirect(url_for("user.profile"))

    logger.warning("Failed login attempt with username: %s", username)
    return render_template("login.html", error=login_result.get("message"))


# ---------- VIEW PERSONAL PROFILE ----------
@user_bp.get("/profile")
def profile():
    """Displays the user's personal profile page."""
    user = get_current_user()
    if not user:
        return redirect(url_for("user.login_get"))
    message = request.args.get("message")
    logger.info("Profile page accessed by user: %s", user.username)
    return render_template("profile.html", user=user, message=message, user_type=session.get("user_type"))


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
    user_type, user = get_user_by_email(email)

    if user:
        # Ensure session reflects the user so we can land on profile
        session["user_id"] = user.id
        session["user_type"] = user_type
        logger.info("Password reset requested for email: %s (type=%s)", email, user_type)
        return redirect(url_for("user.profile", message="Password reset link sent."))

    logger.warning("Password reset requested for non-existent email: %s", email)
    return render_template("reset_password.html", message="If this email exists, a reset link has been sent.")


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
    logger.info("Username changed from '%s' to '%s' for type %s", old_username, new_username, session.get("user_type"))

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
    if current_password != user.password_hash:
        logger.warning("Password change failed for user %s: wrong current password", user.username)
        return render_template("change_password.html", error="Current password is incorrect.")

    user.password_hash = new_password
    logger.info(f"Password changed for user: {user.username}")
    return redirect(url_for("user.profile", message="Password changed successfully."))


# ---------- LOG OUT ----------
@user_bp.get("/logout")
def logout():
    """Logs out the current user by clearing the session."""
    logger.info("User logged out")
    session.clear()
    return redirect(url_for("user.login_get"))
