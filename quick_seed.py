import sys
sys.path.insert(0, '/e/Users/User/Downloads/FYP/codingPortion')

from pymongo import MongoClient
import bcrypt
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("MONGODB_CONNECTION_STRING")
db_name = os.getenv("MONGODB_DATABASE_NAME", "orbitlinkfyp")

print(f"Connecting to: {db_name}")
client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
db = client[db_name]

print("Connected! Checking users...")
users = list(db.users.find({}, {"username": 1, "email": 1}))
print(f"Found {len(users)} users:")
for u in users:
    print(f"  - {u.get('username')} ({u.get('email')})")

# Create bizreg user
print("\nCreating bizreg user...")
hashed = bcrypt.hashpw('bizpass'.encode('utf-8'), bcrypt.gensalt(rounds=12))

user_doc = {
    "email": "bizreg@example.com",
    "username": "bizreg",
    "password": hashed.decode('utf-8'),
    "role": "business",
    "status": "active",
    "created_at": datetime.utcnow()
}

# Check if exists
if db.users.find_one({"$or": [{"username": "bizreg"}, {"email": "bizreg@example.com"}]}):
    print("User bizreg already exists!")
else:
    db.users.insert_one(user_doc)
    print("✓ Created bizreg user")

# Create infreg user
print("Creating infreg user...")
hashed = bcrypt.hashpw('infpass'.encode('utf-8'), bcrypt.gensalt(rounds=12))

user_doc = {
    "email": "infreg@example.com",
    "username": "infreg",
    "password": hashed.decode('utf-8'),
    "role": "influencer",
    "status": "active",
    "created_at": datetime.utcnow()
}

if db.users.find_one({"$or": [{"username": "infreg"}, {"email": "infreg@example.com"}]}):
    print("User infreg already exists!")
else:
    db.users.insert_one(user_doc)
    print("✓ Created infreg user")

print("\n=== Users now in database ===")
users = list(db.users.find({}, {"username": 1, "email": 1, "role": 1}))
for u in users:
    print(f"  - {u.get('username')} ({u.get('email')}) - {u.get('role', 'user')}")

print("\n=== Login Credentials ===")
print("Business: bizreg / bizpass")
print("Influencer: infreg / infpass")
