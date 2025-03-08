# Google Cloud Run CI/CD Setup Guide

This document provides step-by-step instructions for setting up continuous integration and continuous deployment (CI/CD) for your application using Google Cloud Run and connecting it to your Git repository.

## Prerequisites
- Google Cloud Platform account with billing enabled
- Git repository with your project code (GitHub, GitLab, or Bitbucket)
- Project code that includes a Dockerfile or buildpacks compatibility

## Connecting Git Repository to Cloud Run CI/CD

### Step 1: Enable Required APIs

First, make sure the necessary APIs are enabled in your Google Cloud project:

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  cloudresourcemanager.googleapis.com \
  artifactregistry.googleapis.com
```

### Step 2: Connect Your Git Repository

1. **Go to Cloud Run Console**
   - Visit the [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "Cloud Run" in the left sidebar
   - Click "Create Service"

2. **Select Continuous Deployment**
   - In the "Create Service" page, select "Continuously deploy from a repository"
   - Click "Set up with Cloud Build"

3. **Choose Repository Provider**
   - Select your repository provider (GitHub, GitLab, or Bitbucket)
   - Authenticate and authorize Google Cloud Build to access your repositories
   - Select your repository from the list

4. **Configure Build Settings**
   - Select the branch to deploy (e.g., `main` or `master`)
   - Choose build type:
     - **Dockerfile**: If your repository contains a Dockerfile
     - **Buildpacks**: If you want Google Cloud to determine how to build your app
   - Set the build location (typically the root directory `/`)
   - Optionally configure build timeout and service account

### Step 3: Configure Cloud Run Service

1. **Set Service Name**
   - Enter a name for your Cloud Run service

2. **Choose Region**
   - Select a region (e.g., `asia-south1` for Mumbai)

3. **Set Memory and CPU Allocation**
   - Specify memory and CPU requirements for your container

4. **Configure Autoscaling**
   - Set minimum and maximum instances
   - Define concurrency (requests per instance)

5. **Set Traffic Settings**
   - Choose whether to send all traffic to the new revision or not

6. **Enable Authentication**
   - Decide if you want to require authentication or allow unauthenticated invocations

7. **Review and Create**
   - Click "Create" to set up the continuous deployment pipeline

## Setting Environment Variables and Secrets

### Adding Environment Variables

1. **During Service Creation**
   - In the "Container, Networking, Security" section of service creation
   - Click "Variables & Secrets" tab
   - Add environment variables by clicking "+ Add Variable"
   - Enter key-value pairs for your environment variables

2. **For Existing Services**
   - Go to the Cloud Run service details page
   - Click "Edit & Deploy New Revision"
   - Go to "Variables & Secrets" tab
   - Add or modify environment variables
   - Click "Deploy" to apply changes

### Adding Secrets

1. **Create Secrets in Secret Manager**
   - Go to Security > Secret Manager in GCP Console
   - Click "Create Secret"
   - Enter a name for your secret (e.g., `FIREBASE_CREDENTIALS`)
   - Enter the secret value (for Firebase SDK JSON, paste the entire JSON content)
   - Click "Create Secret"

2. **Grant Access to Cloud Run**
   - In Secret Manager, select your secret
   - Go to the "Permissions" tab
   - Click "Add Member"
   - Add your Cloud Run service account with the "Secret Manager Secret Accessor" role
   - The service account typically has the format: `service-PROJECT_NUMBER@serverless-robot-prod.iam.gserviceaccount.com`

3. **Mount Secrets in Cloud Run**
   - Go to your Cloud Run service
   - Click "Edit & Deploy New Revision"
   - Go to "Variables & Secrets" tab
   - Click "Add Secret"
   - Select the secret you created
   - Choose mounting method:
     - **Environment variable**: Set a variable name that will contain the secret value
     - **Volume mount**: Mount the secret as a file at a specified path
   - For Firebase credentials, you might want to mount it as a file at `/secrets/firebase-credentials.json`
   - Click "Deploy" to apply changes

4. **Accessing Secrets in Your Code**

   For environment variable:
   ```python
   import os
   import json
   
   # If mounted as environment variable
   firebase_credentials = json.loads(os.environ['FIREBASE_CREDENTIALS'])
   ```

   For mounted file:
   ```python
   import os
   
   # If mounted as file
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/secrets/firebase-credentials.json'
   ```

## Triggering Deployments

Once CI/CD is set up, new deployments will automatically trigger when you:

1. Push changes to the configured branch of your repository
2. Cloud Build will automatically build a new container image
3. Cloud Run will deploy the new image as a new revision
4. Traffic will be routed to the new revision based on your traffic settings

## Monitoring Deployments

You can monitor your deployments in the Google Cloud Console:

1. **Cloud Build History**
   - View build logs and status at Cloud Build > History

2. **Cloud Run Revisions**
   - Check deployment status and revision history in Cloud Run > Service Details > Revisions

## Troubleshooting

- **Build Failures**: Check Cloud Build logs for errors in your build process
- **Deployment Failures**: Review Cloud Run revision details for container startup issues
- **Secret Access Issues**: Verify IAM permissions and secret mounting configuration
- **Network Connectivity**: Check VPC and ingress/egress settings if applicable
