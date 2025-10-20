import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

REPOSITORIES = [
    "Trancendos/repo1",
    "Trancendos/repo2",
    "Trancendos/repo3",
    "Trancendos/repo4",
    "Trancendos/repo5",
    "Trancendos/repo6",
    "Trancendos/repo7",
    "Trancendos/repo8",
    "Trancendos/repo9",
    "Trancendos/repo10"
]

# Function to fetch issues from GitHub
def fetch_github_issues(repo):
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info(f"Fetched issues from {repo}")
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error fetching issues from {repo}: {e}")
        return []
    except Exception as e:
        logging.error(f"Error fetching issues from {repo}: {e}")
        return []

# Function to update Notion database
def update_notion_database(issue):
    url = f"https://api.notion.com/v1/pages"
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    data = {
        "parent": {"id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": issue['title']
                        }
                    }
                ]
            },
            "URL": {
                "url": issue['html_url']
            },
            "State": {
                "select": {
                    "name": issue['state']
                }
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"Updated Notion database with issue: {issue['title']}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error updating Notion database for issue {issue['title']}: {e}")
    except Exception as e:
        logging.error(f"Error updating Notion database for issue {issue['title']}: {e}")

# Main function to sync issues
def sync_github_to_notion():
    for repo in REPOSITORIES:
        issues = fetch_github_issues(repo)
        for issue in issues:
            update_notion_database(issue)

if __name__ == "__main__":
    sync_github_to_notion()
