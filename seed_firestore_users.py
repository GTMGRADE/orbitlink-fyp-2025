from db_config import get_connection
from entity.user import User
from datetime import datetime

def seed_users():
    """Create initial test users in Firestore"""
    db = get_connection()
    if db is None:
        print("Failed to connect to database")
        return
    
    # Check existing users
    print("Checking existing users...")
    existing_users = list(db.users.find({}, {"username": 1, "email": 1, "status": 1}))
    print(f"Found {len(existing_users)} existing users:")
    for user in existing_users:
        print(f"  - {user.get('username')} ({user.get('email')}) - {user.get('status', 'active')}")
    
    print("\nCreating test users...")
    
    users = [
        {
            'email': 'admin@example.com',
            'username': 'admin',
            'password': 'adminpass',
            'role': 'admin'
        },
        {
            'email': 'bizreg@example.com',
            'username': 'bizreg',
            'password': 'bizpass',
            'role': 'business'
        },
        {
            'email': 'infreg@example.com',
            'username': 'infreg',
            'password': 'infpass',
            'role': 'influencer'
        },
        {
            'email': 'john@example.com',
            'username': 'john',
            'password': 'johnpass',
            'role': 'business'
        }
    ]
    
    for user in users:
        try:
            # Check if user already exists
            existing = db.users.find_one({
                "$or": [
                    {"email": user['email']},
                    {"username": user['username']}
                ]
            })
            
            if existing:
                print(f"⚠ User {user['username']} already exists, skipping...")
                continue
            
            # Hash the password
            hashed_password = User.hash_password(user['password'])
            
            # Insert user
            user_doc = {
                "email": user['email'],
                "username": user['username'],
                "password": hashed_password,
                "role": user.get('role', 'user'),
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            result = db.users.insert_one(user_doc)
            print(f"✓ Created {user.get('role', 'user')} user: {user['username']} ({user['email']})")
            
        except Exception as e:
            print(f"✗ Error creating user {user['username']}: {e}")
    
    print("\n=== User Credentials ===")
    print("Admin: admin@example.com / adminpass")
    print("Business: bizreg / bizpass")
    print("Influencer: infreg / infpass")
    print("Test User: john@example.com / johnpass")

if __name__ == "__main__":
    seed_users()
