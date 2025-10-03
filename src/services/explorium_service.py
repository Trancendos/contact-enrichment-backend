
import os
import json
import subprocess

def call_explorium_tool(tool_name, input_data):
    """Calls a specified Explorium MCP tool with the given input data."""
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
        print(f"Output: {result.stdout}")
        return {"error": "JSON decode error", "output": result.stdout}

def get_business_id(company_name=None, domain=None):
    """Matches a company name or domain to get an Explorium business ID."""
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

def enrich_contact_with_explorium(contact):
    """Enriches a contact with data from Explorium based on company and prospect info."""
    enriched_data = {}
    company_name = contact.get("org")
    email = next((e.get("value") for e in contact.get("email", []) if e.get("value")), None)
    full_name = contact.get("fn")

    business_id = None
    if company_name:
        business_id = get_business_id(company_name=company_name)
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

