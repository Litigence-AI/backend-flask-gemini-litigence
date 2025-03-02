from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import base64
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

law_assistant_instruction = """You are Litigence AI 🤖⚖️ an Indian law legal AI Assistant

1. Provide concise answers to legal questions and elaborate only if user asks more questions
2. Only answer questions related to law and legal topics. Politely decline answering non-legal questions as its a violation to the service policy.
3. Use plain language and avoid legal jargon when possible. When legal terms are necessary, provide brief explanations.
4. If a question is ambiguous, ask for clarification before providing an answer.
5. If uncertain about a specific legal point, acknowledge limitations and suggest consulting a qualified attorney.
6. Provide citations to relevant statutes, case law, or regulations when discussing specific legal points.
7. Use plain text and avoid markdowns, HTML, or other formatting in responses.
8. Provide historical context for laws and legal concepts when it adds value to the explanation.
9. Avoid providing personal opinions or advice. Stick to the facts and the law.
"""

def clean_response(response):
    try:
        # Extract text from response
        if hasattr(response, 'candidates') and response.candidates:
            if hasattr(response.candidates[0].content, 'parts'):
                return response.candidates[0].content.parts[0].text
            elif hasattr(response.candidates[0].content, 'text'):
                return response.candidates[0].content.text
        return str(response)
    except Exception as e:
        return {"answer": str(response), "error": str(e)}

@app.route("/")
def health_check():
    return jsonify({"status": "healthy", "service": "legal-assistant-api"})

@app.route("/ask", methods=["POST"])
def ask_legal_question():
    project_id = os.environ.get('PROJECT_ID')
    location = os.environ.get('LOCATION')

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    # Extract question and optional media
    question = request.json.get("question")
    images = request.json.get("images", [])  # List of base64 encoded images
    documents = request.json.get("documents", [])  # List of base64 encoded PDFs
    
    if not question and not (images or documents):
        return jsonify({"error": "Question or media input is required"}), 400

    try:
        # Initialize genai client
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )

        # # Set up tools (Google Search)
        # tools = [
        #     types.Tool(google_search=types.GoogleSearch())
        # ]

        # Configure safety settings
        safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_ONLY_HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_ONLY_HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_ONLY_HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_ONLY_HIGH"
            )
        ]

        # Set generation config
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            max_output_tokens=8192,
            response_modalities=["TEXT"],
            safety_settings=safety_settings,
            # tools=tools,
            system_instruction=[types.Part.from_text(text=law_assistant_instruction)],
        )

        # Create parts for the content
        parts = []
        
        # Add images if provided
        for img_data in images:
            try:
                # Extract MIME type and base64 content
                if ";" in img_data and "," in img_data:
                    mime_type = img_data.split(";")[0].split(":")[1]
                    base64_content = img_data.split(",")[1]
                else:
                    # Assume JPEG if not specified
                    mime_type = "image/jpeg"
                    base64_content = img_data
                
                # Create image part
                image_part = types.Part.from_bytes(
                    data=base64.b64decode(base64_content),
                    mime_type=mime_type
                )
                parts.append(image_part)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": f"Error processing image: {str(e)}"
                }), 400
        
        # Add documents if provided
        for doc_data in documents:
            try:
                # Extract MIME type and base64 content
                if ";" in doc_data and "," in doc_data:
                    mime_type = doc_data.split(";")[0].split(":")[1]
                    base64_content = doc_data.split(",")[1]
                else:
                    # Assume PDF if not specified
                    mime_type = "application/pdf"
                    base64_content = doc_data
                
                # Create document part
                doc_part = types.Part.from_bytes(
                    data=base64.b64decode(base64_content),
                    mime_type=mime_type
                )
                parts.append(doc_part)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": f"Error processing document: {str(e)}"
                }), 400
        
        # Add text question if provided
        if question:
            parts.append(types.Part.from_text(text=question))
        
        # Create content with user's input
        contents = [
            types.Content(
                role="user",
                parts=parts
            )
        ]

        # Get response from model
        response = client.models.generate_content(
            model="gemini-1.5-pro-002",  # Using 1.5 Pro for multimodal capabilities
            contents=contents,
            config=generate_content_config,
        )

        cleaned_text = clean_response(response)
        
        return jsonify({
            "status": "success",
            "response": cleaned_text
        })

    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500

@app.route("/ask_stream", methods=["POST"])

def ask_legal_question_stream():
    """Streaming version of the ask endpoint that returns responses as they are generated"""
    project_id = os.environ.get('PROJECT_ID')
    location = os.environ.get('LOCATION')

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    # Extract question and optional media
    question = request.json.get("question")
    images = request.json.get("images", [])
    documents = request.json.get("documents", [])
    
    if not question and not (images or documents):
        return jsonify({"error": "Question or media input is required"}), 400

    try:
        # Initialize genai client
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )

        # Set up tools and configs as in the non-streaming version
        tools = [types.Tool(google_search=types.GoogleSearchRetrieval())]
        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH")
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            max_output_tokens=8192,
            response_modalities=["TEXT"],
            safety_settings=safety_settings,
            tools=tools,
            system_instruction=[types.Part.from_text(text=law_assistant_instruction)],
        )

        # Create parts for the content (same as non-streaming version)
        parts = []
        
        # Add images if provided
        for img_data in images:
            try:
                if ";" in img_data and "," in img_data:
                    mime_type = img_data.split(";")[0].split(":")[1]
                    base64_content = img_data.split(",")[1]
                else:
                    mime_type = "image/jpeg"
                    base64_content = img_data
                
                image_part = types.Part.from_bytes(
                    data=base64.b64decode(base64_content),
                    mime_type=mime_type
                )
                parts.append(image_part)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": f"Error processing image: {str(e)}"
                }), 400
        
        # Add documents if provided
        for doc_data in documents:
            try:
                if ";" in doc_data and "," in doc_data:
                    mime_type = doc_data.split(";")[0].split(":")[1]
                    base64_content = doc_data.split(",")[1]
                else:
                    mime_type = "application/pdf"
                    base64_content = doc_data
                
                doc_part = types.Part.from_bytes(
                    data=base64.b64decode(base64_content),
                    mime_type=mime_type
                )
                parts.append(doc_part)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": f"Error processing document: {str(e)}"
                }), 400
        
        # Add text question if provided
        if question:
            parts.append(types.Part.from_text(text=question))
        
        # Create content with user's input
        contents = [
            types.Content(
                role="user",
                parts=parts
            )
        ]

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
        return app.response_class(
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

if __name__ == "__main__":
    app.run(
        debug=(os.environ.get("FLASK_ENV", "development") != "production"),
        host="0.0.0.0",
        port=8080
    )
