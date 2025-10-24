import os
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

class AITaggingService:
    """Provides AI-powered and rule-based contact tagging.

    This service can use OpenAI to suggest tags for contacts, or fall back
    to a rule-based system if the OpenAI API is not available.
    """
    def __init__(self):
        """Initializes the AITaggingService."""
        if OPENAI_AVAILABLE and OpenAI:
            self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        else:
            self.client = None
    
    def suggest_tags(self, contact_data):
        """Analyzes contact data and suggests relevant tags using AI.
        
        Args:
            contact_data: A dictionary containing contact information.
            
        Returns:
            A list of suggested tags.
        """
        if not self.client:
            # Fallback to rule-based tagging if OpenAI is not available
            return self._fallback_suggest_tags(contact_data)
        
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
        """Suggests tags for multiple contacts at once.
        
        Args:
            contacts: A list of contact dictionaries.
            
        Returns:
            A dictionary mapping contact IDs to suggested tags.
        """
        results = {}
        for contact in contacts:
            contact_id = contact.get('id')
            if contact_id:
                results[contact_id] = self.suggest_tags(contact)
        return results
    
    def _fallback_suggest_tags(self, contact_data):
        """Provides rule-based fallback tagging when AI is not available.
        
        Args:
            contact_data: A dictionary containing contact information.
            
        Returns:
            A list of suggested tags.
        """
        tags = []
        # Check organization
        org = contact_data.get('org', '').lower()
        if org:
            tags.append('work')
            if any(word in org for word in ['corp', 'inc', 'llc', 'ltd', 'company']):
                tags.append('business')
        
        # Check email domains
        emails = [email.get('value', '') for email in contact_data.get('emails', [])]
        for email in emails:
            if '@' in email:
                domain = email.split('@')[1].lower()
                if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                    if 'personal' not in tags:
                        tags.append('personal')
                else:
                    if 'work' not in tags:
                        tags.append('work')
        
        # Check title
        title = contact_data.get('title', '').lower()
        if title:
            if any(word in title for word in ['ceo', 'cto', 'cfo', 'president', 'director', 'vp']):
                tags.append('executive')
            if any(word in title for word in ['manager', 'lead', 'head']):
                tags.append('management')
            if any(word in title for word in ['developer', 'engineer', 'programmer']):
                tags.append('technical')
        
        # Check if contact has multiple phones/emails (might be important)
        if len(contact_data.get('phones', [])) > 2 or len(emails) > 2:
            tags.append('vip')
        
        # Remove duplicates and limit to 5 tags
        existing_tags = [t.lower() for t in contact_data.get('tags', [])]
        tags = [tag for tag in tags if tag not in existing_tags]
        
        return tags[:5]
