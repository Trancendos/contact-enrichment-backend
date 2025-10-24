"""
Natural Language Understanding Service for Contact Notes
Extracts entities like names, companies, dates, and relationships from notes.
"""

import re


class ContactNLUService:
    def __init__(self):
        # Common relationship indicators
        self.relationship_keywords = {
            "family": [
                "wife",
                "husband",
                "son",
                "daughter",
                "brother",
                "sister",
                "mother",
                "father",
                "parent",
                "child",
                "spouse",
                "partner",
            ],
            "professional": [
                "colleague",
                "coworker",
                "boss",
                "manager",
                "employee",
                "client",
                "vendor",
                "supplier",
                "consultant",
            ],
            "social": ["friend", "neighbor", "acquaintance", "classmate", "teammate"],
        }

        # Common company indicators
        self.company_indicators = [
            "inc",
            "llc",
            "ltd",
            "corp",
            "corporation",
            "company",
            "co",
            "group",
            "enterprises",
        ]

    def analyze_note(self, note_text):
        """Analyze a contact note and extract structured information"""
        if not note_text:
            return {}

        analysis = {
            "names": self.extract_names(note_text),
            "companies": self.extract_companies(note_text),
            "dates": self.extract_dates(note_text),
            "relationships": self.extract_relationships(note_text),
            "emails": self.extract_emails(note_text),
            "phones": self.extract_phones(note_text),
            "locations": self.extract_locations(note_text),
            "sentiment": self.analyze_sentiment(note_text),
            "keywords": self.extract_keywords(note_text),
        }

        return analysis

    def extract_names(self, text):
        """Extract potential person names from text"""
        # Simple pattern: Capitalized words (2-3 words)
        pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b"
        matches = re.findall(pattern, text)

        # Filter out common false positives
        filtered = []
        for match in matches:
            if not any(
                indicator in match.lower() for indicator in self.company_indicators
            ):
                filtered.append(match)

        return list(set(filtered))

    def extract_companies(self, text):
        """Extract company names from text"""
        companies = []

        # Pattern 1: Words ending with company indicators
        for indicator in self.company_indicators:
            pattern = rf"\b([A-Z][A-Za-z\s&]+\s+{indicator}\.?)\b"
            matches = re.findall(pattern, text, re.IGNORECASE)
            companies.extend(matches)

        # Pattern 2: All caps words (often company names)
        pattern = r"\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b"
        matches = re.findall(pattern, text)
        companies.extend(matches)

        return list(set([c.strip() for c in companies]))

    def extract_dates(self, text):
        """Extract dates from text"""
        dates = []

        # Pattern 1: MM/DD/YYYY or DD/MM/YYYY
        pattern1 = r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"
        dates.extend(re.findall(pattern1, text))

        # Pattern 2: Month Day, Year (e.g., "January 15, 2024")
        pattern2 = r"\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b"
        dates.extend(re.findall(pattern2, text, re.IGNORECASE))

        # Pattern 3: Year only (e.g., "2024")
        pattern3 = r"\b(20\d{2})\b"
        dates.extend(re.findall(pattern3, text))

        return list(set(dates))

    def extract_relationships(self, text):
        """Extract relationship information from text"""
        relationships = []
        text_lower = text.lower()

        for rel_type, keywords in self.relationship_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Try to find the name associated with this relationship
                    # Look for capitalized words near the relationship keyword
                    pattern = rf"(?:my\s+)?{keyword}(?:\s+is)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        relationships.append(
                            {"type": rel_type, "relationship": keyword, "name": match}
                        )

        return relationships

    def extract_emails(self, text):
        """Extract email addresses from text"""
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return list(set(re.findall(pattern, text)))

    def extract_phones(self, text):
        """Extract phone numbers from text"""
        # Pattern for various phone formats
        patterns = [
            r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",  # 123-456-7890
            r"\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b",  # (123) 456-7890
            r"\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",  # +1-123-456-7890
        ]

        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))

        return list(set(phones))

    def extract_locations(self, text):
        """Extract location information from text"""
        locations = []

        # Pattern 1: City, State
        pattern1 = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b"
        locations.extend(re.findall(pattern1, text))

        # Pattern 2: State names
        states = [
            "California",
            "New York",
            "Texas",
            "Florida",
            "Illinois",
            "Pennsylvania",
            "Ohio",
            "Georgia",
            "North Carolina",
            "Michigan",
        ]
        for state in states:
            if state in text:
                locations.append(state)

        return list(set(locations))

    def analyze_sentiment(self, text):
        """Analyze sentiment of the note"""
        positive_words = [
            "great",
            "excellent",
            "good",
            "wonderful",
            "amazing",
            "fantastic",
            "helpful",
            "friendly",
            "professional",
            "reliable",
        ]
        negative_words = [
            "bad",
            "poor",
            "terrible",
            "awful",
            "difficult",
            "problematic",
            "unreliable",
            "unprofessional",
            "rude",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def extract_keywords(self, text):
        """Extract important keywords from text"""
        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "was",
            "are",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "may",
            "might",
            "must",
            "can",
        }

        # Tokenize and filter
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        keywords = [word for word in words if word not in stop_words]

        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:10]]

    def generate_suggestions_from_analysis(self, contact, analysis):
        """Generate actionable suggestions based on NLU analysis"""
        suggestions = []

        # Suggest adding extracted emails
        for email in analysis.get("emails", []):
            if not any(e.get("value") == email for e in contact.get("emails", [])):
                suggestions.append(
                    {
                        "type": "add_email",
                        "field": "email",
                        "value": email,
                        "confidence": 0.8,
                        "source": "NLU - Extracted from notes",
                    }
                )

        # Suggest adding extracted phones
        for phone in analysis.get("phones", []):
            if not any(p.get("value") == phone for p in contact.get("phones", [])):
                suggestions.append(
                    {
                        "type": "add_phone",
                        "field": "phone",
                        "value": phone,
                        "confidence": 0.75,
                        "source": "NLU - Extracted from notes",
                    }
                )

        # Suggest adding company
        if analysis.get("companies") and not contact.get("organization"):
            suggestions.append(
                {
                    "type": "add_organization",
                    "field": "organization",
                    "value": analysis["companies"][0],
                    "confidence": 0.7,
                    "source": "NLU - Extracted from notes",
                }
            )

        # Suggest related contacts
        for relationship in analysis.get("relationships", []):
            suggestions.append(
                {
                    "type": "add_related_contact",
                    "field": "related_name",
                    "value": f"{relationship['name']} ({relationship['relationship']})",
                    "confidence": 0.65,
                    "source": "NLU - Relationship detected in notes",
                }
            )

        return suggestions


# Global instance
nlu_service = ContactNLUService()
