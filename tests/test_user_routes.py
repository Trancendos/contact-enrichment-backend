import unittest
import os
import sys

# Set TESTING environment variable before importing the app
os.environ['TESTING'] = 'True'

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app, engine
from src.models.base import Base
from src.models.user import User

class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        Base.metadata.create_all(bind=engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_get_user_not_found(self):
        response = self.app.get('/api/users/999')
        self.assertEqual(response.status_code, 404)

    def test_create_user(self):
        response = self.app.post('/api/users', json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password",
            "name": "Test User"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['username'], "testuser")

    def test_update_user(self):
        # First, create a user
        response = self.app.post('/api/users', json={
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "password",
            "name": "Test User 2"
        })
        user_id = response.json['id']

        # Then, update the user
        response = self.app.put(f'/api/users/{user_id}', json={
            "username": "updateduser"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], "updateduser")

    def test_delete_user(self):
        # First, create a user
        response = self.app.post('/api/users', json={
            "username": "testuser3",
            "email": "test3@example.com",
            "password": "password",
            "name": "Test User 3"
        })
        user_id = response.json['id']

        # Then, delete the user
        response = self.app.delete(f'/api/users/{user_id}')
        self.assertEqual(response.status_code, 204)

        # Verify the user is deleted
        response = self.app.get(f'/api/users/{user_id}')
        self.assertEqual(response.status_code, 404)
