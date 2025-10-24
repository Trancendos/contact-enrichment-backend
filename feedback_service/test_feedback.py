
import unittest
import json
from feedback_service.app import app, db, Feedback

class FeedbackAPITestCase(unittest.TestCase):

    def setUp(self):
        """Set up a new test environment before each test."""
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()

        # Create the database and the tables
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the test environment after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_submit_feedback_success(self):
        """Test successful feedback submission."""
        # Define the payload for the POST request
        payload = {
            'user_id': 'testuser123',
            'feedback_text': 'This is a test feedback message.',
            'source': 'WebApp'
        }
        # Send the POST request to the API endpoint
        response = self.app.post('/api/feedback',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        # Assert that the response status code is 201 (Created)
        self.assertEqual(response.status_code, 201)

        # Parse the JSON response
        data = json.loads(response.data)

        # Assert that the response contains the correct data
        self.assertEqual(data['user_id'], 'testuser123')
        self.assertEqual(data['feedback_text'], 'This is a test feedback message.')
        self.assertEqual(data['source'], 'WebApp')
        self.assertIn('id', data)
        self.assertIn('timestamp', data)

        # Verify that the feedback was actually saved to the database
        with app.app_context():
            feedback_entry = Feedback.query.get(data['id'])
            self.assertIsNotNone(feedback_entry)
            self.assertEqual(feedback_entry.feedback_text, 'This is a test feedback message.')

    def test_submit_feedback_missing_fields(self):
        """Test feedback submission with missing required fields."""
        # Define a payload with a missing 'source'
        payload = {
            'user_id': 'testuser123',
            'feedback_text': 'This is another test message.'
        }
        # Send the POST request
        response = self.app.post('/api/feedback',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        # Assert that the status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Parse the JSON response
        data = json.loads(response.data)

        # Assert that the response contains the correct error message
        self.assertEqual(data['error'], 'Missing required fields: feedback_text and source')

    def test_submit_feedback_unsupported_media_type(self):
        """Test feedback submission with an unsupported media type."""
        # Send a request with a non-JSON content type
        response = self.app.post('/api/feedback',
                                 data="this is not json",
                                 content_type='text/plain')

        # Assert that the status code is 415 (Unsupported Media Type)
        self.assertEqual(response.status_code, 415)

    def test_submit_feedback_malformed_json(self):
        """Test feedback submission with malformed JSON."""
        # Send a request with malformed JSON
        response = self.app.post('/api/feedback',
                                 data='{"feedback_text": "test", "source": "WebApp"',
                                 content_type='application/json')

        # Assert that the status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
