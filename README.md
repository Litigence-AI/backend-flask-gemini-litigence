
## Running the Application Locally

To run the application locally:

```bash
python main.py
```

## Installing Google Cloud SDK

Install the Google Cloud SDK by following the instructions [here](https://cloud.google.com/sdk/docs/install).

## Authenticating with Google Cloud

Authenticate with Google Cloud:

```bash
gcloud auth application-default login
```

## Granting Permissions to the Service Account

Grant permissions to the service account:

```bash
./google-cloud-sdk/bin/gcloud projects add-iam-policy-binding law-ai-437009 \
--member=serviceAccount:916007394186-compute@developer.gserviceaccount.com \
--role=roles/cloudbuild.builds.builder
```

## Testing the API Locally

Test the API using:

```bash
curl -X POST http://localhost:8080/ask -H "Content-Type: application/json" -d '{"question":"What are the rights I have as a citizen of India?"}'
```

## Deploying to Google Cloud Run

Deploy the application to Cloud Run:

```bash
./google-cloud-sdk/bin/gcloud run deploy --source .
```

## Additional Resources

- Flask App on Google Cloud Run: [Quickstart Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)
- Google Cloud SDK Installation: [Instructions](https://cloud.google.com/sdk/docs/install)
