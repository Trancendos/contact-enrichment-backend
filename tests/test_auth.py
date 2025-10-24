import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Set dummy environment variables for testing
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test_key'
os.environ['OPENAI_API_KEY'] = 'test_key'
os.environ['SECRET_KEY'] = 'test_key'
os.environ['ENVIRONMENT'] = 'testing'

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import app
from src.models.user import User

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client for each test."""
        app.config['TESTING'] = True
        self.app = app.test_client()

    @patch('main.SessionLocal')
    def test_register_success(self, MockSessionLocal):
        """Test user registration success."""
        mock_db = MagicMock()
        MockSessionLocal.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        response = self.app.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])

    @patch('main.SessionLocal')
    def test_register_user_exists(self, MockSessionLocal):
        """Test user registration when user already exists."""
        mock_db = MagicMock()
        MockSessionLocal.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = User()

        response = self.app.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password'
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('already exists', response.get_json()['error'])

    @patch('main.SessionLocal')
    def test_login_success(self, MockSessionLocal):
        """Test user login success."""
        mock_db = MagicMock()
        MockSessionLocal.return_value = mock_db
        mock_user = User(
            email='test@example.com',
            password='pbkdf2:sha256:150000$...' # A real hash would be here
        )
        # Mock the password check to always return True
        with patch('src.routes.auth.check_password_hash', return_value=True):
            mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user

            response = self.app.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'password'
            })

            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.get_json()['success'])

    @patch('main.SessionLocal')
    def test_login_invalid_credentials(self, MockSessionLocal):
        """Test user login with invalid credentials."""
        mock_db = MagicMock()
        MockSessionLocal.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        response = self.app.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid email or password', response.get_json()['error'])

    def test_logout(self):
        """Test user logout."""
        response = self.app.post('/api/auth/logout')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])

    @patch('main.SessionLocal')
    def test_get_current_user_success(self, MockSessionLocal):
        """Test getting the current user when authenticated."""
        with self.app as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

            mock_db = MagicMock()
            MockSessionLocal.return_value = mock_db
            mock_user = User(id=1, name='Test User', email='test@example.com')
            mock_db.query.return_value.filter.return_value.first.return_value = mock_user

            response = c.get('/api/auth/me')

            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.get_json()['success'])
            self.assertEqual(response.get_json()['user']['id'], 1)

    def test_get_current_user_not_authenticated(self):
        """Test getting the current user when not authenticated."""
        response = self.app.get('/api/auth/me')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Not authenticated', response.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
