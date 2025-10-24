import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from services.ai_predictor import ContactAIPredictor

class TestContactAIPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = ContactAIPredictor()

    def test_extract_contact_features_full(self):
        contact = {
            'fullName': 'John Doe',
            'emails': [{'value': 'john.doe@example.com'}, {'value': 'j.doe@work.com'}],
            'phones': [{'value': '123-456-7890'}, {'value': '098-765-4321'}],
            'organization': 'Example Corp',
            'relatedNames': ['Jane Doe'],
            'note': 'Some notes'
        }
        features = self.predictor.extract_contact_features(contact)
        self.assertTrue(features['has_multiple_emails'])
        self.assertTrue(features['has_multiple_phones'])
        self.assertTrue(features['has_organization'])
        self.assertTrue(features['has_related_names'])
        self.assertEqual(features['name_length'], 8)
        self.assertTrue(features['has_notes'])
        self.assertEqual(features['email_domains'], {'example.com', 'work.com'})
        self.assertEqual(features['phone_count'], 2)
        self.assertEqual(features['email_count'], 2)

    def test_extract_contact_features_minimal(self):
        contact = {
            'fullName': 'Jane Doe',
            'emails': [{'value': 'jane.doe@example.com'}],
            'phones': [{'value': '111-222-3333'}]
        }
        features = self.predictor.extract_contact_features(contact)
        self.assertFalse(features['has_multiple_emails'])
        self.assertFalse(features['has_multiple_phones'])
        self.assertFalse(features['has_organization'])
        self.assertFalse(features['has_related_names'])
        self.assertEqual(features['name_length'], 8)
        self.assertFalse(features['has_notes'])
        self.assertEqual(features['email_domains'], {'example.com'})
        self.assertEqual(features['phone_count'], 1)
        self.assertEqual(features['email_count'], 1)

    def test_extract_contact_features_empty(self):
        contact = {}
        features = self.predictor.extract_contact_features(contact)
        self.assertFalse(features['has_multiple_emails'])
        self.assertFalse(features['has_multiple_phones'])
        self.assertFalse(features['has_organization'])
        self.assertFalse(features['has_related_names'])
        self.assertEqual(features['name_length'], 0)
        self.assertFalse(features['has_notes'])
        self.assertEqual(features['email_domains'], set())
        self.assertEqual(features['phone_count'], 0)
        self.assertEqual(features['email_count'], 0)

class TestCalculateMergeProbability(unittest.TestCase):
    def setUp(self):
        self.predictor = ContactAIPredictor()

    def test_calculate_merge_probability_identical(self):
        contact1 = {
            'fullName': 'John Doe',
            'emails': [{'value': 'john.doe@example.com'}],
            'phones': [{'value': '123-456-7890'}]
        }
        contact2 = {
            'fullName': 'John Doe',
            'emails': [{'value': 'john.doe@example.com'}],
            'phones': [{'value': '123-456-7890'}]
        }
        probability = self.predictor.calculate_merge_probability(contact1, contact2)
        self.assertGreater(probability, 0.9)

    def test_calculate_merge_probability_some_overlap(self):
        contact1 = {
            'fullName': 'John Doe',
            'emails': [{'value': 'john.doe@example.com'}],
            'phones': [{'value': '123-456-7890'}]
        }
        contact2 = {
            'fullName': 'Johnathan Doe',
            'emails': [{'value': 'john.doe@example.com'}],
            'phones': [{'value': '111-222-3333'}]
        }
        probability = self.predictor.calculate_merge_probability(contact1, contact2)
        self.assertGreater(probability, 0.4)

    def test_calculate_merge_probability_no_overlap(self):
        contact1 = {
            'fullName': 'John Doe',
            'emails': [{'value': 'john.doe@example.com'}],
            'phones': [{'value': '123-456-7890'}]
        }
        contact2 = {
            'fullName': 'Jane Smith',
            'emails': [{'value': 'jane.smith@example.com'}],
            'phones': [{'value': '111-222-3333'}]
        }
        probability = self.predictor.calculate_merge_probability(contact1, contact2)
        self.assertEqual(probability, 0.0)

class TestCalculateSplitProbability(unittest.TestCase):
    def setUp(self):
        self.predictor = ContactAIPredictor()

    def test_calculate_split_probability_high(self):
        contact = {
            'emails': [{'value': 'a@b.com'}, {'value': 'c@d.com'}],
            'phones': [{'value': '1'}, {'value': '2'}, {'value': '3'}],
            'relatedNames': ['related']
        }
        probability = self.predictor.calculate_split_probability(contact)
        self.assertGreater(probability, 0.7)

    def test_calculate_split_probability_medium(self):
        contact = {
            'emails': [{'value': 'a@b.com'}, {'value': 'c@d.com'}],
            'phones': [{'value': '1'}]
        }
        probability = self.predictor.calculate_split_probability(contact)
        self.assertLess(probability, 0.4)
        self.assertGreater(probability, 0.2)

    def test_calculate_split_probability_low(self):
        contact = {
            'emails': [{'value': 'a@b.com'}],
            'phones': [{'value': '1'}]
        }
        probability = self.predictor.calculate_split_probability(contact)
        self.assertEqual(probability, 0.0)

class TestLearnFromFeedback(unittest.TestCase):
    def setUp(self):
        self.predictor = ContactAIPredictor()

    def test_learn_from_feedback_merge_approved(self):
        features = {'feature1': True}
        self.predictor.learn_from_feedback('merge', features, True)
        self.assertEqual(self.predictor.merge_patterns['{"feature1": true}'], 1)
        self.assertEqual(self.predictor.split_patterns['{"feature1": true}'], 0)
        self.assertEqual(self.predictor.rejection_patterns['{"feature1": true}'], 0)

    def test_learn_from_feedback_split_approved(self):
        features = {'feature1': True}
        self.predictor.learn_from_feedback('split', features, True)
        self.assertEqual(self.predictor.merge_patterns['{"feature1": true}'], 0)
        self.assertEqual(self.predictor.split_patterns['{"feature1": true}'], 1)
        self.assertEqual(self.predictor.rejection_patterns['{"feature1": true}'], 0)

    def test_learn_from_feedback_rejected(self):
        features = {'feature1': True}
        self.predictor.learn_from_feedback('merge', features, False)
        self.assertEqual(self.predictor.merge_patterns['{"feature1": true}'], 0)
        self.assertEqual(self.predictor.split_patterns['{"feature1": true}'], 0)
        self.assertEqual(self.predictor.rejection_patterns['{"feature1": true}'], 1)

if __name__ == '__main__':
    unittest.main()
