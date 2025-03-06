from google import genai
from google.genai import types
import config
from utils.response_utils import clean_response

def initialize_client():
    """Initialize and return the Google GenAI client"""
    return genai.Client(
        vertexai=True,
        project=config.PROJECT_ID,
        location=config.LOCATION,
    )

def create_generation_config():
    """Create and return the generation configuration"""
    safety_settings = [
        types.SafetySetting(
            category=setting["category"],
            threshold=setting["threshold"]
        ) for setting in config.SAFETY_SETTINGS
    ]
    
    return types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=safety_settings,
        system_instruction=[types.Part.from_text(text=config.LAW_ASSISTANT_INSTRUCTION)],
    )