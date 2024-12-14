from flask import Flask, jsonify, request
import vertexai
from vertexai.preview.generative_models import GenerativeModel, SafetySetting, Tool
from vertexai.preview.generative_models import grounding
import os

app = Flask(__name__)

textsi_1 = """You are LexMachina 🤖⚖ an Indian law legal AI Assistant..."""  # Your original system prompt

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

@app.route("/")
def health_check():
    return jsonify({"status": "healthy", "service": "legal-assistant-api"})

@app.route("/ask", methods=["POST"])
def ask_legal_question():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        vertexai.init(project="law-ai-437009", location="asia-south1")
        tools = [
            Tool.from_google_search_retrieval(
                google_search_retrieval=grounding.GoogleSearchRetrieval()
            ),
        ]
        model = GenerativeModel(
            "gemini-1.5-flash-002",
            tools=tools,
            system_instruction=[textsi_1]
        )
        chat = model.start_chat()
        response = chat.send_message(
            [question],
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        return jsonify({"response": str(response)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(
        debug=True, 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8080))
    )

"""

flask app hot demo
https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service

gcloud cli install
https://cloud.google.com/sdk/docs/install

1.run local app
  python main.py

2.auth gcloud
  gcloud auth application-default login

3.give permission to service account

./google-cloud-sdk/bin/gcloud projects add-iam-policy-binding law-ai-437009 \
    --member=serviceAccount:916007394186-compute@developer.gserviceaccount.com \
    --role=roles/cloudbuild.builds.builder

4.test api
curl -X POST http://localhost:8080/ask   -H "Content-Type: application/json"   -d '{"question":"What are the rights I have as a citizen of India?"}'

5.deploy to cloud run
./google-cloud-sdk/bin/gcloud run deploy --source .





"""