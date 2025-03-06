def clean_response(response):
    """Extract and clean text from the model response"""
    try:
        if hasattr(response, 'candidates') and response.candidates:
            if hasattr(response.candidates[0].content, 'parts'):
                return response.candidates[0].content.parts[0].text
            elif hasattr(response.candidates[0].content, 'text'):
                return response.candidates[0].content.text
        return str(response)
    except Exception as e:
        return {"answer": str(response), "error": str(e)}
