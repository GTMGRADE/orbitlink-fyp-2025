import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RegisteredUser:
    id: int
    username: str
    email: str
    password_hash: str
    remember_me: bool = field(default=False)


class UserController:
    """Business logic for authentication and account maintenance."""

    def __init__(self) -> None:
        self.users: Dict[str, RegisteredUser] = {
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

    def authenticate(self, user_type: str, username: str, password: str, remember_me: bool) -> dict:
        user = self.users.get(user_type)
        if user and user.username == username and user.password_hash == password:
            user.remember_me = remember_me
            return {
                "status": "success",
                "user": user,
                "user_type": user_type,
                "remember": remember_me,
            }
        return {"status": "failure", "message": "Invalid username or password."}

    def get_user(self, user_type: Optional[str], user_id: Optional[int]) -> Optional[RegisteredUser]:
        user = self.users.get(user_type or "") if user_type else None
        if user and user.id == user_id:
            return user
        return None

    def get_user_by_email(self, email: str) -> Tuple[Optional[str], Optional[RegisteredUser]]:
        for utype, user in self.users.items():
            if user.email == email:
                return utype, user
        return None, None

    def change_username(self, user: RegisteredUser, new_username: str) -> None:
        logger.info("Username changed from '%s' to '%s'", user.username, new_username)
        user.username = new_username

    def change_password(self, user: RegisteredUser, current_password: str, new_password: str) -> dict:
        if user.password_hash != current_password:
            logger.warning("Password change failed for user %s: incorrect current password", user.username)
            return {"status": "failure", "message": "Current password is incorrect."}
        user.password_hash = new_password
        logger.info("Password updated for user %s", user.username)
        return {"status": "success"}

    def reset_password(self, email: str) -> dict:
        user_type, user = self.get_user_by_email(email)
        if not user:
            logger.warning("Password reset requested for non-existent email: %s", email)
            return {
                "status": "failure",
                "message": "If this email exists, a reset link has been sent.",
            }
        logger.info("Password reset requested for email: %s (type=%s)", email, user_type)
        return {
            "status": "success",
            "user_type": user_type,
            "user": user,
            "message": "Password reset link sent.",
        }


def _build_controller() -> UserController:
    return UserController()


user_controller = _build_controller()
