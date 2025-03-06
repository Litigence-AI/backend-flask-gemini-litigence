from flask import Blueprint, jsonify

# Create a blueprint for the health check
health_bp = Blueprint('health', __name__)

@health_bp.route("/")
def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return jsonify({
        "status": "healthy",
        "service": "legal-assistant-api"
    })
