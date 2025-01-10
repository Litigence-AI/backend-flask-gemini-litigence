from flask import Flask, jsonify, request
from flask_cors import CORS  # Add this import

import vertexai
from vertexai.preview.generative_models import GenerativeModel, SafetySetting, Part, Tool
from vertexai.preview.generative_models import grounding
import os
import json


app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})

# @app.before_request
# def check_env_variables():
#   if not PROJECT_ID or not LOCATION:
#       return jsonify({
#           "status": "error",
#           "error": "Missing PROJECT_ID or LOCATION environment variable."
#       }), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

law_assistant_instruction = """You are LexMachina 🤖⚖ an Indian law legal AI Assistant..."""  # Your original system prompt

# Update generation config to enforce JSON
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,  
}

safety_settings = [
    SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
    SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
    SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
    SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
]

def clean_response(response):
    try:
        # Convert protobuf to dict and extract text
        response_text = response.candidates[0].content.parts[0].text
        
        return response_text
        
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
  
  question = request.json.get("question")
  if not question:
      return jsonify({"error": "Question is required"}), 400

  try:
      vertexai.init(project=project_id, location=location)
      tools = [
          Tool.from_google_search_retrieval(
              google_search_retrieval=grounding.GoogleSearchRetrieval()
          ),
      ]
      model = GenerativeModel(
          "gemini-1.5-flash-002",
          tools=tools,
          system_instruction=[law_assistant_instruction],
          generation_config=generation_config,
          safety_settings=safety_settings
      )
      chat = model.start_chat()
      response = chat.send_message([question])
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

if __name__ == "__main__":
    app.run(
        debug=(os.environ.get("FLASK_ENV", "development") != "production"),
        host="0.0.0.0",
        port=8080
    )

