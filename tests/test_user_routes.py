import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Set the TESTING environment variable to True BEFORE importing the app
os.environ['TESTING'] = 'True'
# Also set dummy values for other environment variables required by main.py
os.environ['SUPABASE_URL'] = 'https://dummyservice.supabase.co'
os.environ['SUPABASE_KEY'] = 'dummy-key'


# Add the project root to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.models.user import User

class TestUserRoutes(unittest.TestCase):

    def setUp(self):
        """Set up a test client and a mock database session."""
        self.app = app.test_client()
        # The patch should target where the object is looked up.
        # The user routes use g.db, and g.db is created by SessionLocal in main.py
        # So we patch SessionLocal
        self.mock_session = MagicMock()
        self.session_patch = patch('src.main.SessionLocal', return_value=self.mock_session)
        self.session_patch.start()

    def tearDown(self):
        """Stop the patcher."""
        self.session_patch.stop()

    def test_get_user_not_found(self):
        """Test that getting a non-existent user returns a 404 error."""
        # Configure the mock query chain to return None, simulating a user not found
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        # When the app tries to get a user, it should now return a 404
        response = self.app.get('/api/users/999')

        # The corrected code should now return a 404 Not Found
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
