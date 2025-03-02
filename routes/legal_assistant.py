from flask import Blueprint, jsonify, request
from google.genai import types
import json
from services import genai_service, media_service

legal_bp = Blueprint('legal', __name__)

@legal_bp.route("/ask", methods=["POST"])
def ask_legal_question():
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
        
        # Create content with user's input
        contents = [types.Content(role="user", parts=parts)]

        # Get response from model
        response = client.models.generate_content(
            model="gemini-1.5-pro-002",
            contents=contents,
            config=generate_content_config,
        )

        cleaned_text = genai_service.clean_response(response)
        
        return jsonify({
            "status": "success",
            "response": cleaned_text
        })

    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500

# Similar structure for the streaming endpoint
@legal_bp.route("/ask_stream", methods=["POST"])
@legal_bp.route("/ask_stream", methods=["POST"])
def ask_legal_question_stream():
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
        
        # Create content with user's input
        contents = [types.Content(role="user", parts=parts)]

        # Define a generator function for streaming response
        def generate():
            for chunk in client.models.generate_content_stream(
                model="gemini-1.5-pro-002",
                contents=contents,
                config=generate_content_config,
            ):
                if not chunk.candidates or not chunk.candidates[0].content.parts:
                    continue
                
                # Send each chunk as an SSE event
                yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
            
            # Send an end marker
            yield f"data: {json.dumps({'done': True})}\n\n"

        # Return the streaming response
        return current_app.response_class(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500
