import base64
from google.genai import types

def process_image(img_data):
    """Process base64 encoded image data"""
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
        return types.Part.from_bytes(
            data=base64.b64decode(base64_content),
            mime_type=mime_type
        )
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

def process_document(doc_data):
    """Process base64 encoded document data (PDF or DOCX)"""
    try:
        # Extract MIME type and base64 content
        if ";" in doc_data and "," in doc_data:
            mime_type = doc_data.split(";")[0].split(":")[1]
            base64_content = doc_data.split(",")[1]
        else:
            # Check file signature or assume file type
            if doc_data.startswith("UEsDB"):  # DOCX file signature check
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                mime_type = "application/pdf"
            base64_content = doc_data
        
        # Create document part
        return types.Part.from_bytes(
            data=base64.b64decode(base64_content),
            mime_type=mime_type
        )
    except Exception as e:
        raise ValueError(f"Error processing document: {str(e)}")
