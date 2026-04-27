import sys
sys.path.insert(0, 'backend')

print("Loading app...")
from src.main import app
print("App loaded!")

from fastapi.testclient import TestClient
client = TestClient(app)

print("Testing login endpoint...")
response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'test123'})
print('Status:', response.status_code)
print('Response:', response.text)

print("Testing register endpoint...")
response = client.post('/auth/register', json={'email': 'newuser@example.com', 'password': 'test123', 'name': 'Test User'})
print('Status:', response.status_code)
print('Response:', response.text)
