from flask import Blueprint, jsonify, request
from google.genai import types
from services import genai_service, media_service

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

        # Update chat history with user input and AI response
        chat_history.append(user_content)  # Store user message
        chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=cleaned_text)]))  # Store AI response
        
        return jsonify({
            "status": "success",
            "response": cleaned_text,
            "history_length": len(chat_history) // 2  # Number of exchanges (user + AI)
        })

    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500
