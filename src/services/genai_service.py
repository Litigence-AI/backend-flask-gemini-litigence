from google import genai
from google.genai import types
import config
import os
import json
from pathlib import Path
from src.utils.response_utils import clean_response

def initialize_client():
    """Initialize and return the Google GenAI client"""
    try:
        # Define possible paths for credentials
        current_dir = Path(__file__).parent.parent.parent
        adc_path = current_dir / "secrets" / "application_default_credentials.json"
        
        # First try: Check if the application default credentials file exists
        if adc_path.exists():
            # Set the environment variable to point to the credentials file
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(adc_path)
            print(f"Using application default credentials from: {adc_path}")
            
            # Explicitly set project_id and location if not provided
            project_id = config.PROJECT_ID or "litigence-ai"
            location = config.LOCATION or "us-central1"
            
            print(f"Initializing Vertex AI client with project: {project_id}, location: {location}")
            return genai.Client(
                vertexai=True,
                project=project_id,
                location=location,
            )
        
        # Second try: Check for Firebase credentials and try to use them
        firebase_path = current_dir / "secrets" / "litigence-ai-firebase-adminsdk-fbsvc-d1986c607b.json"
        if firebase_path.exists():
            try:
                # Try to use Firebase credentials for Google API authentication
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(firebase_path)
                print(f"Attempting to use Firebase credentials for Google API authentication: {firebase_path}")
                
                # You may need to adjust project_id and location based on the Firebase credentials
                return genai.Client(
                    vertexai=True,
                    project="litigence-ai",  # Use the correct project ID from Firebase
                    location="us-central1",
                )
            except Exception as firebase_error:
                print(f"Could not use Firebase credentials for Google API: {firebase_error}")
                # Continue to next authentication method
                pass
        
        # Third try: Check for API key
        api_key = os.environ.get('GOOGLE_API_KEY') or config.GOOGLE_API_KEY
        if api_key:
            print("Using API key authentication for Google GenAI")
            return genai.Client(api_key=api_key)
        
        # If we've reached here, we need to handle the error gracefully for testing
        # This is only for development purposes - in production you would want to fail
        print("WARNING: Using mock client for development/testing only!")
        # Return a minimal compatible client for testing
        # In a real application, you would throw an error here
        return MockGenAIClient()
    except Exception as e:
        print(f"Error initializing GenAI client: {e}")
        raise

# Mock client for development/testing only
class MockGenAIClient:
    """A mock client that simulates the Gemini API for testing purposes."""
    def __init__(self):
        self.models = MockModelsClient()
    
    # Add other methods as needed for testing

class MockModelsClient:
    """Mock models client that returns simple responses for testing."""
    def generate_content(self, model, contents, config=None):
        print(f"MOCK API CALL: Would have called model {model} with {len(contents) if contents else 0} content items")
        # Return a simple mock response object
        return MockResponse("This is a mock response from the Gemini API for testing purposes. In production, you would need to provide valid Google API credentials.")

class MockResponse:
    """Mock response with a simple text output."""
    def __init__(self, text):
        self.text = text
        self.parts = [MockPart(text)]
    
    def __str__(self):
        return self.text

class MockPart:
    """Mock part with text."""
    def __init__(self, text):
        self.text = text
    
    def __str__(self):
        return self.text

def create_generation_config():
    """Create and return the generation configuration"""
    safety_settings = [
        types.SafetySetting(
            category=setting["category"],
            threshold=setting["threshold"]
        ) for setting in config.SAFETY_SETTINGS
    ]
    
    return types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=safety_settings,
        system_instruction=[types.Part.from_text(text=config.LAW_ASSISTANT_INSTRUCTION)],
    )