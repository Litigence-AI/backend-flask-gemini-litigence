def clean_response(response):
    """Extract and clean text from the model response"""
    try:
        # Handle normal Gemini responses
        if hasattr(response, 'candidates') and response.candidates:
            if hasattr(response.candidates[0].content, 'parts'):
                return response.candidates[0].content.parts[0].text
            elif hasattr(response.candidates[0].content, 'text'):
                return response.candidates[0].content.text
        # Handle our mock response
        elif hasattr(response, 'parts') and response.parts:
            return response.parts[0].text if hasattr(response.parts[0], 'text') else str(response.parts[0])
        # Handle simple string or other object types
        return str(response)
    except Exception as e:
        print(f"Error cleaning response: {e}")
        return {"answer": str(response), "error": str(e)}
