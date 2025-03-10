from flask import Blueprint, jsonify, request
from google.genai import types
# from src.services import genai_service, media_service
from config import MODEL_NAME,PROJECT_ID,LOCATION,LAW_ASSISTANT_INSTRUCTION
from google import genai
from google.genai import types
# import base64


from src.services.firebase_services import save_chat_to_firestore

legal_bp = Blueprint('legal', __name__)

# Global chat history to store user and AI exchanges
chat_history = []

@legal_bp.route("/ask", methods=["POST"])
def ask_legal_question():
    
    try:
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        model = MODEL_NAME
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="""put the question here ?""")
                ]
            ),
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text="""I'm ready! Please provide the question you would like me to answer.""")
                ]
            ),
            types.Content(
            role="user",
            parts=[
            types.Part.from_text(text="""put the next question here ?""")
            ]
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature = 1,
            top_p = 0.95,
            max_output_tokens = 8192,
            response_modalities = ["TEXT"],
            system_instruction=[types.Part.from_text(text="""put system instruction here""")],
        )

        for chunk in client.models.generate_content_stream(
            model = model,
            contents = contents,
            config = generate_content_config,
            ):
            print(chunk.text, end="")

        return jsonify({
            "message": "I'm ready! Please provide the question you would like me to answer."
        }) 

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
