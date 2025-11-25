# Quick Start: Vertex AI Setup (5 Minutes)

## Prerequisites
- Google Cloud account ([Sign up free](https://cloud.google.com/free))
- `gcloud` CLI installed ([Download](https://cloud.google.com/sdk/docs/install))

## Setup Steps

### 1. Create GCP Project (1 min)
```bash
# Create project
gcloud projects create cyberguard-academy-dev --name="CyberGuard Academy Dev"

# Set as default
gcloud config set project cyberguard-academy-dev
```

### 2. Enable Vertex AI API (1 min)
```bash
gcloud services enable aiplatform.googleapis.com
```

### 3. Authenticate (1 min)
```bash
gcloud auth application-default login
```

### 4. Configure Environment (1 min)
```bash
# Copy example config
cp .env.example .env

# Edit .env and set:
# GOOGLE_CLOUD_PROJECT=cyberguard-academy-dev
```

### 5. Test (1 min)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run migration test
python test_vertex_migration.py
```

Expected output:
```
✓ Initialization successful
✓ Flash model response: Hello from Vertex AI!
✓ Pro model response: Pro model working!
✓ Security content response: [phishing subject line]
```

## You're Done! 🎉

Start the app:
```bash
python main.py
```

## Troubleshooting

**"GOOGLE_CLOUD_PROJECT not set"**  
→ Add `GOOGLE_CLOUD_PROJECT=your-project-id` to `.env`

**"Permission denied"**  
→ Run `gcloud auth application-default login`

**"API not enabled"**  
→ Run `gcloud services enable aiplatform.googleapis.com`

**Need more help?**  
→ See [VERTEX_AI_MIGRATION.md](VERTEX_AI_MIGRATION.md) for detailed guide

## Cost Note

Development usage typically costs **$0.10-$2.00/day**. The free tier includes $300 credit for 90 days.
