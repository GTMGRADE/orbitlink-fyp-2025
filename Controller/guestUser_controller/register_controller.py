import logging
from db_config import get_connection
from entity.user import User
from datetime import datetime

logger = logging.getLogger(__name__)

class RegisterController:
    def __init__(self):
        self.conn = get_connection()

    def register_user(self, email, username, password):
        """Register a new user in the database using MongoDB"""
        try:
            # Check database connection using 'is None' instead of boolean evaluation
            if self.conn is None:
                return False, "Database connection failed", None
            
            # Check if email already exists
            if self.conn.users.find_one({"email": email}):
                return False, "Email already registered", None
            
            # Check if username already exists
            if self.conn.users.find_one({"username": username}):
                return False, "Username already taken", None
            
            # Create user with hashed password
            user = User.create_user(email, username, password)
            
            # Insert into MongoDB database
            user_doc = {
                "email": user.email,
                "username": user.username,
                "password": user.password,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            result = self.conn.users.insert_one(user_doc)
            
            # Get the created user
            user_data = self.conn.users.find_one({"_id": result.inserted_id})
            
            # Format response
            formatted_user = {
                "id": str(user_data["_id"]),
                "email": user_data["email"],
                "username": user_data["username"],
                "created_at": user_data.get("created_at"),
                "status": user_data.get("status", "active")
            }
            
            logger.info(f"User registered successfully: {username} ({email})")
            return True, "Registration successful", formatted_user
            
        except Exception as e:
            error_msg = type(e).__name__ + ": " + str(e)
            logger.error(f"Error registering user: {error_msg}")
            return False, f"Registration failed: {error_msg}", None
    
    def get_register_page_data(self):
        """Get data for the register page"""
        return {
            'page_title': 'Register - OrbitLink',
            'hero_text': 'Map your networks.\nMaster your data.'
        }