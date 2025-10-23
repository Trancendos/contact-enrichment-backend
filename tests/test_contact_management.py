import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock the problematic modules before anything from 'src' is imported.
sys.modules['src.models.base'] = MagicMock()
sys.modules['src.models.user'] = MagicMock()
sys.modules['src.models.contact'] = MagicMock()
sys.modules['src.models.contact_history'] = MagicMock()
sys.modules['src.models.contact_relationship'] = MagicMock()
sys.modules['src.services.history_service'] = MagicMock()


class TestContactManagementService(unittest.TestCase):
    def test_merge_contacts_with_relationships(self):
        from src.services.contact_management_service import ContactManagementService
        from src.models.contact import Contact
        from src.models.contact_relationship import ContactRelationship

        # Arrange
        db_session = MagicMock()
        user_id = 1

        contact1 = MagicMock()
        contact1.id = 1
        contact1.user_id = user_id
        contact1.emails = []
        contact1.phones = []
        contact1.tags = []
        contact1.notes = ""
        contact1.to_dict.return_value = {'id': 1}

        contact2 = MagicMock()
        contact2.id = 2
        contact2.user_id = user_id
        contact2.to_dict.return_value = {'id': 2}

        relationship = MagicMock()
        relationship.contact_id_1 = 2
        relationship.contact_id_2 = 3

        contacts_to_merge = [contact1, contact2]

        def query_side_effect(model):
            if model == Contact:
                q = MagicMock()
                q.filter.return_value.all.return_value = contacts_to_merge
                return q
            elif model == ContactRelationship:
                 q = MagicMock()
                 q.filter.return_value.all.return_value = [relationship]
                 return q
            return MagicMock()

        db_session.query.side_effect = query_side_effect

        service = ContactManagementService(db_session, user_id)

        # Act
        result = service.merge_contacts(contact_ids=[1, 2])

        # Assert
        self.assertTrue(result['success'])
        # The test fails here because the service doesn't update the relationship
        self.assertEqual(relationship.contact_id_1, 1)

    def test_merge_contacts_deletes_self_referencing_relationship(self):
        from src.services.contact_management_service import ContactManagementService
        from src.models.contact import Contact
        from src.models.contact_relationship import ContactRelationship

        # Arrange
        db_session = MagicMock()
        user_id = 1

        contact1 = MagicMock()
        contact1.id = 1
        contact1.user_id = user_id
        contact1.emails = []
        contact1.phones = []
        contact1.tags = []
        contact1.notes = ""
        contact1.to_dict.return_value = {'id': 1}

        contact2 = MagicMock()
        contact2.id = 2
        contact2.user_id = user_id
        contact2.to_dict.return_value = {'id': 2}

        # This relationship will become self-referencing after the merge
        relationship = MagicMock()
        relationship.contact_id_1 = 1
        relationship.contact_id_2 = 2

        contacts_to_merge = [contact1, contact2]

        def query_side_effect(model):
            if model == Contact:
                q = MagicMock()
                q.filter.return_value.all.return_value = contacts_to_merge
                return q
            elif model == ContactRelationship:
                q = MagicMock()
                q.filter.return_value.all.return_value = [relationship]
                return q
            return MagicMock()

        db_session.query.side_effect = query_side_effect

        service = ContactManagementService(db_session, user_id)

        # Act
        result = service.merge_contacts(contact_ids=[1, 2])

        # Assert
        self.assertTrue(result['success'])
        db_session.delete.assert_any_call(relationship)

if __name__ == '__main__':
    unittest.main()
