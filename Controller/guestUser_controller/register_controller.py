import logging
from db_config import get_connection
from entity.user import User
<<<<<<< HEAD
<<<<<<< HEAD
import mysql.connector
=======
from datetime import datetime
>>>>>>> feature/Simon
=======
from datetime import datetime
>>>>>>> development

logger = logging.getLogger(__name__)

class RegisterController:
    def __init__(self):
<<<<<<< HEAD
<<<<<<<< HEAD:Controller/guestUser_controller/register_controller.py
        self.conn = get_connection()

    def register_user(self, email, username, password):
        """Register a new user in the database"""
========
        self.db = get_connection()
    
    def register_user(self, email, username, password, role=None):
        """
        Register a new user in the database
        Returns: (success, message, user_data)
        """
>>>>>>>> development:Controller/register_controller.py
        try:
<<<<<<< HEAD
            if not self.conn:
                return False, "Database connection failed", None
            
            cursor = self.conn.cursor(dictionary=True)
=======
            # Check database connection using 'is not None' instead of truthy evaluation
            if self.db is None:
                return False, "Database connection error", None
>>>>>>> feature/Simon
            
            # Check if email already exists
            if self.db.users.find_one({"email": email}):
                return False, "Email already registered", None
            
            # Check if username already exists
            if self.db.users.find_one({"username": username}):
                return False, "Username already taken", None
            
<<<<<<<< HEAD:Controller/guestUser_controller/register_controller.py
            # Create user with hashed password (no role parameter)
            user = User.create_user(email, username, password)
            
            # Insert into database without role
            cursor.execute("""
                INSERT INTO users (email, username, password)
                VALUES (%s, %s, %s)
            """, (user.email, user.username, user.password))
========
            # Create user with hashed password
            user = User.create_user(email, username, password)
            
            # Insert into database
=======
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
>>>>>>> development
            user_doc = {
                "email": user.email,
                "username": user.username,
                "password": user.password,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
<<<<<<< HEAD
>>>>>>>> development:Controller/register_controller.py
            
            if role:
                user_doc["role"] = role
            
            result = self.db.users.insert_one(user_doc)
            
            # Get the created user
            user_data = self.db.users.find_one({"_id": result.inserted_id})
=======
            
            result = self.conn.users.insert_one(user_doc)
            
            # Get the created user
            user_data = self.conn.users.find_one({"_id": result.inserted_id})
>>>>>>> development
            
            # Format response
            formatted_user = {
                "id": str(user_data["_id"]),
                "email": user_data["email"],
                "username": user_data["username"],
                "created_at": user_data.get("created_at"),
                "status": user_data.get("status", "active")
            }
<<<<<<< HEAD
            if "role" in user_data:
                formatted_user["role"] = user_data["role"]
            
<<<<<<< HEAD
            logger.info(f"Registration Controller : User registered successfully: {username} ({email})")
            print("Registration Controller : User registered successfully") 
            return True, "Registration successful", user_data
=======
            logger.info(f"User registered successfully: {username} ({email})")
            return True, "Registration successful", formatted_user
>>>>>>> feature/Simon
            
        except mysql.connector.Error as e:
            logger.error(f"Database error registering user: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
        except Exception as e:
<<<<<<< HEAD
            logger.error(f"Error registering user: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
        finally:
            if 'cursor' in locals():
                cursor.close()
=======
            error_msg = type(e).__name__ + ": " + str(e)
            logger.error(f"Error registering user: {error_msg}")
            return False, f"Registration failed: {error_msg}", None
>>>>>>> feature/Simon
=======
            
            logger.info(f"Registration Controller : User registered successfully: {username} ({email})")
            print("Registration Controller : User registered successfully") 
            return True, "Registration successful", formatted_user
            
        except Exception as e:
            error_msg = type(e).__name__ + ": " + str(e)
            logger.error(f"Error registering user: {error_msg}")
            return False, f"Registration failed: {error_msg}", None
>>>>>>> development
    
    
    def get_register_page_data(self):
        """Get data for the register page"""
        return {
            'page_title': 'Register - OrbitLink',
            'hero_text': 'Map your networks.\nMaster your data.'
        }