from db_config import get_connection

class LoginError(Exception):
    """Raised when login credentials are invalid."""
    pass


class AccountEntity:
    """
    Entity for account operations using database.
    """

    def __init__(self, email: str, role: str):
        self.email = email
        self.role = role

    @classmethod
    def authenticate(cls, email: str, password: str) -> "AccountEntity":
        """Authenticate admin user - with hardcoded admin support"""
        
        # 1. FIRST CHECK: Hardcoded Admin
        if email == "admin@example.com" and password == "admin123":
            return cls(email=email, role="admin")
        
        # 2. SECOND CHECK: Database admin
<<<<<<< HEAD
        conn = get_connection()
        if not conn:
            raise LoginError("Database connection error.")
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT email, role FROM users 
                WHERE email = %s AND role = 'admin'
            """, (email,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Verify password
                cursor.execute("""
                    SELECT password FROM users 
                    WHERE email = %s AND role = 'admin'
                """, (email,))
                password_data = cursor.fetchone()
                
                if password_data:
                    from entity.user import User
                    if User.verify_password(password_data['password'], password):
                        return cls(email=user_data['email'], role=user_data['role'])
=======
        db = get_connection()
        if db is None:
            raise LoginError("Database connection error.")
        
        try:
            # Find admin user by email
            user_data = db.users.find_one(
                {"email": email, "role": "admin"},
                {"email": 1, "role": 1, "password": 1}
            )
            
            if user_data:
                from entity.user import User
                if User.verify_password(user_data['password'], password):
                    return cls(email=user_data['email'], role=user_data['role'])
>>>>>>> feature/Simon
            
            raise LoginError("Invalid email or password.")
            
        except Exception as e:
            raise LoginError(f"Authentication error: {str(e)}")
<<<<<<< HEAD
        finally:
            cursor.close()
            conn.close()
=======
>>>>>>> feature/Simon

    def to_dict(self) -> dict:
        return {"email": self.email, "role": self.role}

    # User account operations
    @classmethod
    def retrieve_user_accounts(cls) -> list[dict]:
        """Retrieve all user accounts from database"""
<<<<<<< HEAD
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username as name, email, status 
                FROM users 
                WHERE id != 0  # Exclude hardcoded admin
                ORDER BY id
            """)
            
            users = cursor.fetchall()
            
            # Format the status for display
            for user in users:
                user['status'] = user['status'].capitalize()
            
            return users
=======
        db = get_connection()
        if db is None:
            return []
        
        try:
            # Find all users, exclude hardcoded admin by checking for specific email
            users = list(db.users.find(
                {"email": {"$ne": "admin@example.com"}},
                {"_id": 1, "username": 1, "email": 1, "status": 1}
            ).sort("_id", 1))
            
            # Format the response
            formatted_users = []
            for user in users:
                formatted_users.append({
                    "id": str(user["_id"]),
                    "name": user.get("username", ""),
                    "email": user.get("email", ""),
                    "status": user.get("status", "active").capitalize()
                })
            
            return formatted_users
>>>>>>> feature/Simon
            
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return []
<<<<<<< HEAD
        finally:
            cursor.close()
            conn.close()
=======
>>>>>>> feature/Simon

    @classmethod
    def search_user_accounts(cls, keyword: str) -> list[dict]:
        """Search user accounts by keyword"""
<<<<<<< HEAD
        kw = f"%{keyword}%"
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username as name, email, status 
                FROM users 
                WHERE id != 0  # Exclude hardcoded admin
                AND (username LIKE %s OR email LIKE %s)
                ORDER BY id
            """, (kw, kw))
            
            users = cursor.fetchall()
            
            # Format the status for display
            for user in users:
                user['status'] = user['status'].capitalize()
            
            return users
            
        except Exception as e:
            print(f"Error searching users: {str(e)}")
            return []
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_user_by_id(cls, user_id: int) -> dict | None:
        """Get user by ID"""
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username as name, email, status 
                FROM users 
                WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                user['status'] = user['status'].capitalize()
            
            return user
            
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_status(cls, user_id: int, status: str) -> bool:
=======
        db = get_connection()
        if db is None:
            return []
        
        try:
            # MongoDB regex search (case-insensitive)
            regex_pattern = {"$regex": keyword, "$options": "i"}
            users = list(db.users.find(
                {
                    "email": {"$ne": "admin@example.com"},
                    "$or": [
                        {"username": regex_pattern},
                        {"email": regex_pattern}
                    ]
                },
                {"_id": 1, "username": 1, "email": 1, "status": 1}
            ).sort("_id", 1))
            
            # Format the response
            formatted_users = []
            for user in users:
                formatted_users.append({
                    "id": str(user["_id"]),
                    "name": user.get("username", ""),
                    "email": user.get("email", ""),
                    "status": user.get("status", "active").capitalize()
                })
            
            return formatted_users
            
        except Exception as e:
            print(f"Error searching users: {str(e)}")
            return []

    @classmethod
    def get_user_by_id(cls, user_id: str) -> dict | None:
        """Get user by ID"""
        db = get_connection()
        if db is None:
            return None
        
        try:
            from bson import ObjectId
            # Try to convert to ObjectId if it's a valid format
            try:
                query_id = ObjectId(user_id)
            except:
                query_id = user_id
            
            user = db.users.find_one(
                {"_id": query_id},
                {"_id": 1, "username": 1, "email": 1, "status": 1}
            )
            
            if user:
                return {
                    "id": str(user["_id"]),
                    "name": user.get("username", ""),
                    "email": user.get("email", ""),
                    "status": user.get("status", "active").capitalize()
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            return None

    @classmethod
    def update_status(cls, user_id: str, status: str) -> bool:
>>>>>>> feature/Simon
        """Update user status in database"""
        status = (status or "").strip().lower()
        if status not in ("active", "suspended"):
            return False

<<<<<<< HEAD
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET status = %s WHERE id = %s
            """, (status, user_id))
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def toggle_suspend(cls, user_id: int) -> dict | None:
=======
        db = get_connection()
        if db is None:
            return False
        
        try:
            from bson import ObjectId
            try:
                query_id = ObjectId(user_id)
            except:
                query_id = user_id
            
            result = db.users.update_one(
                {"_id": query_id},
                {"$set": {"status": status}}
            )
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            return False

    @classmethod
    def toggle_suspend(cls, user_id: str) -> dict | None:
>>>>>>> feature/Simon
        """Toggle a user's status between Active <-> Suspended."""
        user = cls.get_user_by_id(user_id)
        if not user:
            return None

<<<<<<< HEAD
        # Get current status from database
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT status FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            current_status = result['status']
            new_status = "suspended" if current_status == "active" else "active"
            
            cursor.execute("""
                UPDATE users SET status = %s WHERE id = %s
            """, (new_status, user_id))
            conn.commit()
=======
        db = get_connection()
        if db is None:
            return None
        
        try:
            from bson import ObjectId
            try:
                query_id = ObjectId(user_id)
            except:
                query_id = user_id
            
            # Get current status
            user_doc = db.users.find_one({"_id": query_id}, {"status": 1})
            if not user_doc:
                return None
            
            current_status = user_doc.get('status', 'active')
            new_status = "suspended" if current_status == "active" else "active"
            
            # Update status
            db.users.update_one(
                {"_id": query_id},
                {"$set": {"status": new_status}}
            )
>>>>>>> feature/Simon
            
            # Update the user dict
            user['status'] = new_status.capitalize()
            return user
            
        except Exception as e:
            print(f"Error toggling suspend: {str(e)}")
<<<<<<< HEAD
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
=======
            return None
>>>>>>> feature/Simon
