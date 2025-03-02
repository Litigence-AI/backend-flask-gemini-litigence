#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Run Flask app
flask --app main.py --debug run --host=0.0.0.0 --port=8080
