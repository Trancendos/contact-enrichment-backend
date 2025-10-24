"""
Advanced AI Predictor Service for Contact Merging/Splitting
This service learns from user feedback to improve predictions over time.
"""

import json
from collections import defaultdict


class ContactAIPredictor:
    def __init__(self):
        self.merge_patterns = defaultdict(int)  # Track approved merge patterns
        self.split_patterns = defaultdict(int)  # Track approved split patterns
        self.rejection_patterns = defaultdict(int)  # Track rejected suggestions

    def extract_contact_features(self, contact):
        """Extract features from a contact for ML analysis"""
        features = {
            "has_multiple_emails": len(
                [e for e in contact.get("emails", []) if e.get("value")]
            )
            > 1,
            "has_multiple_phones": len(
                [p for p in contact.get("phones", []) if p.get("value")]
            )
            > 1,
            "has_organization": bool(contact.get("organization")),
            "has_related_names": len(contact.get("relatedNames", [])) > 0,
            "name_length": len(contact.get("fullName", "")),
            "has_notes": bool(contact.get("note")),
            "email_domains": set(
                [
                    e.get("value", "").split("@")[1]
                    for e in contact.get("emails", [])
                    if "@" in e.get("value", "")
                ]
            ),
            "phone_count": len(
                [p for p in contact.get("phones", []) if p.get("value")]
            ),
            "email_count": len(
                [e for e in contact.get("emails", []) if e.get("value")]
            ),
        }
        return features

    def calculate_merge_probability(self, contact1, contact2):
        """Calculate probability that two contacts should be merged"""
        score = 0.0
        max_score = 0.0

        # Name similarity
        max_score += 30
        name1 = contact1.get("fullName", "").lower()
        name2 = contact2.get("fullName", "").lower()
        if name1 and name2:
            if name1 == name2:
                score += 30
            elif name1 in name2 or name2 in name1:
                score += 20
            elif self._fuzzy_match(name1, name2):
                score += 15

        # Email overlap
        max_score += 25
        emails1 = set(
            [
                e.get("value", "").lower()
                for e in contact1.get("emails", [])
                if e.get("value")
            ]
        )
        emails2 = set(
            [
                e.get("value", "").lower()
                for e in contact2.get("emails", [])
                if e.get("value")
            ]
        )
        if emails1 and emails2:
            overlap = len(emails1 & emails2)
            if overlap > 0:
                score += 25
            elif self._same_domain(emails1, emails2):
                score += 10

        # Phone overlap
        max_score += 25
        phones1 = set(
            [
                p.get("value", "").replace(" ", "").replace("-", "")
                for p in contact1.get("phones", [])
                if p.get("value")
            ]
        )
        phones2 = set(
            [
                p.get("value", "").replace(" ", "").replace("-", "")
                for p in contact2.get("phones", [])
                if p.get("value")
            ]
        )
        if phones1 and phones2:
            overlap = len(phones1 & phones2)
            if overlap > 0:
                score += 25

        # Organization match
        max_score += 10
        org1 = contact1.get("organization", "").lower()
        org2 = contact2.get("organization", "").lower()
        if org1 and org2 and org1 == org2:
            score += 10

        # Related names overlap
        max_score += 10
        related1 = set([r.lower() for r in contact1.get("relatedNames", [])])
        related2 = set([r.lower() for r in contact2.get("relatedNames", [])])
        if related1 and related2:
            overlap = len(related1 & related2)
            if overlap > 0:
                score += 10

        probability = score / max_score if max_score > 0 else 0.0
        return probability

    def calculate_split_probability(self, contact):
        """Calculate probability that a contact should be split"""
        features = self.extract_contact_features(contact)
        score = 0.0

        # Multiple emails with different domains
        if features["email_count"] > 1 and len(features["email_domains"]) > 1:
            score += 0.3

        # Multiple phones
        if features["phone_count"] > 2:
            score += 0.2

        # Has related names (suggests merged family/colleagues)
        if features["has_related_names"]:
            score += 0.25

        # Multiple emails AND multiple phones
        if features["has_multiple_emails"] and features["has_multiple_phones"]:
            score += 0.25

        return min(score, 1.0)

    def learn_from_feedback(self, suggestion_type, features, approved):
        """Learn from user approval/rejection of suggestions"""
        feature_key = json.dumps(features, sort_keys=True)

        if approved:
            if suggestion_type == "merge":
                self.merge_patterns[feature_key] += 1
            elif suggestion_type == "split":
                self.split_patterns[feature_key] += 1
        else:
            self.rejection_patterns[feature_key] += 1

    def _fuzzy_match(self, str1, str2):
        """Simple fuzzy string matching"""
        # Remove common prefixes/suffixes
        str1 = str1.replace("mr.", "").replace("mrs.", "").replace("dr.", "").strip()
        str2 = str2.replace("mr.", "").replace("mrs.", "").replace("dr.", "").strip()

        # Check if one contains the other
        if str1 in str2 or str2 in str1:
            return True

        # Check first 3 characters match
        if len(str1) > 3 and len(str2) > 3:
            return str1[:3] == str2[:3]

        return False

    def _same_domain(self, emails1, emails2):
        """Check if email sets share the same domain"""
        domains1 = set([e.split("@")[1] for e in emails1 if "@" in e])
        domains2 = set([e.split("@")[1] for e in emails2 if "@" in e])
        return len(domains1 & domains2) > 0


# Global instance
predictor = ContactAIPredictor()
