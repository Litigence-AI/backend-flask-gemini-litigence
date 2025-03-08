# Firebase Setup Guide

This document provides instructions for generating and setting up Firebase SDK JSON configuration for your project.

## Prerequisites
- Google account with access to [Firebase Console](https://console.firebase.google.com/)
- Firebase project created or access to an existing project

## Generating Firebase SDK JSON

1. **Access Firebase Console**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Sign in with your Google account

2. **Select Your Project**
   - Choose your existing project or create a new one
   - If creating a new project, follow the on-screen instructions

3. **Add Firebase to Your App**
   - From the project overview page, click the gear icon (⚙️) next to "Project Overview"
   - Select "Project settings"
   - Scroll down to the "Your apps" section
   - Click the "</>" icon to add a web app (or select the appropriate platform)
   - Register your app with a nickname (this is for internal reference only)
   - Check the "Also set up Firebase Hosting" option if needed

4. **Generate and Download Configuration**
   - After registering, you'll be presented with Firebase configuration options
   - For a service account JSON file (used for server-side applications):
     - Go to "Project settings" > "Service accounts" tab
     - Click "Generate new private key"
     - Save the JSON file securely (this contains sensitive credentials)

5. **Secure Your Firebase SDK JSON**
   - **IMPORTANT**: Never commit this file to version control
   - Store it securely and use environment variables or secret management services
   - For local development, keep it in a location outside your git repository
   - For production, use Google Cloud Run secrets (described in the Cloud Run setup document)

## Using Firebase SDK JSON in Your Application

### Local Development

1. **Place the JSON file**
   - Save the Firebase SDK JSON file to a secure location outside your git repository
   - You can rename it to something like `firebase-credentials.json`

2. **Configure Environment Variables**
   - Set an environment variable pointing to your JSON file:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/firebase-credentials.json"
     ```
   - Alternatively, for Flask applications, you can load the file directly:
     ```python
     import firebase_admin
     from firebase_admin import credentials
     
     cred = credentials.Certificate('path/to/firebase-credentials.json')
     firebase_admin.initialize_app(cred)
     ```

### Production Environment

For production, refer to the Google Cloud Run setup documentation on how to:
- Store the Firebase SDK JSON as a secret
- Mount the secret as a file or environment variable in your container

## Troubleshooting

- If you encounter permission issues, ensure your service account has the necessary IAM roles
- For Firebase Authentication issues, verify that the appropriate authentication methods are enabled in the Firebase Console
- For Firestore access problems, check that your security rules allow the operations you're attempting
