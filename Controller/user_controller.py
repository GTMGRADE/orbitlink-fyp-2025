import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from db_config import get_connection
from entity.user import User
import bcrypt

logger = logging.getLogger(__name__)


@dataclass
class RegisteredUser:
    id: int
    username: str
    email: str
    password_hash: str
    role: str
    remember_me: bool = field(default=False)


class UserController:
    """Business logic for authentication and account maintenance."""

    def __init__(self) -> None:
        pass  # Remove hardcoded users

    def authenticate(self, username: str, password: str, remember_me: bool) -> dict:
        """Authenticate user from database"""
        conn = get_connection()
        if not conn:
            return {"status": "failure", "message": "Database connection error."}
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Try to find user by username or email
            cursor.execute("""
                SELECT id, username, email, password, role 
                FROM users 
                WHERE username = %s OR email = %s
            """, (username, username))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Verify password using User entity's verify_password method
                if User.verify_password(user_data['password'], password):
                    user = RegisteredUser(
                        id=user_data['id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=user_data['password'],
                        role=user_data['role'],
                        remember_me=remember_me
                    )
                    return {
                        "status": "success",
                        "user": user,
                        "user_type": user_data['role'],
                        "remember": remember_me,
                    }
            
            return {"status": "failure", "message": "Invalid username or password."}
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {"status": "failure", "message": "Authentication error."}
        finally:
            cursor.close()
            conn.close()

    def resolve_user_type_by_username(self, username: str) -> Optional[str]:
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role FROM users WHERE username = %s OR email = %s
            """, (username, username))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error resolving user type: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()

    def authenticate_auto(self, username: str, password: str, remember_me: bool) -> dict:
        """Authenticate without an explicit user type."""
        # Use the same authenticate method
        return self.authenticate(username, password, remember_me)

    def get_user(self, user_type: Optional[str], user_id: Optional[int]) -> Optional[RegisteredUser]:
        if not user_id:
            return None
        
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            if user_type:
                cursor.execute("""
                    SELECT id, username, email, password, role 
                    FROM users 
                    WHERE id = %s AND role = %s
                """, (user_id, user_type))
            else:
                cursor.execute("""
                    SELECT id, username, email, password, role 
                    FROM users 
                    WHERE id = %s
                """, (user_id,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                return RegisteredUser(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password'],
                    role=user_data['role'],
                    remember_me=False
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_by_email(self, email: str) -> Tuple[Optional[str], Optional[RegisteredUser]]:
        conn = get_connection()
        if not conn:
            return None, None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, email, password, role 
                FROM users 
                WHERE email = %s
            """, (email,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                user = RegisteredUser(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password'],
                    role=user_data['role'],
                    remember_me=False
                )
                return user_data['role'], user
            return None, None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None, None
        finally:
            cursor.close()
            conn.close()

    def change_username(self, user: RegisteredUser, new_username: str) -> None:
        conn = get_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET username = %s WHERE id = %s
            """, (new_username, user.id))
            conn.commit()
            logger.info("Username changed from '%s' to '%s'", user.username, new_username)
            user.username = new_username
        except Exception as e:
            logger.error(f"Error changing username: {str(e)}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def change_password(self, user: RegisteredUser, current_password: str, new_password: str) -> dict:
        # First verify current password
        if not User.verify_password(user.password_hash, current_password):
            logger.warning("Password change failed for user %s: incorrect current password", user.username)
            return {"status": "failure", "message": "Current password is incorrect."}
        
        # Hash new password
        new_hashed_password = User.hash_password(new_password)
        
        conn = get_connection()
        if not conn:
            return {"status": "failure", "message": "Database error."}
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password = %s WHERE id = %s
            """, (new_hashed_password, user.id))
            conn.commit()
            
            # Update the user object
            user.password_hash = new_hashed_password
            logger.info("Password updated for user %s", user.username)
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            conn.rollback()
            return {"status": "failure", "message": "Database error."}
        finally:
            cursor.close()
            conn.close()

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