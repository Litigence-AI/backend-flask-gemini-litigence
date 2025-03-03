from flask import Blueprint, jsonify, request
from google.genai import types
import json
from services import genai_service, media_service
import os
import base64
from flask import current_app

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
