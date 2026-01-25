# import hashlib
# import secrets
# import bcrypt  # Add bcrypt for more secure password hashing

# class User:
#     def __init__(self, id=None, email=None, username=None, password=None, role=None, created_at=None, status='active'):
#         self.id = id
#         self.email = email
#         self.username = username
#         self.password = password  
#         self.role = role
#         self.created_at = created_at
#         self.status = status
    
#     @staticmethod
#     def hash_password(password):
#         """Hash a password for storing using bcrypt (more secure)."""
#         password_bytes = password.encode('utf-8')
#         salt = bcrypt.gensalt(rounds=12)  
#         hashed = bcrypt.hashpw(password_bytes, salt)
#         return hashed.decode('utf-8')  
    
#     @staticmethod
#     def verify_password(stored_password, provided_password):
#         """Verify a stored password against one provided by user"""
#         # For bcrypt hashes
#         if stored_password.startswith('$2b$') or stored_password.startswith('$2a$'):
#             try:
#                 stored_bytes = stored_password.encode('utf-8')
#                 provided_bytes = provided_password.encode('utf-8')
#                 return bcrypt.checkpw(provided_bytes, stored_bytes)
#             except Exception:
#                 pass
        
#         # Fallback for old hashes (PBKDF2)
#         try:
#             salt = stored_password[:32]
#             stored_hash = stored_password[32:]
#             pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
#             return pwdhash.hex() == stored_hash
#         except Exception:
#             return False
    
#     @staticmethod
#     def create_user(email, username, password, role):
#         """Create a new user with hashed password"""
#         hashed_password = User.hash_password(password)
#         return User(
#             email=email,
#             username=username,
#             password=hashed_password,
#             role=role
#         )
    
#     def to_dict(self):
#         """Convert user object to dictionary"""
#         return {
#             'id': self.id,
#             'email': self.email,
#             'username': self.username,
#             'role': self.role,
#             'created_at': self.created_at,
#             'status': self.status
#         }

import hashlib
import secrets
import bcrypt  # Add bcrypt for more secure password hashing

class User:
    def __init__(self, id=None, email=None, username=None, password=None, created_at=None, status='active'):
        self.id = id
        self.email = email
        self.username = username
        self.password = password  
<<<<<<< HEAD
=======
<<<<<<< HEAD
        self.role = role
=======
>>>>>>> feature/Simon
>>>>>>> development
        self.created_at = created_at
        self.status = status
    
    @staticmethod
    def hash_password(password):
        """Hash a password for storing using bcrypt (more secure)."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)  
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')  
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        # For bcrypt hashes
        if stored_password.startswith('$2b$') or stored_password.startswith('$2a$'):
            try:
                stored_bytes = stored_password.encode('utf-8')
                provided_bytes = provided_password.encode('utf-8')
                return bcrypt.checkpw(provided_bytes, stored_bytes)
            except Exception:
                pass
        
        # Fallback for old hashes (PBKDF2)
        try:
            salt = stored_password[:32]
            stored_hash = stored_password[32:]
            pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwdhash.hex() == stored_hash
        except Exception:
            return False
    
    @staticmethod
    def create_user(email, username, password):
        """Create a new user with hashed password"""
        hashed_password = User.hash_password(password)
        return User(
            email=email,
            username=username,
            password=hashed_password
        )
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at,
            'status': self.status
        }