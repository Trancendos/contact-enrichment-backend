
import os
os.environ['SUPABASE_URL'] = 'https://dummy.supabase.co'
os.environ['SUPABASE_KEY'] = 'dummy_key'

import unittest
import json
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestUserAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a real in-memory SQLite engine for testing
        cls.test_engine = create_engine('sqlite:///:memory:')
        cls.TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.test_engine)

        # Patch the original engine and SessionLocal in src.main
        cls.patcher_engine = patch('src.main.engine', cls.test_engine)
        cls.patcher_session = patch('src.main.SessionLocal', cls.TestSessionLocal)

        cls.patcher_engine.start()
        cls.patcher_session.start()

        # Now we can import the app and other components
        # We need to import them here after the patch is active
        from src.main import app
        from src.models.base import Base

        # Import all models to ensure they are registered with Base
        from src.models.user import User
        from src.models.contact import Contact
        from src.models.contact_history import ContactHistory
        from src.models.contact_relationship import ContactRelationship

        cls.app = app
        cls.Base = Base
        cls.User = User

    @classmethod
    def tearDownClass(cls):
        cls.patcher_engine.stop()
        cls.patcher_session.stop()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        # Create all tables in the in-memory database
        self.Base.metadata.create_all(bind=self.test_engine)
        self.db = self.TestSessionLocal()

    def tearDown(self):
        self.db.close()
        # Drop all tables
        self.Base.metadata.drop_all(bind=self.test_engine)
        self.app_context.pop()

    def test_update_user_duplicate_email(self):
        # Create two users
        user1 = self.User(username='user1', email='user1@example.com', password='password', name='User One')
        user2 = self.User(username='user2', email='user2@example.com', password='password', name='User Two')
        self.db.add_all([user1, user2])
        self.db.commit()

        # Get the IDs
        user2_id = user2.id

        # Commit and close session to ensure objects are detached and test mimics a real request
        self.db.close()

        # Try to update user2's email to user1's email
        response = self.client.put(
            f'/api/users/{user2_id}',
            data=json.dumps({'email': 'user1@example.com'}),
            content_type='application/json'
        )

        # Before the fix, this should cause an IntegrityError from the DB,
        # resulting in a 500 status code, not the expected 409.
        # The test assertion will check for 409, so it should fail.
        self.assertEqual(response.status_code, 409, f"Expected 409 but got {response.status_code}. Response data: {response.data.decode()}")

if __name__ == '__main__':
    unittest.main()
