# Contact Enrichment Backend

A Flask-based backend API for contact enrichment with AI-powered tagging and relationship management.

## Features

- Contact management with enrichment capabilities
- AI-powered contact tagging using OpenAI
- Contact relationship tracking
- Contact history and suggestions
- User authentication
- PostgreSQL database with Supabase

## Documentation

For detailed information about API integrations, development strategies, and cost analysis:

- **[API Integration Summary](./API_INTEGRATION_SUMMARY.md)** - 📋 **Start here!** Executive overview and recommendations
- **[Quick Reference Guide](./API_INTEGRATION_QUICK_REFERENCE.md)** - 🚀 At-a-glance reference for developers
- **[API Marketplace Analysis](./API_MARKETPLACE_ANALYSIS.md)** - 📊 Comprehensive analysis of API integrations, pros/cons
- **[API Cost Calculation](./API_COST_CALCULATION.md)** - 💰 Detailed cost analysis, ROI calculations, financial projections
- **[Development Strategy](./DEVELOPMENT_STRATEGY.md)** - 🛠️ Implementation roadmap, best practices, code examples

## Production Deployment

The application is configured to deploy automatically to Google Cloud Run when changes are pushed to the `main` branch.

### Required Secrets

The following secrets must be configured in Google Cloud Secret Manager:

1. **SECRET_KEY** - Flask application secret key for session management (generate a secure random string)
2. **SUPABASE_URL** - Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)
3. **SUPABASE_KEY** - Your Supabase database password/key
4. **OPENAI_API_KEY** - OpenAI API key for AI tagging features

### Setting up Secrets in Google Cloud

```bash
# Create secrets in Google Cloud Secret Manager
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "https://your-project.supabase.co" | gcloud secrets create SUPABASE_URL --data-file=-
echo -n "your-supabase-key" | gcloud secrets create SUPABASE_KEY --data-file=-
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding SECRET_KEY \
    --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor

# Repeat for other secrets...
```

### Required GitHub Secrets

Configure these in your GitHub repository settings under Settings > Secrets and variables > Actions:

- **GCP_PROJECT_ID** - Your Google Cloud project ID
- **GCP_SA_KEY** - Service account key JSON with permissions to deploy to Cloud Run

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL (or Supabase account)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Trancendos/contact-enrichment-backend.git
cd contact-enrichment-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables (create a `.env` file or export):
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-key"
export OPENAI_API_KEY="your-openai-api-key"
export SECRET_KEY="your-local-secret-key"
export ENVIRONMENT="development"
```

5. Run the application:
```bash
python src/main.py
```

The application will run on `http://localhost:5000` with debug mode enabled.

## Production Configuration

In production, the application:
- Runs with `ENVIRONMENT=production` (debug mode disabled)
- Uses Gunicorn as the WSGI server
- Loads secrets from Google Cloud Secret Manager
- Serves static frontend files from the `/static` directory
- Enforces HTTPS and security best practices

## Architecture Overview

The application is a monolithic Flask backend with a modular structure. The code is organized into the following directories:

- `src/models`: Contains SQLAlchemy models for all database tables.
- `src/routes`: Defines the API endpoints and handles incoming requests.
- `src/services`: Contains the business logic for the application.
- `src/middleware`: Contains middleware for handling authentication and database sessions.

## API Endpoints

### Authentication

- `POST /api/auth/register`: Register a new user.
- `POST /api/auth/login`: Log in a user.
- `POST /api/auth/logout`: Log out the current user.
- `GET /api/auth/me`: Get the current user's information.

### Contact Management

- `POST /api/contacts`: Create a new contact.
- `PUT /api/contacts/<contact_id>`: Update an existing contact.
- `DELETE /api/contacts/<contact_id>`: Delete a contact.
- `POST /api/contacts/split_phone`: Split a phone number from a contact into a new contact.
- `POST /api/contacts/split_all`: Split all phone numbers and emails from a contact into new contacts.
- `POST /api/contacts/merge`: Merge multiple contacts into a single contact.

### Contact Enrichment

- `POST /api/enrich_contact`: Enrich a contact's information using the Explorium service.

### Suggestions

- `POST /api/suggestions/analyze`: Analyze contacts and generate suggestions.
- `GET /api/suggestions/list`: Get all pending suggestions for the current user.
- `POST /api/suggestions/<suggestion_id>/approve`: Approve a suggestion.
- `POST /api/suggestions/<suggestion_id>/reject`: Reject a suggestion.
- `POST /api/suggestions/bulk_action`: Approve or reject multiple suggestions at once.

### Tagging

- `POST /api/tagging/suggest_tags`: Suggest tags for a contact using AI.
- `POST /api/tagging/suggest_tags_batch`: Suggest tags for multiple contacts using AI.

### History and Backups

- `GET /api/history/contact/<contact_id>`: Get the history for a specific contact.
- `GET /api/history/user`: Get all history for the current user.
- `GET /api/history/recent`: Get recent actions for the current user.
- `POST /api/history/undo/<history_id>`: Undo a specific action.
- `POST /api/backup/create`: Create a backup of all contacts.
- `GET /api/backup/list`: List all backups for the current user.
- `POST /api/backup/restore/<backup_id>`: Restore contacts from a backup.

### Relationships

- `POST /api/relationships`: Create a new relationship between two contacts.
- `GET /api/relationships/<contact_id>`: Get all relationships for a specific contact.
- `PUT /api/relationships/<relationship_id>`: Update an existing relationship.
- `DELETE /api/relationships/<relationship_id>`: Delete a relationship.

## Technology Stack

- **Backend Framework**: Flask 3.1.2
- **WSGI Server**: Gunicorn 23.0.0 (production)
- **Database**: PostgreSQL via Supabase
- **ORM**: SQLAlchemy 2.0.43
- **AI/ML**: OpenAI API
- **Deployment**: Google Cloud Run
- **CI/CD**: GitHub Actions

## License

This project is proprietary and confidential. 
