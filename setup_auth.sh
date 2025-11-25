#!/bin/bash
# Authentication Setup Helper for CyberGuard Academy
# This script helps set up authentication for Vertex AI in WSL/Linux environments

set -e  # Exit on error

echo "=========================================="
echo "CyberGuard Academy - Authentication Setup"
echo "=========================================="
echo ""

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project configured. Please run:"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Current Project: $PROJECT_ID"
echo ""
echo "Choose authentication method:"
echo "  1) Service Account Key (Recommended for WSL/development)"
echo "  2) Application Default Credentials (Try again)"
echo "  3) Use existing gcloud credentials as ADC"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Creating service account for CyberGuard Academy..."
        
        SA_NAME="cyberguard-dev"
        SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
        KEY_FILE="$HOME/.config/gcloud/cyberguard-key.json"
        
        # Create service account
        if gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
            echo "✓ Service account already exists: $SA_EMAIL"
        else
            gcloud iam service-accounts create $SA_NAME \
                --display-name="CyberGuard Academy Development" \
                --description="Service account for CyberGuard Academy development"
            echo "✓ Service account created"
        fi
        
        # Grant Vertex AI User role
        echo "Granting Vertex AI permissions..."
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="roles/aiplatform.admin" \
            --condition=None \
            2>/dev/null || true
        
        # Create key
        echo "Creating service account key..."
        mkdir -p $(dirname $KEY_FILE)
        gcloud iam service-accounts keys create $KEY_FILE \
            --iam-account=$SA_EMAIL
        
        echo ""
        echo "✓ Service account key created: $KEY_FILE"
        echo ""
        echo "Setting GOOGLE_APPLICATION_CREDENTIALS..."
        export GOOGLE_APPLICATION_CREDENTIALS="$KEY_FILE"
        
        # Add to .bashrc if not already there
        if ! grep -q "GOOGLE_APPLICATION_CREDENTIALS.*cyberguard-key.json" ~/.bashrc 2>/dev/null; then
            echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$KEY_FILE\"" >> ~/.bashrc
            echo "✓ Added to ~/.bashrc"
        fi
        
        echo ""
        echo "======================================"
        echo "✓ Authentication configured!"
        echo "======================================"
        echo ""
        echo "To use in current terminal:"
        echo "  export GOOGLE_APPLICATION_CREDENTIALS=\"$KEY_FILE\""
        echo ""
        echo "Or restart your terminal (already added to ~/.bashrc)"
        ;;
        
    2)
        echo ""
        echo "Attempting application-default login..."
        gcloud auth application-default login --no-launch-browser
        ;;
        
    3)
        echo ""
        echo "Using gcloud credentials as ADC..."
        ADC_PATH="$HOME/.config/gcloud/application_default_credentials.json"
        GCLOUD_CREDS_PATH="$HOME/.config/gcloud/legacy_credentials/$(gcloud config get-value account 2>/dev/null)/adc.json"
        
        mkdir -p $(dirname $ADC_PATH)
        
        # Copy gcloud credentials
        if [ -f "$GCLOUD_CREDS_PATH" ]; then
            cp "$GCLOUD_CREDS_PATH" "$ADC_PATH"
            echo "✓ ADC configured from existing gcloud credentials"
        else
            echo "❌ Could not find gcloud credentials. Please try option 1 or 2."
            exit 1
        fi
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Testing authentication..."
echo ""

# Test with Python
cd /mnt/c/Users/elson/Software/Projects/CyberGuard-Academy
source .venv/bin/activate 2>/dev/null || true
python test_vertex_migration.py
