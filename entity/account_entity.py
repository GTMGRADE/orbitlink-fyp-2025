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
            
            raise LoginError("Invalid email or password.")
            
        except Exception as e:
            raise LoginError(f"Authentication error: {str(e)}")

    def to_dict(self) -> dict:
        return {"email": self.email, "role": self.role}

    # User account operations
    @classmethod
    def retrieve_user_accounts(cls) -> list[dict]:
        """Retrieve all user accounts from database"""
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
            
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return []

    @classmethod
    def search_user_accounts(cls, keyword: str) -> list[dict]:
        """Search user accounts by keyword"""
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
        """Update user status in database"""
        status = (status or "").strip().lower()
        if status not in ("active", "suspended"):
            return False

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
        """Toggle a user's status between Active <-> Suspended."""
        user = cls.get_user_by_id(user_id)
        if not user:
            return None

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
            
            # Update the user dict
            user['status'] = new_status.capitalize()
            return user
            
        except Exception as e:
            print(f"Error toggling suspend: {str(e)}")
            return None