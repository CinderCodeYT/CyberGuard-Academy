# Migration to Vertex AI - Setup Guide

## Why We Migrated

The consumer Gemini API has strict safety filters that block educational security content, making it unsuitable for CyberGuard Academy's training scenarios. **Vertex AI** provides:

✅ **Full safety control** - BLOCK_NONE settings work for all harm categories  
✅ **Enterprise reliability** - Better SLA and quota management  
✅ **GCP integration** - Native logging, tracing, and monitoring  
✅ **Scalability** - Better suited for production deployments  

## Prerequisites

Before you begin, you'll need:
- A Google Cloud Platform (GCP) account
- Basic familiarity with GCP Console
- `gcloud` CLI installed ([Installation Guide](https://cloud.google.com/sdk/docs/install))

## Step-by-Step Setup

### 1. Create a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., `cyberguard-academy-dev`)
4. Note your **Project ID** (you'll need this)

### 2. Enable Vertex AI API

1. Go to [Vertex AI API page](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
2. Select your project
3. Click **"Enable"**
4. Wait for activation (usually takes 1-2 minutes)

### 3. Set Up Authentication

You have two options for authentication:

#### Option A: Application Default Credentials (Recommended for Development)

```bash
# Authenticate with your Google account
gcloud auth application-default login

# Set your default project
gcloud config set project YOUR_PROJECT_ID
```

#### Option B: Service Account (Recommended for Production)

```bash
# Create a service account
gcloud iam service-accounts create cyberguard-sa \
    --display-name="CyberGuard Academy Service Account"

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:cyberguard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/cyberguard-key.json \
    --iam-account=cyberguard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/cyberguard-key.json
```

### 4. Update Your Environment File

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:

```dotenv
# Replace with your actual GCP project ID
GOOGLE_CLOUD_PROJECT=your-actual-project-id
GOOGLE_CLOUD_REGION=us-central1
VERTEX_AI_LOCATION=us-central1
```

**Important Notes:**
- Remove any `GOOGLE_API_KEY` entries (no longer needed)
- Ensure `GOOGLE_CLOUD_PROJECT` matches your GCP project ID exactly
- Region and location can be changed based on your needs ([Available Regions](https://cloud.google.com/vertex-ai/docs/general/locations))

### 5. Install Dependencies

```bash
# The Vertex AI SDK is already in pyproject.toml
# Just reinstall dependencies
pip install -e .
```

### 6. Test the Migration

Run the migration test script:

```bash
python test_vertex_migration.py
```

Expected output:
```
==============================================================
Testing Vertex AI Migration
==============================================================

1. Configuration Check:
   Project ID: your-project-id
   Location: us-central1
   Pro Model: gemini-2.5-pro
   Flash Model: gemini-2.5-flash

2. Initializing GeminiClient...
   ✓ Initialization successful

3. Testing Flash model (high-volume generation)...
   ✓ Flash model response: Hello from Vertex AI!

4. Testing Pro model (complex reasoning)...
   ✓ Pro model response: Pro model working!

5. Testing with system instruction...
   ✓ System instruction response: [response]

6. Testing educational security content generation...
   ✓ Security content response: [phishing subject line]

7. Testing conversation with context...
   ✓ Context-aware response: [response]

==============================================================
Migration Test Complete!
==============================================================
```

## Troubleshooting

### Error: "GOOGLE_CLOUD_PROJECT not found"
**Solution:** Ensure you've set `GOOGLE_CLOUD_PROJECT` in your `.env` file.

### Error: "Permission denied" or "403 Forbidden"
**Solution:** 
1. Verify Vertex AI API is enabled
2. Check your authentication:
   ```bash
   gcloud auth application-default print-access-token
   ```
3. Ensure your account/service account has `roles/aiplatform.user` role

### Error: "Could not automatically determine credentials"
**Solution:** Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`

### Error: "Content blocked" for educational content
**Solution:** This shouldn't happen with Vertex AI. If it does:
1. Verify you're using Vertex AI (check console output)
2. Confirm safety settings in `gemini_client.py` are set to `BLOCK_NONE`
3. File an issue on the repository

### Error: "Quota exceeded"
**Solution:** 
1. Check your [Vertex AI quotas](https://console.cloud.google.com/iam-admin/quotas?filter=aiplatform)
2. Request quota increase if needed
3. Consider using Flash model more (cheaper and faster)

## Cost Considerations

Vertex AI pricing is pay-as-you-go:

| Model | Input | Output |
|-------|--------|--------|
| Gemini 2.5 Flash | $0.075 / 1M chars | $0.30 / 1M chars |
| Gemini 2.5 Pro | $1.25 / 1M chars | $5.00 / 1M chars |

**Tips to minimize costs:**
- Use Flash model for Threat Actors (high volume, simpler tasks)
- Use Pro model only for Game Master (complex reasoning)
- Set appropriate `max_tokens` limits
- Implement caching for common prompt segments (future enhancement)

For development, typical costs are **$0.10-$2.00 per day** depending on usage.

## What Changed

### Removed
- ❌ `google-generativeai` package (consumer API)
- ❌ `GOOGLE_API_KEY` environment variable
- ❌ API key authentication

### Added
- ✅ Uses existing `google-cloud-aiplatform` package
- ✅ `GOOGLE_CLOUD_PROJECT` environment variable (required)
- ✅ GCP authentication (gcloud or service account)
- ✅ Full safety control with `BLOCK_NONE` for educational content

### Code Changes
- `cyberguard/gemini_client.py`: Completely rewritten to use Vertex AI SDK
- `cyberguard/config.py`: Removed `google_api_key`, made `google_cloud_project` required
- `pyproject.toml`: Removed `google-generativeai` dependency

All agent code remains unchanged - the `GeminiClient` API is backward compatible.

## Next Steps

After successful migration:

1. Run the full test suite:
   ```bash
   pytest tests/
   ```

2. Start the application:
   ```bash
   python main.py
   ```

3. Verify scenarios work correctly with realistic phishing content

4. Monitor costs in [GCP Console](https://console.cloud.google.com/billing)

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all setup steps were completed
3. Check [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs)
4. File an issue on the repository with the full error message

## Reverting (Not Recommended)

If you need to revert to the consumer API (not recommended due to safety limitations):

```bash
git revert <migration-commit-hash>
pip install google-generativeai
# Add GOOGLE_API_KEY back to .env
```

However, note that phishing scenarios may be blocked by safety filters.
