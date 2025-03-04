from flask import Blueprint, jsonify, request
from google.genai import types
from services import genai_service, media_service
from firebase_admin import firestore

from services.firebase_services import save_chat_to_firestore

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


@legal_bp.route("/chat_history", methods=["GET"])
def get_chat_history():
    """Retrieve chat history for a user"""
    user_id = request.args.get("user_id")
    chat_title = request.args.get("chat_title")
    
    if not user_id:
        return jsonify({"status": "error", "error": "user_id is required"}), 400
    
    try:
        db = firestore.client()
        
        if chat_title:
            # Get a specific chat
            chat_ref = db.collection('user_data').document(user_id) \
                         .collection('user_chats').document(chat_title)
            chat_doc = chat_ref.get()
            
            if not chat_doc.exists:
                return jsonify({"status": "error", "error": "Chat not found"}), 404
                
            return jsonify({
                "status": "success",
                "chat": chat_doc.to_dict()
            })
        else:
            # Get all chats for the user
            chats_ref = db.collection('user_data').document(user_id) \
                          .collection('user_chats')
            chats = chats_ref.get()
            
            chat_list = []
            for chat in chats:
                chat_data = chat.to_dict()
                chat_data['id'] = chat.id  # Add the document ID
                chat_list.append(chat_data)
                
            return jsonify({
                "status": "success",
                "chats": chat_list
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
