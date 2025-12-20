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
        # Hardcoded admin credentials
        self.hardcoded_admin = {
            "id": 0,
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",  # Simple password
            "role": "admin"
        }

    def authenticate(self, username: str, password: str, remember_me: bool) -> dict:
        """Authenticate user - first check hardcoded admin, then database"""
        
        # 1. first check: Hardcoded Admin
        if (username == self.hardcoded_admin["username"] or 
            username == self.hardcoded_admin["email"]) and \
            password == self.hardcoded_admin["password"]:
            
            user = RegisteredUser(
                id=self.hardcoded_admin["id"],
                username=self.hardcoded_admin["username"],
                email=self.hardcoded_admin["email"],
                password_hash="",  # Not needed for hardcoded
                role=self.hardcoded_admin["role"],
                remember_me=remember_me
            )
            print(f"✅ Logged in as HARDCODED ADMIN")
            return {
                "status": "success",
                "user": user,
                "user_type": "admin",
                "remember": remember_me,
            }
        
        # 2. second check: Database users
        conn = get_connection()
        if not conn:
            return {"status": "failure", "message": "Database connection error."}
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Trying to find user by username or email
            cursor.execute("""
                SELECT id, username, email, password, role 
                FROM users 
                WHERE username = %s OR email = %s
            """, (username, username))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Verifying password using User entity's verify_password method
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
        # Checking hardcoded admin first
        if username == self.hardcoded_admin["username"] or username == self.hardcoded_admin["email"]:
            return "admin"
        
        # Then check database
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
        # Using the same authenticate method
        return self.authenticate(username, password, remember_me)

    def get_user(self, user_type: Optional[str], user_id: Optional[int]) -> Optional[RegisteredUser]:
        if not user_id:
            return None
        
        # Checking if it's the hardcoded admin (id = 0)
        if user_id == 0:
            return RegisteredUser(
                id=0,
                username=self.hardcoded_admin["username"],
                email=self.hardcoded_admin["email"],
                password_hash="",
                role="admin",
                remember_me=False
            )
        
        # Otherwise check database
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
        # Checking hardcoded admin first
        if email == self.hardcoded_admin["email"]:
            user = RegisteredUser(
                id=0,
                username=self.hardcoded_admin["username"],
                email=self.hardcoded_admin["email"],
                password_hash="",
                role="admin",
                remember_me=False
            )
            return "admin", user
        
        # Then check database
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
        # Can't change hardcoded admin username
        if user.id == 0:
            return
        
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
        # Can't change hardcoded admin password via UI
        if user.id == 0:
            return {"status": "failure", "message": "Cannot change hardcoded admin password."}
        
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
            
            # Updating the user object
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
        # Can't reset hardcoded admin password
        if email == self.hardcoded_admin["email"]:
            return {
                "status": "failure",
                "message": "Cannot reset hardcoded admin password.",
            }
        
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