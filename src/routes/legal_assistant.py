from flask import Blueprint, jsonify, request, Response, stream_with_context
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
        chat_title = "Static Chat Title 1"
        
        # Define the streaming response generator function
        def generate():
            # Store the complete response for saving to Firestore
            complete_response = ""
            
            try:
                # Use the streaming service to generate a response
                for chunk in generate_legal_response(question):
                    complete_response += chunk
                    yield chunk
                    
                # Save to Firebase after stream is complete
                if user_id != 'anonymous':
                    try:
                        save_chat_to_firestore(user_id, chat_title, question, complete_response)
                    except Exception as e:
                        print(f"Warning: Failed to save chat to Firestore: {str(e)}")
                        
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                yield error_msg
        
        # Return a streaming response
        return Response(stream_with_context(generate()), content_type='text/plain')

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# Non-streaming endpoint (commented out as streaming is now the standard)
"""
@legal_bp.route("/ask_non_stream", methods=["POST"])
def ask_legal_question_non_stream():
    try:
        # Get the question from the request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing required field: question"}), 400
            
        question = data.get('question')
        user_id = data.get('user_id', 'anonymous')
        chat_title = "Static Chat Title 1"
        
        try:
            # Use the service to generate a response
            response_text = generate_legal_response_non_stream(question)
        except Exception as e:
            return jsonify({"error": f"Error generating response: {str(e)}"}), 500
        
        # Save to Firebase if user_id is provided
        if user_id != 'anonymous':
            try:
                save_chat_to_firestore(user_id, chat_title, question, response_text)
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
"""