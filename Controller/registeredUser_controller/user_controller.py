import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from db_config import get_connection
from entity.user import User
import bcrypt

logger = logging.getLogger(__name__)


@dataclass
class RegisteredUser:
    id: str  # Changed from int to str for MongoDB ObjectId compatibility
    username: str
    email: str
    password_hash: str
    role: str = "user"  # Default role if not specified
    remember_me: bool = field(default=False)


class UserController:
    """Business logic for authentication and account maintenance."""

    def __init__(self) -> None:
        # Hardcoded admin credentials
        self.hardcoded_admin = {
            "id": "0",  # String ID for consistency with MongoDB
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
                password_hash="",
                role="admin",
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
        db = get_connection()
        if db is None:
            return {"status": "failure", "message": "Database connection error."}
        
        try:
            # Check if user is suspended FIRST
            suspended_user = db.users.find_one({
                "$or": [{"username": username}, {"email": username}],
                "status": "suspended"
            })
            
            if suspended_user:
                return {
                    "status": "failure", 
                    "message": "Your account has been suspended. Please contact support for further assistance."
                }
            
            # Then check for active users
            user_data = db.users.find_one({
                "$or": [{"username": username}, {"email": username}],
                "status": "active"
            })
            
            if user_data:
                # Verifying password using User entity's verify_password method
                if User.verify_password(user_data['password'], password):
                    user = RegisteredUser(
                        id=str(user_data['_id']),
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=user_data['password'],
                        role=user_data.get('role', 'user'),
                        remember_me=remember_me
                    )
                    return {
                        "status": "success",
                        "user": user,
                        "user_type": user_data.get('role', 'user'),
                        "remember": remember_me,
                    }
            
            return {"status": "failure", "message": "Invalid username or password."}
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {"status": "failure", "message": "Authentication error."}

    def resolve_user_type_by_username(self, username: str) -> Optional[str]:
        # Checking hardcoded admin first
        if username == self.hardcoded_admin["username"] or username == self.hardcoded_admin["email"]:
            return "admin"
        
        # Then check database
        db = get_connection()
        if db is None:
            return None
        
        try:
            user_data = db.users.find_one(
                {"$or": [{"username": username}, {"email": username}]},
                {"role": 1}
            )
            return user_data.get('role') if user_data else None
        except Exception as e:
            logger.error(f"Error resolving user type: {str(e)}")
            return None

    def authenticate_auto(self, username: str, password: str, remember_me: bool) -> dict:
        """Authenticate without an explicit user type."""
        # Using the same authenticate method
        return self.authenticate(username, password, remember_me)

    def get_user(self, user_type: Optional[str], user_id: Optional[str]) -> Optional[RegisteredUser]:
        if not user_id:
            return None
        
        # Checking if it's the hardcoded admin (id = "0")
        if user_id == "0" or user_id == 0:
            return RegisteredUser(
                id="0",
                username=self.hardcoded_admin["username"],
                email=self.hardcoded_admin["email"],
                password_hash="",
                role="admin",
                remember_me=False
            )
        
        # Otherwise check database
        db = get_connection()
        if db is None:
            return None
        
        try:
            from bson import ObjectId
            try:
                query_id = ObjectId(user_id)
            except:
                query_id = user_id
            
            # Query only by _id (do not filter by role)
            # Regular users don't have a role field, so we just match by ID
            query = {"_id": query_id}
            
            user_data = db.users.find_one(query)
            
            if user_data:
                return RegisteredUser(
                    id=str(user_data['_id']),
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password'],
                    role=user_data.get('role', 'user'),
                    remember_me=False
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    def get_user_by_email(self, email: str) -> Tuple[Optional[str], Optional[RegisteredUser]]:
        # Checking hardcoded admin first
        if email == self.hardcoded_admin["email"]:
            user = RegisteredUser(
                id="0",
                username=self.hardcoded_admin["username"],
                email=self.hardcoded_admin["email"],
                password_hash="",
                role="admin",
                remember_me=False
            )
            return "admin", user
        
        # Then check database
        db = get_connection()
        if db is None:
            return None, None
        
        try:
            user_data = db.users.find_one({"email": email})
            
            if user_data:
                user = RegisteredUser(
                    id=str(user_data['_id']),
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password'],
                    role=user_data.get('role', 'user'),
                    remember_me=False
                )
                return user_data.get('role'), user
            return None, None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None, None

    def change_username(self, user: RegisteredUser, new_username: str) -> None:
        # Can't change hardcoded admin username
        if user.id == 0 or user.id == "0":
            return
        
        db = get_connection()
        if db is None:
            return
        
        try:
            from bson import ObjectId
            try:
                query_id = ObjectId(user.id)
            except:
                query_id = user.id
            
            db.users.update_one(
                {"_id": query_id},
                {"$set": {"username": new_username}}
            )
            logger.info("Username changed from '%s' to '%s'", user.username, new_username)
            user.username = new_username
        except Exception as e:
            logger.error(f"Error changing username: {str(e)}")

    def change_password(self, user: RegisteredUser, current_password: str, new_password: str) -> dict:
        # Can't change hardcoded admin password via UI
        if user.id == 0 or user.id == "0":
            return {"status": "failure", "message": "Cannot change hardcoded admin password."}
        
        # First verify current password
        if not User.verify_password(user.password_hash, current_password):
            logger.warning("Password change failed for user %s: incorrect current password", user.username)
            return {"status": "failure", "message": "Current password is incorrect."}
        
        # Hash new password
        new_hashed_password = User.hash_password(new_password)
        
        db = get_connection()
        if db is None:
            return {"status": "failure", "message": "Database error."}
        
        try:
            from bson import ObjectId
            try:
                query_id = ObjectId(user.id)
            except:
                query_id = user.id
            
            db.users.update_one(
                {"_id": query_id},
                {"$set": {"password": new_hashed_password}}
            )
            
            # Updating the user object
            user.password_hash = new_hashed_password
            logger.info("Password updated for user %s", user.username)
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return {"status": "failure", "message": "Database error."}

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
        
        # Check if user is suspended
        db = get_connection()
        if db is None:
            return {"status": "failure", "message": "Database error."}
        
        try:
            user_doc = db.users.find_one({"email": email}, {"status": 1})
            
            if user_doc and user_doc.get('status') == 'suspended':
                return {
                    "status": "failure",
                    "message": "Your account has been suspended. Please contact support for further assistance.",
                }
        except Exception as e:
            logger.error(f"Error checking user status: {str(e)}")
        
        logger.info("Password reset requested for email: %s (type=%s)", email, user_type)
        return {
            "status": "success",
            "user_type": user_type,
            "user": user,
            "message": "Password reset link sent.",
        }

    def delete_account(self, user: RegisteredUser) -> dict:
        """Delete a user account from the database"""
        # Can't delete hardcoded admin account
        if user.id == "0" or user.id == 0:
            return {"status": "failure", "message": "Cannot delete admin account."}
        
        db = get_connection()
        if db is None:
            return {"status": "failure", "message": "Database connection error."}
        
        try:
            from bson import ObjectId
            try:
                query_id = ObjectId(user.id)
            except:
                query_id = user.id
            
            # Delete the user document from the database
            result = db.users.delete_one({"_id": query_id})
            
            if result.deleted_count > 0:
                logger.info("Account deleted for user: %s (id=%s)", user.username, user.id)
                return {"status": "success", "message": "Account deleted successfully."}
            else:
                logger.warning("Account deletion failed for user: %s (id=%s) - user not found", user.username, user.id)
                return {"status": "failure", "message": "Account not found."}
                
        except Exception as e:
            logger.error(f"Error deleting account for user {user.username}: {str(e)}")
            return {"status": "failure", "message": f"Error deleting account: {str(e)}"}


def _build_controller() -> UserController:
    return UserController()


user_controller = _build_controller()