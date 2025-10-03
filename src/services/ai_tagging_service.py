import os
import json
from openai import OpenAI

class AITaggingService:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    def suggest_tags(self, contact_data):
        """
        Analyze contact data and suggest relevant tags using AI.
        
        Args:
            contact_data: Dictionary containing contact information
            
        Returns:
            List of suggested tags
        """
        try:
            # Extract relevant information from contact
            name = contact_data.get('fullName') or f"{contact_data.get('firstName', '')} {contact_data.get('lastName', '')}".strip()
            emails = [email.get('value', '') for email in contact_data.get('emails', [])]
            phones = [phone.get('value', '') for phone in contact_data.get('phones', [])]
            org = contact_data.get('org', '')
            title = contact_data.get('title', '')
            note = contact_data.get('note', '')
            existing_tags = contact_data.get('tags', [])
            
            # Build prompt for AI
            prompt = f"""Analyze the following contact information and suggest 3-5 relevant tags for categorization.

Contact Information:
- Name: {name}
- Organization: {org}
- Title: {title}
- Email domains: {', '.join([email.split('@')[1] if '@' in email else '' for email in emails if email])}
- Notes: {note[:200] if note else 'None'}
- Existing tags: {', '.join(existing_tags) if existing_tags else 'None'}

Suggest tags that would help categorize this contact. Consider:
- Professional vs Personal
- Industry or domain
- Relationship type (client, vendor, colleague, friend, family)
- Importance level (VIP, regular)
- Any specific categories based on the information provided

Return ONLY a JSON array of 3-5 suggested tags in lowercase, like: ["work", "client", "technology"]
Do not include tags that already exist."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that suggests relevant tags for contact management. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            if content.startswith('['):
                suggested_tags = json.loads(content)
            else:
                # Try to find JSON array in the response
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    suggested_tags = json.loads(json_match.group())
                else:
                    suggested_tags = []
            
            # Filter out existing tags and ensure lowercase
            suggested_tags = [tag.lower() for tag in suggested_tags if tag.lower() not in [t.lower() for t in existing_tags]]
            
            return suggested_tags[:5]  # Return max 5 suggestions
            
        except Exception as e:
            print(f"Error suggesting tags: {e}")
            return []
    
    def suggest_tags_batch(self, contacts):
        """
        Suggest tags for multiple contacts at once.
        
        Args:
            contacts: List of contact dictionaries
            
        Returns:
            Dictionary mapping contact IDs to suggested tags
        """
        results = {}
        for contact in contacts:
            contact_id = contact.get('id')
            if contact_id:
                results[contact_id] = self.suggest_tags(contact)
        return results
