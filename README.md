## Overview
This application provides a Flask-based API that can be run locally or deployed in a Google Cloud environment. Below are step-by-step instructions on installing dependencies, configuring Google Cloud, running the application, and testing the API locally.

---

## Prerequisites
1. **Python 3** (for running the Flask application)  
2. **Google Cloud SDK** (for Google Cloud integration)  
3. **curl** (for API testing)

---

## Running the Application Locally

### Clone or open the repository.  

### Create a virtual environment
```python -m venv .venv```

### Activate it (this will need to be done each time you start a new shell)
```source .venv/bin/activate```

### Install dependencies
```pip install -r requirements.txt```

## Installing Google Cloud SDK

Use the steps below on a Linux x86_64 machine:

```bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xf google-cloud-cli-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh
```

Opt Yes to add sdk path to rc and Open a new terminal shell

Initialize the SDK:
```bash
gcloud init
```

Follow the prompts to choose your Google Cloud project and configure default settings.

---

## Authenticating with Google Cloud

Authenticate using Application Default Credentials:
```bash
gcloud auth application-default login
```
Follow the sign-in process in your browser, and your credentials will be saved locally.

---

## Granting Permissions to the Service Account

You may need to grant specific permissions, for example:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
--member=serviceAccount:SERVICE_ACCOUNT_EMAIL \
--role=ROLE_NAME
```

---

## Region and Zone Configuration

Set your preferred default compute region and zone:
```bash
gcloud config set compute/zone asia-south1-a
gcloud config set compute/region asia-south1
```

---

Run the application:
```bash
python main.py
```
This starts the application at `http://localhost:8000`.

---

## Testing the API Locally

Once the app is running on `http://localhost:8080`, you can test an endpoint with `curl`, for example:
```bash
curl --location 'http://localhost:8080/ask' \
--header 'Content-Type: application/json' \
--data '{"question":"What are the rights I have as a citizen of India?"}'
```
You should receive a JSON response containing the answer from your service.

For comprehensive API testing examples including media uploads, Firestore integration, and streaming responses, refer to the [API Testing Guide](docs/api_testing_guide.md).

---

## Additional Notes

- Check the generated `.boto` file if you plan to interact with Google Cloud Storage.  
- Your credentials are stored at `~/.config/gcloud/application_default_credentials.json`.  
- Ensure you have billing enabled on the selected project if you use any paid Google Cloud services.
- For Firebase SDK JSON generation and configuration, refer to the [Firebase Setup Guide](docs/firebase_setup.md).
- For setting up Google Cloud Run CI/CD with your Git repository and configuring environment variables and secrets, see the [Google Cloud Run CI/CD Setup Guide](docs/cloud_run_setup.md).

---

### Build the Docker Image
```bash
sudo docker build -t litigence-ai-backend .
```

### Run the Docker Container
```bash
docker run -p 8080:8080 \
  -e FLASK_ENV=placeholder \
  -e PORT=placeholder \
  -e PROJECT_ID=placeholder \
  -e LOCATION=placeholder \
  litigence-ai-backend
```

### Check Running Containers
```bash
sudo docker ps
```

### Stop a Running Container
```bash
sudo docker stop <container_id>
```
