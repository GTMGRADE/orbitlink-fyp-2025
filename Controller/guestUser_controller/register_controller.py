import logging
from db_config import get_connection
from entity.user import User
import mysql.connector

logger = logging.getLogger(__name__)

class RegisterController:
    def __init__(self):
        self.conn = get_connection()

    def register_user(self, email, username, password, role):
        """Register a new user in the database"""
        try:
            if not self.conn:
                return False, "Database connection failed", None
            
            cursor = self.conn.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Email already registered", None
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already taken", None
            
            # Create user with hashed password (no role parameter)
            user = User.create_user(email, username, password)
            
            # Insert into database without role
            cursor.execute("""
                INSERT INTO users (email, username, password)
                VALUES (%s, %s, %s)
            """, (user.email, user.username, user.password))
            
            self.conn.commit()
            user_id = cursor.lastrowid
            
            # Get the created user
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            logger.info(f"Registration Controller : User registered successfully: {username} ({email})")
            print("Registration Controller : User registered successfully") 
            return True, "Registration successful", user_data
            
        except mysql.connector.Error as e:
            logger.error(f"Database error registering user: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    
    def get_register_page_data(self):
        """Get data for the register page"""
        return {
            'page_title': 'Register - OrbitLink',
            'hero_text': 'Map your networks.\nMaster your data.'
        }