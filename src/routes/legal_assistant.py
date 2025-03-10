from flask import Blueprint, jsonify, request
from google.genai import types
from src.services import genai_service
from config import MODEL_NAME, PROJECT_ID, LOCATION, DEBUG, LAW_ASSISTANT_INSTRUCTION
from google import genai
import os
import json
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request

from src.services.firebase_services import save_chat_to_firestore

legal_bp = Blueprint('legal', __name__)

@legal_bp.route("/ask", methods=["POST"])
def ask_legal_question():
    try:
        # Get the question from the request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing required field: question"}), 400
            
        question = data.get('question')
        user_id = data.get('user_id', 'anonymous')
        
        APP_DEFAULT_CREDENTIALS = None
        
        # Check if GOOGLE_APPLICATION_CREDENTIALS environment variable is set
        if not DEBUG:
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            # Let the Google client library handle authentication
            client = genai.Client(
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
                    APP_DEFAULT_CREDENTIALS = UserCredentials(
                        token=None,  # No token initially
                        refresh_token=credentials_info.get('refresh_token'),
                        client_id=credentials_info.get('client_id'),
                        client_secret=credentials_info.get('client_secret'),
                        token_uri='https://oauth2.googleapis.com/token',
                        scopes=['https://www.googleapis.com/auth/cloud-platform']
                    )
                    
                    # Refresh the token
                    request_obj = Request()
                    APP_DEFAULT_CREDENTIALS.refresh(request_obj)
                    
                    client = genai.Client(
                        credentials=APP_DEFAULT_CREDENTIALS,
                        vertexai=True,
                        project=PROJECT_ID,
                        location=LOCATION,
                    )
                else:
                    return jsonify({"error": "Invalid credentials format in application_default_credentials.json"}), 500
            except Exception as e:
                return jsonify({"error": f"Error loading credentials: {str(e)}"}), 500

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
        
        response_text = response.text
        
        # Save to Firebase if user_id is provided
        if user_id != 'anonymous':
            try:
                save_chat_to_firestore(user_id, question, response_text)
            except Exception as e:
                print(f"Warning: Failed to save chat to Firestore: {str(e)}")

        return jsonify({
            "response": response_text,
            "user_id": user_id
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
