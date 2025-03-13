from flask import Blueprint, jsonify, request
from src.services.genai_services import generate_legal_response
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
        
        try:
            # Use the service to generate a response
            response_text = generate_legal_response(question)
        except Exception as e:
            return jsonify({"error": f"Error generating response: {str(e)}"}), 500
        
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
