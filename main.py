from flask import Flask
from flask_cors import CORS
import config
from routes.health import health_bp
from routes.legal_assistant import legal_bp
from routes.fetch_data import fetch_bp
from services.firebase_services import initialize_firebase

def create_app():
    app = Flask(__name__)

    # Initialize Firebase
    initialize_firebase()
    
    # Configure CORS
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
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(fetch_bp, url_prefix='')
    
    return app

app = create_app()
if __name__ == "__main__":
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
