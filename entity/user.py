import hashlib
import secrets

class User:
    def __init__(self, id=None, email=None, username=None, password=None, role=None, created_at=None, status='active'):
        self.id = id
        self.email = email
        self.username = username
        self.password = password  # This should be the hashed password
        self.role = role
        self.created_at = created_at
        self.status = status
    
    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        hashed = salt + pwdhash.hex()
        return hashed
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:32]
        stored_hash = stored_password[32:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return pwdhash.hex() == stored_hash
    
    @staticmethod
    def create_user(email, username, password, role):
        """Create a new user with hashed password"""
        hashed_password = User.hash_password(password)
        return User(
            email=email,
            username=username,
            password=hashed_password,
            role=role
        )
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at,
            'status': self.status
        }
