# API Testing Guide

This document provides examples and instructions for testing the Litigence AI API endpoints. These commands can be used to verify that your deployment is working correctly, both locally and in production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Health Check Testing](#health-check-testing)
- [Basic API Testing](#basic-api-testing)
- [Testing with Media Attachments](#testing-with-media-attachments)
- [Streaming API Testing](#streaming-api-testing)
- [Firestore Integration Testing](#firestore-integration-testing)
- [Chat History Testing](#chat-history-testing)
- [Context Awareness Testing](#context-awareness-testing)

## Prerequisites

Before running these tests, ensure:
- The Flask application is running (locally on port 8080 or on your deployed URL)
- You have `curl` installed on your system
- For tests with media, you have sample images and PDFs available

## Health Check Testing

### Health Check Endpoint (`GET /`)

Verify if the service is running and responsive:

```bash
curl -X GET http://localhost:8080/
```

Expected response: A confirmation message that the service is up and running.

## Basic API Testing

### Ask Endpoint (`POST /ask`) with JSON Question Only

Test a simple legal query without any media attachments:

```bash
curl -X POST http://localhost:8080/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is the process to file an FIR in India?"}'
```

Expected response: A JSON object containing the AI's answer to the legal question.

## Testing with Media Attachments

### Ask Endpoint with Base64-encoded Image

First, encode your image to base64:

```bash
base64 your-image.jpg > image.txt
```

Then, send the request with the encoded image:

```bash
curl -X POST http://localhost:8080/ask \
-H "Content-Type: application/json" \
-d @- << EOF
{
  "question": "Is this document legally valid?",
  "images": ["$(cat image.txt)"]
}
EOF
```

### Ask Endpoint with Base64-encoded PDF Document

Encode your PDF first:

```bash
base64 your-document.pdf > document.txt
```

Then, send the request with the encoded PDF:

```bash
curl -X POST http://localhost:8080/ask \
-H "Content-Type: application/json" \
-d @- << EOF
{
  "question": "Can you summarize this legal document?",
  "documents": ["$(cat document.txt)"]
}
EOF
```

### Ask Endpoint with Both Image and Document Attachments

Test with both types of media attachments simultaneously:

```bash
curl -X POST http://localhost:8080/ask \
-H "Content-Type: application/json" \
-d @- << EOF
{
  "question": "Please analyze these attachments for legal compliance.",
  "images": ["$(cat image.txt)"],
  "documents": ["$(cat document.txt)"]
}
EOF
```

## Streaming API Testing

### Streaming Endpoint (`POST /ask_stream`) for Real-time Responses

Test the streaming API endpoint for incremental responses:

```bash
curl -X POST http://localhost:8080/ask_stream \
-H "Content-Type: application/json" \
-d '{"question": "Explain the Indian Contract Act briefly."}'
```

> Note: The streaming response will appear incrementally in your terminal as Server-Sent Events (SSE).

## Firestore Integration Testing

### Test Saving a Chat Message

Test if the API correctly saves conversations to Firestore:

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the basic elements of a contract?",
    "user_id": "test_user_123"
  }'
```

**Expected results:**
- You should receive a JSON response with the AI's answer
- Verify data storage in Firebase console:
  1. Go to [Firebase Console](https://console.firebase.google.com/)
  2. Select your project
  3. Click on "Firestore Database" in the left menu
  4. Look for a collection called `users`
  5. Inside it, find a document with ID `test_user_123`
  6. Inside that, find a sub-collection called `chats`
  7. You should see a document with the title "Legal Consultation"

## Chat History Testing

### Test Retrieving Chat History

Test the chat history retrieval endpoint:

```bash
# Retrieve all chats for a user
curl "http://localhost:8080/chat_history?user_id=test_user_123"

# Retrieve a specific chat by title
curl "http://localhost:8080/chat_history?user_id=test_user_123&chat_title=Legal%20Consultation"
```

## Context Awareness Testing

### Test Conversational Context

Test if the API maintains context from previous questions:

```bash
# First request
curl -X POST http://localhost:8080/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is a writ petition?", "user_id": "test_user_123"}'

# Follow-up request referring to previous question
curl -X POST http://localhost:8080/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is my previous request?", "user_id": "test_user_123"}'
```

The second response should acknowledge and reference the first question about writ petitions.

## ⚠️ Important Notes

- Replace `http://localhost:8080` with your actual server URL if testing a deployed instance
- Ensure the application is running and accessible on the specified port
- For tests with media attachments, make sure your files are properly base64 encoded
- Large files may require adjusting timeout settings in curl or your server
- The streaming endpoint uses Server-Sent Events (SSE), which appear as incremental chunks in your terminal
- If testing against a production environment, ensure your firewall/security settings allow these requests
