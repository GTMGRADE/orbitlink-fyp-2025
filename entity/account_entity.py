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
        """Authenticate admin user"""
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
                # We should verify password here too
                # For admin, we can check if the password matches
                cursor.execute("""
                    SELECT password FROM users 
                    WHERE email = %s AND role = 'admin'
                """, (email,))
                password_data = cursor.fetchone()
                
                if password_data:
                    # Import User here to avoid circular import
                    from entity.user import User
                    if User.verify_password(password_data['password'], password):
                        return cls(email=user_data['email'], role=user_data['role'])
            
            raise LoginError("Invalid email or password.")
            
        except Exception as e:
            raise LoginError(f"Authentication error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def to_dict(self) -> dict:
        return {"email": self.email, "role": self.role}

    # User account operations
    @classmethod
    def retrieve_user_accounts(cls) -> list[dict]:
        """Retrieve all user accounts from database"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username as name, role, email, status 
                FROM users 
                WHERE role IN ('influencer', 'business')
                ORDER BY id
            """)
            
            users = cursor.fetchall()
            
            # Format the role for display
            for user in users:
                user['role'] = user['role'].capitalize() + " User"
                user['status'] = user['status'].capitalize()
            
            return users
            
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return []
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def search_user_accounts(cls, keyword: str) -> list[dict]:
        """Search user accounts by keyword"""
        kw = f"%{keyword}%"
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username as name, role, email, status 
                FROM users 
                WHERE role IN ('influencer', 'business')
                AND (username LIKE %s OR email LIKE %s OR role LIKE %s)
                ORDER BY id
            """, (kw, kw, kw))
            
            users = cursor.fetchall()
            
            # Format the role for display
            for user in users:
                user['role'] = user['role'].capitalize() + " User"
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
                SELECT id, username as name, role, email, status 
                FROM users 
                WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                user['role'] = user['role'].capitalize() + " User"
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
        """Update user status in database"""
        status = (status or "").strip().lower()
        if status not in ("active", "suspended"):
            return False

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
        """Toggle a user's status between Active <-> Suspended."""
        user = cls.get_user_by_id(user_id)
        if not user:
            return None

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
            
            # Update the user dict
            user['status'] = new_status.capitalize()
            return user
            
        except Exception as e:
            print(f"Error toggling suspend: {str(e)}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()