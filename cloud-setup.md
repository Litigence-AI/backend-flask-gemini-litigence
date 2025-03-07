# Google Cloud Run Setup Guide for Litigence-AI Backend

This guide explains how to properly set up your application on Google Cloud Run with secure secret management.

## 1. Set Up Google Cloud Project

```bash
# Set your project ID
PROJECT_ID=your-project-id

# Create a new project (if needed)
gcloud projects create $PROJECT_ID

# Set the project as your default
gcloud config set project $PROJECT_ID

# Enable necessary APIs
gcloud services enable \
  run.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

## 2. Configure Secret Manager

```bash
# Create a secret for Firebase credentials
gcloud secrets create firebase-credentials --replication-policy="automatic"

# Add the Firebase credentials from your local file
gcloud secrets versions add firebase-credentials --data-file="./secrets/litigence-ai-firebase-adminsdk-fbsvc-d1986c607b.json"

# Optional: Add other secrets if needed
gcloud secrets create google-ai-api-key --replication-policy="automatic"
gcloud secrets versions add google-ai-api-key --data-file="./secrets/api-key.txt"
```

## 3. Create Service Account for Deployment

```bash
# Create a service account for GitHub Actions
gcloud iam service-accounts create github-actions-deployer

# Grant the necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Create and download a key for the service account
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions-deployer@$PROJECT_ID.iam.gserviceaccount.com
```

## 4. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

- `GCP_PROJECT_ID` - Your Google Cloud project ID
- `GCP_SA_KEY` - The entire contents of the key.json file created above
- `GCP_LOCATION` - Your preferred GCP region (e.g., asia-south1)

## 5. Manual Deployment (If Needed)

```bash
# Build the Docker image locally
docker build -t gcr.io/$PROJECT_ID/litigence-backend:latest .

# Push the Docker image to Google Container Registry
docker push gcr.io/$PROJECT_ID/litigence-backend:latest

# Deploy to Cloud Run with secret access
gcloud run deploy litigence-backend \
  --image gcr.io/$PROJECT_ID/litigence-backend:latest \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=$PROJECT_ID,LOCATION=asia-south1,FLASK_ENV=production" \
  --set-secrets "FIREBASE_CREDENTIALS=firebase-credentials:latest" \
  --memory 512Mi \
  --cpu 1
```

## 6. Local Testing with Docker

```bash
# Build the Docker image
docker build -t litigence-backend:local .

# Run the container with mounted secrets
docker run -p 8080:8080 -v "$(pwd)/secrets:/app/secrets:ro" litigence-backend:local
```
