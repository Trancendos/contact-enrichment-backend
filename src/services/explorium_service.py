"""
Service for interacting with the Explorium MCP.

This service provides methods for calling Explorium tools to enrich contact
and business data.
"""
import os
import json
import subprocess
from sqlalchemy.orm import Session
from src.models.contact import Contact


def call_explorium_tool(tool_name, input_data):
    """
    Call a specified Explorium MCP tool with the given input data.

    Args:
        tool_name (str): The name of the tool to call.
        input_data (dict): The input data for the tool.

    Returns:
        dict: The JSON response from the tool, or an error dictionary if the
            call fails.
    """
    input_json = json.dumps(input_data)
    command = [
        "manus-mcp-cli",
        "tool",
        "call",
        tool_name,
        "--server",
        "explorium",
        "--input",
        input_json
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error calling Explorium tool {tool_name}: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return {"error": str(e), "stdout": e.stdout, "stderr": e.stderr}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Explorium tool {tool_name} output: {e}")
        # Attempt to parse partial JSON or return raw output if it's not JSON
        try:
            return json.loads(result.stdout)
        except:
            return {"error": "JSON decode error", "output": result.stdout}


class ExploriumService:
    """
    A service for enriching contact data using the Explorium MCP.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize the ExploriumService.

        Args:
            db (sqlalchemy.orm.Session): The database session.
            user_id (int): The ID of the current user.
        """
        self.db = db
        self.user_id = user_id

    def get_business_id(self, company_name=None, domain=None):
        """
        Match a company name or domain to get an Explorium business ID.

        Args:
            company_name (str, optional): The name of the company. Defaults to None.
            domain (str, optional): The domain of the company. Defaults to None.

        Returns:
            str: The Explorium business ID, or None if no match is found.
        """
        if not company_name and not domain:
            return None

        businesses_to_match = []
        if company_name and domain:
            businesses_to_match.append({"name": company_name, "domain": domain})
        elif company_name:
            businesses_to_match.append({"name": company_name})
        elif domain:
            businesses_to_match.append({"domain": domain})

        if not businesses_to_match:
            return None

        input_data = {
            "businesses_to_match": businesses_to_match,
            "tool_reasoning": f"Get business ID for company: {company_name or domain}"
        }
        response = call_explorium_tool("match-business", input_data)
        if response and isinstance(response, list) and response[0].get("business_id"):
            return response[0]["business_id"]
        return None

    def enrich_contact_with_explorium(self, contact_data: dict):
        """
        Enrich a contact with data from Explorium.

        This method enriches a contact with business and prospect data from
        Explorium based on the contact's company name, email, and full name.

        Args:
            contact_data (dict): A dictionary of contact data.

        Returns:
            dict: A dictionary of enriched data from Explorium.
        """
        enriched_data = {}
        company_name = contact_data.get("organization")
        # Assuming emails is a list of dicts, get the first valid email
        email = next((e.get("value") for e in contact_data.get("emails", []) if e.get("value")), None)
        full_name = contact_data.get("full_name")

        business_id = None
        if company_name:
            business_id = self.get_business_id(company_name=company_name)
            if business_id:
                enriched_data["explorium_business_id"] = business_id
                # Fetch and enrich business data
                business_enrichment_input = {
                    "business_ids": [business_id],
                    "enrichments": ["firmographics", "technographics", "workforce-trends"],
                    "tool_reasoning": f"Enrich business data for {company_name}"
                }
                business_data = call_explorium_tool("enrich-business", business_enrichment_input)
                if business_data and isinstance(business_data, list) and business_data[0]:
                    enriched_data["explorium_business_data"] = business_data[0]

        # Match and enrich prospect data if full name and company are available
        if full_name and (company_name or business_id):
            prospect_match_input = {
                "prospects_to_match": [{
                    "full_name": full_name,
                    "company_name": company_name,
                    "business_id": business_id # Use business_id if available for better accuracy
                }],
                "tool_reasoning": f"Match prospect {full_name} at {company_name}"
            }
            prospect_match_response = call_explorium_tool("match-prospects", prospect_match_input)
            if prospect_match_response and isinstance(prospect_match_response, list) and prospect_match_response[0].get("prospect_id"):
                prospect_id = prospect_match_response[0]["prospect_id"]
                enriched_data["explorium_prospect_id"] = prospect_id
                prospect_enrichment_input = {
                    "prospect_ids": [prospect_id],
                    "enrichments": ["profiles", "contacts"],
                    "tool_reasoning": f"Enrich prospect data for {full_name}"
                }
                prospect_data = call_explorium_tool("enrich-prospects", prospect_enrichment_input)
                if prospect_data and isinstance(prospect_data, list) and prospect_data[0]:
                    enriched_data["explorium_prospect_data"] = prospect_data[0]

        return enriched_data

