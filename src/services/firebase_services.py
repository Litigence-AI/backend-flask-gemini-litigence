import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase with credentials from environment variables or files
    
    For Google Cloud Run, we use environment variables populated from Secret Manager.
    For local development, we can use a local credentials file.
    
    Priority order:
    1. FIREBASE_CREDENTIALS environment variable (JSON string set via Secret Manager in Cloud Run)
    2. Local file in /secrets directory (for local development)
    """
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print('Firebase already initialized')
        return True
    except ValueError:
        # Attempt to get credentials from various sources
        cred = None
        
        # Option 1: JSON string in environment variable (from Secret Manager in Cloud Run)
        firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
        if firebase_creds_json:
            try:
                cred_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(cred_dict)
                print('Firebase credentials loaded from FIREBASE_CREDENTIALS environment variable (Secret Manager)')
                print(cred)
            except Exception as e:
                print(f"Error parsing Firebase credentials from environment: {e}")
        
        # Option 2: Local file in project (for local development)
        if cred is None:
            # Try standard locations for credentials file
            credential_paths = [
                'litigence-ai-firebase-adminsdk-fbsvc-d1986c607b.json',  # Current directory
                './secrets/litigence-ai-firebase-adminsdk-fbsvc-d1986c607b.json',  # Secrets directory
                '/app/secrets/litigence-ai-firebase-adminsdk-fbsvc-d1986c607b.json'  # Docker container path
            ]
            
            for path in credential_paths:
                if os.path.exists(path):
                    try:
                        cred = credentials.Certificate(path)
                        print(f'Firebase credentials loaded from file: {path}')
                        break
                    except Exception as e:
                        print(f"Error loading credentials from {path}: {e}")
        
        # Initialize Firebase if credentials were found
        if cred:
            firebase_admin.initialize_app(cred)
            return True
        else:
            print('Failed to initialize Firebase: No valid credentials found')
            return False



def save_chat_to_firestore(user_id, chat_title, user_message, ai_response):
    """
    Save a chat exchange (user message and AI response) to Firestore.
    
    Args:
        user_id (str): The ID of the user
        chat_title (str): The title of the chat session
        user_message (str): The message sent by the user
        ai_response (str): The response generated by the AI
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = firestore.client()
        try:
            current_timestamp = datetime.now()
            print(f"Current timestamp: {current_timestamp}")
        except Exception as e:
            print(f"Error with datetime: {str(e)}")

        # Create message objects
        user_message_data = {
            'role': 'user',
            'message': user_message,
            'timestamp': current_timestamp
        }
        
        ai_message_data = {
            'role': 'ai',
            'message': ai_response,
            'timestamp': current_timestamp
        }
        
        # Reference to chat document
        chat_ref = db.collection('users').document(user_id) \
                     .collection('user_chats').document(chat_title)
        
        # Update in transaction
        transaction = db.transaction()
        
        @firestore.transactional
        def update_in_transaction(transaction, doc_ref):
            doc = doc_ref.get(transaction=transaction)
            
            if doc.exists:
                transaction.update(doc_ref, {
                    'messages': firestore.ArrayUnion([user_message_data, ai_message_data]),
                    'last_updated': current_timestamp
                })
            else:
                transaction.set(doc_ref, {
                    'title': chat_title,
                    'createdAt': current_timestamp,
                    'last_updated': current_timestamp,
                    'messages': [user_message_data, ai_message_data]
                })
        
        update_in_transaction(transaction, chat_ref)
        return True
    except Exception as e:
        print(f"Error saving chat to Firestore: {e}")
        return False
