from flask import Blueprint, jsonify, request
from google.genai import types
from src.services import genai_service, media_service
from firebase_admin import firestore

from src.services.firebase_services import save_chat_to_firestore

legal_bp = Blueprint('legal', __name__)

# Global chat history to store user and AI exchanges
chat_history = []

@legal_bp.route("/ask", methods=["POST"])
def ask_legal_question():
    global chat_history  # Use the global chat history
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    # Extract question and optional media
    question = request.json.get("question")
    images = request.json.get("images", [])
    documents = request.json.get("documents", [])
    
    if not question and not (images or documents):
        return jsonify({"error": "Question or media input is required"}), 400

    try:
        # Initialize client and config
        client = genai_service.initialize_client()
        generate_content_config = genai_service.create_generation_config()

        # Process media and create parts
        parts = []
        
        # Add images if provided
        for img_data in images:
            try:
                parts.append(media_service.process_image(img_data))
            except ValueError as e:
                return jsonify({"status": "error", "error": str(e)}), 400
        
        # Add documents if provided
        for doc_data in documents:
            try:
                parts.append(media_service.process_document(doc_data))
            except ValueError as e:
                return jsonify({"status": "error", "error": str(e)}), 400
        
        # Add text question if provided
        if question:
            parts.append(types.Part.from_text(text=question))
        
        # Create content for this user input
        user_content = types.Content(role="user", parts=parts)

        # Build the full conversation history (last 10 exchanges to avoid overflow)
        contents = chat_history[-10:]  # Include only recent history for context
        contents.append(user_content)  # Add current user input

        # Get response from model
        response = client.models.generate_content(
            model="gemini-1.5-pro-002",
            contents=contents,
            config=generate_content_config,
        )

        cleaned_text = genai_service.clean_response(response)

                # Add this code to save to Firebase
        # For now, use a fixed chat title and get user_id from request
        chat_title = "Legal Consultation"
        user_id = request.json.get("user_id", "anonymous")  # Get user_id from request or use "anonymous"
        
        # Save the conversation to Firestore
        save_chat_to_firestore(
            user_id=user_id,
            chat_title=chat_title,
            user_message=question,  # The original question text
            ai_response=cleaned_text  # The AI's response
        )

        # Update chat history with user input and AI response
        chat_history.append(user_content)  # Store user message
        chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=cleaned_text)]))  # Store AI response
        
        return jsonify({
            "status": "success",
            "response": cleaned_text,
            # You can add this to indicate the chat was saved
            "chat_saved": True,
            "chat_title": chat_title
        })

    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500


def save_chat_to_firestore(user_id, chat_title, user_message, ai_response, chat_id=None):
  """
  Save a chat message to Firestore with proper document IDs.
  
  Args:
      user_id (str): User identifier
      chat_title (str): Human-readable title for the chat
      user_message (str): Message from the user
      ai_response (str): Response from the AI
      chat_id (str, optional): Existing chat ID for continuing conversations
      
  Returns:
      dict: Contains chat_id, title and success status
  """
  db = firestore.client()
  current_timestamp = datetime.now()
  
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
  
  # Case 1: Continuing an existing chat
  if chat_id:
      chat_ref = db.collection('user_data').document(user_id) \
                    .collection('user_chats').document(chat_id)
      
      chat_doc = chat_ref.get()
      if chat_doc.exists:
          # Update existing chat
          chat_ref.update({
              'messages': firestore.ArrayUnion([user_message_data, ai_message_data]),
              'last_updated': current_timestamp
          })
          return {
              'success': True,
              'chat_id': chat_id,
              'title': chat_doc.get('title')
          }
      else:
          # Chat ID provided but doesn't exist - create a new one instead
          chat_id = None
  
  # Case 2: Creating a new chat
  if not chat_id:
      # Generate a title if none provided
      if not chat_title:
          # Use first few words of user message as title
          words = user_message.split()[:5]
          chat_title = " ".join(words) + "..." if len(words) >= 5 else user_message
      
      # Create a new document with auto-generated ID
      chat_ref = db.collection('user_data').document(user_id) \
                    .collection('user_chats').document()
      
      # Set the data with title preserved
      chat_ref.set({
          'title': chat_title,  # Store the user-friendly title
          'createdAt': current_timestamp,
          'last_updated': current_timestamp,
          'messages': [user_message_data, ai_message_data]
      })
      
      return {
          'success': True,
          'chat_id': chat_ref.id,
          'title': chat_title,
          'is_new': True
      }
