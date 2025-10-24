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
