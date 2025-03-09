from flask import jsonify, request
from firebase_admin import firestore

# Import the blueprint from wherever you've defined it
from . import fetch_bp  # Adjust this path as needed

@fetch_bp.route("/chat_titles", methods=["GET"])
def get_chat_titles():
    """Retrieve just the chat titles for a user"""
    user_id = request.args.get("user_id")
    
    if not user_id:
        return jsonify({"status": "error", "error": "user_id is required"}), 400
    
    try:
        db = firestore.client()
        
        # Query all chats for the user but only get minimal data
        chats_ref = db.collection('user_data').document(user_id) \
                      .collection('user_chats')
        
        # Get only the title and last_updated fields for efficiency
        chats = chats_ref.get()
        
        chat_titles = []
        for chat in chats:
            chat_data = chat.to_dict()
            # Only include the necessary fields for the drawer
            chat_titles.append({
                'id': chat.id,
                'title': chat_data.get('title', 'Untitled Chat'),
                'last_updated': chat_data.get('last_updated', None)
            })
                
        # Sort by last_updated (newest first)
        chat_titles.sort(key=lambda x: x.get('last_updated', 0), reverse=True)
            
        return jsonify({
            "status": "success",
            "chat_titles": chat_titles
        })
            
    except Exception as e:
        return jsonify({
            "status": "error in response util",
            "error": str(e)
        }), 500
