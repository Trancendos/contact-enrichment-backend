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

## API Endpoints

- `/api/auth/*` - Authentication endpoints
- `/api/enrichment/*` - Contact enrichment endpoints
- `/api/suggestions/*` - Contact suggestions
- `/api/tagging/*` - AI tagging endpoints
- `/api/history/*` - Contact history
- `/api/*` - Contact and user management

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
