#!/usr/bin/env python3
import requests
import json
import re

session = requests.Session()

# Step 1: Login
print("Step 1: Login")
session.post('http://localhost:5000/login', data={
    'username': 'admin@example.com',
    'password': 'adminpass'
})
print("  Logged in as admin")

# Step 2: Get current form state
print("\nStep 2: Get admin editor for page 3")
editor_resp = session.get('http://localhost:5000/admin/edit-website?page_id=3')

# Extract current content from hidden textarea
hidden_match = re.search(r'<textarea name="content"[^>]*>([^<]*)</textarea>', editor_resp.text)
if hidden_match:
    current_content = hidden_match.group(1).strip()
    if current_content:
        try:
            current = json.loads(current_content)
            print(f"  Current plan name: {list(current.get('plans', {}).values())[0].get('name') if current.get('plans') else 'N/A'}")
        except:
            print(f"  Could not parse current content")
else:
    print("  Could not find hidden textarea")

# Step 3: Save test change
print("\nStep 3: Save test change")
test_content = json.dumps({
    "plans": {
        "free": {
            "name": "Premium Test",
            "price": "999",
            "period": "/month test"
        }
    },
    "included": ["Test Feature 1", "Test Feature 2"]
})

save_resp = session.post('http://localhost:5000/admin/edit-website', data={
    'page_id': 3,
    'content': test_content
})
print(f"  Save status: {save_resp.status_code}")
if save_resp.status_code == 200:
    print("  [OK] Save succeeded")

# Step 4: Check landing page
print("\nStep 4: Check landing page for changes")
landing = session.get('http://localhost:5000/')

checks = {
    'Premium Test': 'Premium Test' in landing.text,
    '$999': '$999' in landing.text or '999' in landing.text,
    '/month test': '/month test' in landing.text,
    'Test Feature 1': 'Test Feature 1' in landing.text,
    'Test Feature 2': 'Test Feature 2' in landing.text
}

all_found = True
for check_name, found in checks.items():
    status = "[YES]" if found else "[NO]"
    print(f"  {status} {check_name}")
    if not found:
        all_found = False

if all_found:
    print("\n[SUCCESS] All test changes appear on landing page!")
    print("The admin editor is working correctly!")
else:
    print("\n[PARTIAL] Some changes missing from landing page")
    print("Issue may be:")
    print("  - Form data not being converted to JSON correctly")
    print("  - Database update failing silently")
    print("  - Cache not being cleared")
