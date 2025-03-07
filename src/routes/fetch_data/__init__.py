# routes/legal_assistant/__init__.py
from flask import Blueprint

fetch_bp = Blueprint('fetch', __name__)

# Import routes to register them with the blueprint
from src.routes.fetch_data import fetch_history, fetch_titles
