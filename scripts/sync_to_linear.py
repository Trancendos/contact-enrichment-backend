import requests
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
LINEAR_API_KEY = os.getenv('LINEAR_API_KEY')
REPOSITORIES = [
    'Trancendos/repo1',
    'Trancendos/repo2',
    'Trancendos/repo3',
    'Trancendos/repo4',
    'Trancendos/repo5',
    'Trancendos/repo6',
    'Trancendos/repo7',
    'Trancendos/repo8',
    'Trancendos/repo9',
    'Trancendos/repo10',
]

# User and label mappings (to be defined)
GITHUB_TO_LINEAR_USER_MAP = {}  # Define user mapping here
GITHUB_TO_LINEAR_LABEL_MAP = {}  # Define label mapping here

# Function to get GitHub issues

def get_github_issues(repo):
    url = f'https://api.github.com/repos/{repo}/issues'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f'Error fetching issues from {repo}: {response.status_code} - {response.json()}')
        return []

# Function to create Linear issue

def create_linear_issue(issue_data):
    query = '''
    mutation ($input: CreateIssueInput!) {
        issue: createIssue(input: $input) {
            id
            title
        }
    }
    '''
    variables = {
        'input': {
            'title': issue_data['title'],
            'description': issue_data.get('body', ''),
            'assigneeId': GITHUB_TO_LINEAR_USER_MAP.get(issue_data['user']['login']),
            'labelIds': [GITHUB_TO_LINEAR_LABEL_MAP.get(label) for label in issue_data.get('labels', [])],
            'priority': issue_data.get('priority', None),
        }
    }
    headers = {'Authorization': f'Bearer {LINEAR_API_KEY}', 'Content-Type': 'application/json'}
    response = requests.post('https://api.linear.app/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        logging.info(f'Successfully created issue in Linear: {response.json()}')
    else:
        logging.error(f'Error creating issue in Linear: {response.status_code} - {response.json()}')

# Main function to sync issues

def sync_github_to_linear():
    for repo in REPOSITORIES:
        issues = get_github_issues(repo)
        for issue in issues:
            create_linear_issue(issue)

if __name__ == '__main__':
    sync_github_to_linear()