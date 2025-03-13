from google.genai import types
from google import genai
import os
import json
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request
from config import MODEL_NAME, PROJECT_ID, LOCATION, DEBUG, LAW_ASSISTANT_INSTRUCTION, SAFETY_SETTINGS

def initialize_genai_client():
    """Initialize and return a Google Generative AI client."""
    if not DEBUG:
        # Let the Google client library handle authentication
        return genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )
    else:
        # For local development, load credentials from file
        try:
            credentials_path = './secrets/application_default_credentials.json'
            with open(credentials_path, 'r') as f:
                credentials_info = json.load(f)

            # Make sure it's an authorized_user type
            if credentials_info.get('type') == 'authorized_user':
                app_default_credentials = UserCredentials(
                    token=None,  # No token initially
                    refresh_token=credentials_info.get('refresh_token'),
                    client_id=credentials_info.get('client_id'),
                    client_secret=credentials_info.get('client_secret'),
                    token_uri='https://oauth2.googleapis.com/token',
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                
                # Refresh the token
                request_obj = Request()
                app_default_credentials.refresh(request_obj)
                
                return genai.Client(
                    credentials=app_default_credentials,
                    vertexai=True,
                    project=PROJECT_ID,
                    location=LOCATION,
                )
            else:
                raise ValueError("Invalid credentials format in application_default_credentials.json")
        except Exception as e:
            raise Exception(f"Error loading credentials: {str(e)}")

def generate_legal_response(question):
    """Generate a response to a legal question using Gemini."""
    client = initialize_genai_client()
    
    # Create content for the model
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=question)
            ]
        )
    ]
    
    # Create generation config
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        system_instruction=[types.Part.from_text(text=LAW_ASSISTANT_INSTRUCTION)],
    )

    # Generate response
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=generate_content_config,
    )
    
    return response.text

def generate_legal_response_stream(question):
    """
    Generate a streamed response to a legal question using Gemini.
    
    Args:
        question (str): The legal question text
        
    Yields:
        str: Chunks of the generated response as they become available
    """
    client = initialize_genai_client()
    
    # Create content for the model
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=question)
            ]
        )
    ]
    
    # Create generation config
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        system_instruction=[types.Part.from_text(text=LAW_ASSISTANT_INSTRUCTION)],
    )

    try:
        # Generate response as a stream
        for chunk in client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
            config=generate_content_config,
        ):
            # Skip empty chunks
            if not chunk.candidates or not chunk.candidates[0].content.parts:
                continue
                
            # Yield each chunk of text as it arrives
            if hasattr(chunk, 'text'):
                yield chunk.text
            elif hasattr(chunk.candidates[0].content.parts[0], 'text'):
                yield chunk.candidates[0].content.parts[0].text
    except Exception as e:
        # Yield the error as part of the stream
        yield f"Error generating response: {str(e)}"
