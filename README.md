## Overview
This application provides a Flask-based API that can be run locally or deployed in a Google Cloud environment. Below are step-by-step instructions on installing dependencies, configuring Google Cloud, running the application, and testing the API locally.

---

## Prerequisites
1. **Python 3** (for running the Flask application)  
2. **Google Cloud SDK** (for Google Cloud integration)  
3. **curl** (for API testing)

---

## Running the Application Locally

1. Clone or open the repository.  
2. Ensure you have installed Python dependencies (if applicable, use `pip install -r requirements.txt`).  
3. Run the application:
```bash
python main.py
```
This starts the application at `http://localhost:8000`.

---

## Installing Google Cloud SDK

Use the steps below on a Linux x86_64 machine:

```bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xf google-cloud-cli-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh
```

(Optional) Add the Google Cloud CLI to your PATH:
```bash
# Example approach
echo "source ~/google-cloud-sdk/path.bash.inc" >> ~/.bashrc
source ~/.bashrc
```
Initialize the SDK:
```bash
./google-cloud-sdk/bin/gcloud init
```

Follow the prompts to choose your Google Cloud project and configure default settings.

---

## Authenticating with Google Cloud

Authenticate using Application Default Credentials:
```bash
./google-cloud-sdk/bin/gcloud auth application-default login
```
Follow the sign-in process in your browser, and your credentials will be saved locally.

---

## Granting Permissions to the Service Account

You may need to grant specific permissions, for example:
```bash
./google-cloud-sdk/bin/gcloud projects add-iam-policy-binding law-ai-437009 \
--member=serviceAccount:916007394186-compute@developer.gserviceaccount.com \
--role=roles/cloudbuild.builds.builder
```

---

## Region and Zone Configuration

Set your preferred default compute region and zone:
```bash
gcloud config set compute/zone asia-south1-a
gcloud config set compute/region asia-south1
```

---

## Testing the API Locally

Once the app is running on `http://localhost:8000`, you can test an endpoint with `curl`, for example:
```bash
curl --location 'http://localhost:8000/ask' \
--header 'Content-Type: application/json' \
--data '{"question":"What are the rights I have as a citizen of India?"}'
```
You should receive a JSON response containing the answer from your service.

---

## Additional Notes

- Check the generated `.boto` file if you plan to interact with Google Cloud Storage.  
- Your credentials are stored at `~/.config/gcloud/application_default_credentials.json`.  
- Ensure you have billing enabled on the selected project if you use any paid Google Cloud services.

---