from flask import Blueprint, jsonify, request
from firebase_admin import firestore
import traceback
from datetime import datetime

# Import the blueprint from wherever you've defined it
from . import fetch_bp  # Adjust this path as needed

@fetch_bp.route("/chat_history", methods=["GET"])
def get_chat_history():
    """Retrieve chat history for a user"""
    user_id = request.args.get("user_id")
    chat_title = request.args.get("chat_title")
    
    if not user_id:
        return jsonify({"status": "error", "error": "user_id is required"}), 400
    
    try:
        db = firestore.client()
        
        if chat_title:
            # Get a specific chat
            chat_ref = db.collection('users').document(user_id) \
                         .collection('chats').document(chat_title)
            chat_doc = chat_ref.get()
            
            if not chat_doc.exists:
                return jsonify({"status": "error", "error": "Chat not found"}), 404
                
            return jsonify({
                "status": "success",
                "chat": chat_doc.to_dict()
            })
        else:
            # Get all chats for the user
            chats_ref = db.collection('users').document(user_id) \
                          .collection('chats')
            chats = chats_ref.get()
            
            chat_list = []
            for chat in chats:
                chat_data = chat.to_dict()
                chat_data['id'] = chat.id  # Add the document ID
                chat_list.append(chat_data)
                
            return jsonify({
                "status": "success",
                "chats": chat_list
            })
            
    except Exception as e:
        return jsonify({
            "status": "error in fetch_history",
            "error": str(e)
        }), 500

