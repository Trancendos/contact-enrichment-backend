from src.services.history_service import HistoryService

class ContactManagementService:
    """Service for managing contact modifications and logging history"""
    
    @staticmethod
    def create_contact(user_id, contact_data, request=None):
        """Create a new contact and log the action"""
        # In a real application, this would save the contact to the database
        # For now, we just log the action
        
        new_contact_id = contact_data.get("id", f"contact-{hash(str(contact_data))}")
        
        HistoryService.log_action(
            user_id=user_id,
            contact_id=new_contact_id,
            action_type="create",
            after_data=contact_data,
            description=f"Created new contact: {contact_data.get('fullName', 'Unknown')}",
            request=request
        )
        
        return { "success": True, "contact_id": new_contact_id }

    @staticmethod
    def update_contact(user_id, contact_id, before_data, after_data, request=None):
        """Update a contact and log the action"""
        # In a real application, this would update the contact in the database
        
        HistoryService.log_action(
            user_id=user_id,
            contact_id=contact_id,
            action_type="update",
            before_data=before_data,
            after_data=after_data,
            description=f"Updated contact: {after_data.get('fullName', 'Unknown')}",
            request=request
        )
        
        return { "success": True }

    @staticmethod
    def delete_contact(user_id, contact_id, contact_data, request=None):
        """Delete a contact and log the action"""
        # In a real application, this would delete the contact from the database
        
        HistoryService.log_action(
            user_id=user_id,
            contact_id=contact_id,
            action_type="delete",
            before_data=contact_data,
            description=f"Deleted contact: {contact_data.get('fullName', 'Unknown')}",
            request=request
        )
        
        return { "success": True }

    @staticmethod
    def split_phone(user_id, original_contact, phone_to_split, request=None):
        """Split a phone number into a new contact and log the actions"""
        
        # 1. Create the new contact
        new_contact_data = {
            "id": f"contact-{hash(str(phone_to_split))}",
            "fullName": "",
            "firstName": "",
            "lastName": "",
            "emails": [{ "value": "", "type": "Home" }],
            "phones": [phone_to_split],
            "organization": original_contact.get("organization", ""),
            "title": original_contact.get("title", ""),
            "note": f"Split from: {original_contact.get('fullName', 'Unknown')}",
            "relatedNames": [],
            "rawLines": []
        }
        
        ContactManagementService.create_contact(user_id, new_contact_data, request)
        
        # 2. Update the original contact
        updated_original_data = {
            **original_contact,
            "phones": [p for p in original_contact.get("phones", []) if p["value"] != phone_to_split["value"]]
        }
        
        ContactManagementService.update_contact(
            user_id=user_id,
            contact_id=original_contact["id"],
            before_data=original_contact,
            after_data=updated_original_data,
            request=request
        )
        
        return { "success": True, "new_contact": new_contact_data, "updated_original": updated_original_data }

    @staticmethod
    def split_all(user_id, original_contact, request=None):
        """Split a contact into multiple new contacts and log the actions"""
        
        new_contacts = []
        
        # 1. Create new contacts for each email
        for email in original_contact.get("emails", []):
            if email.get("value"):
                new_contact_data = {
                    "id": f"contact-{hash(str(email))}",
                    "fullName": "",
                    "emails": [email],
                    "phones": [],
                    "note": f"Split from: {original_contact.get('fullName', 'Unknown')}"
                }
                ContactManagementService.create_contact(user_id, new_contact_data, request)
                new_contacts.append(new_contact_data)
        
        # 2. Create new contacts for each phone
        for phone in original_contact.get("phones", []):
            if phone.get("value"):
                new_contact_data = {
                    "id": f"contact-{hash(str(phone))}",
                    "fullName": "",
                    "emails": [],
                    "phones": [phone],
                    "note": f"Split from: {original_contact.get('fullName', 'Unknown')}"
                }
                ContactManagementService.create_contact(user_id, new_contact_data, request)
                new_contacts.append(new_contact_data)
        
        # 3. Delete the original contact
        ContactManagementService.delete_contact(user_id, original_contact["id"], original_contact, request)
        
        return { "success": True, "new_contacts": new_contacts }

    @staticmethod
    def merge_contacts(user_id, contacts_to_merge, request=None):
        """Merge multiple contacts into one and log the actions"""
        
        if not contacts_to_merge or len(contacts_to_merge) < 2:
            return { "success": False, "error": "At least two contacts are required for merging" }
        
        # 1. Create the merged contact
        merged_contact_data = {
            "id": contacts_to_merge[0]["id"],
            "fullName": next((c["fullName"] for c in contacts_to_merge if c.get("fullName")), ""),
            "emails": [],
            "phones": [],
            "note": " | ".join(filter(None, (c.get("note") for c in contacts_to_merge)))
        }
        
        # Collect unique emails and phones
        email_set = set()
        phone_set = set()
        for contact in contacts_to_merge:
            for email in contact.get("emails", []):
                if email.get("value") and email["value"] not in email_set:
                    merged_contact_data["emails"].append(email)
                    email_set.add(email["value"])
            for phone in contact.get("phones", []):
                if phone.get("value") and phone["value"] not in phone_set:
                    merged_contact_data["phones"].append(phone)
                    phone_set.add(phone["value"])
        
        # 2. Log the merge action
        HistoryService.log_action(
            user_id=user_id,
            contact_id=merged_contact_data["id"],
            action_type="merge",
            before_data={ "merged_from": [c["id"] for c in contacts_to_merge] },
            after_data=merged_contact_data,
            description=f"Merged {len(contacts_to_merge)} contacts",
            request=request
        )
        
        # 3. Delete the other contacts
        for contact in contacts_to_merge[1:]:
            ContactManagementService.delete_contact(user_id, contact["id"], contact, request)
        
        return { "success": True, "merged_contact": merged_contact_data }

