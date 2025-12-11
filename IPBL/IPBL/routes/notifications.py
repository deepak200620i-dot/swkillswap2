from flask import Blueprint, jsonify
from database import get_db
from utils import token_required

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('/check', methods=['GET'])
@token_required
def check_notifications(current_user):
    """Check for new messages and requests"""
    try:
        user_id = current_user['user_id']
        db = get_db()
        
        # 1. Count unread messages
        # Since messages table doesn't have receiver_id, we infer it from conversation
        # We want messages in conversations where I am a participant, but NOT the sender, and is_read=0
        unread_messages_count = db.execute('''
            SELECT COUNT(*) as count
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE (c.user1_id = ? OR c.user2_id = ?)
            AND m.sender_id != ?
            AND m.is_read = 0
        ''', (user_id, user_id, user_id)).fetchone()['count']
        
        # 2. Count pending requests
        pending_requests_count = db.execute('''
            SELECT COUNT(*) as count
            FROM swap_requests
            WHERE receiver_id = ? AND status = 'pending'
        ''', (user_id,)).fetchone()['count']
        
        # Optional: Get latest unread message for Toast content
        latest_message = None
        if unread_messages_count > 0:
            msg = db.execute('''
                SELECT m.content, u.full_name
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                JOIN users u ON m.sender_id = u.id
                WHERE (c.user1_id = ? OR c.user2_id = ?)
                AND m.sender_id != ?
                AND m.is_read = 0
                ORDER BY m.created_at DESC
                LIMIT 1
            ''', (user_id, user_id, user_id)).fetchone()
            
            if msg:
                # Decrypt message content (assuming encryption is utilized but not defined here clearly)
                # For now returning raw (or handle decryption if imports allow)
                # Need to import decrypt_message
                pass 
                
        return jsonify({
            'unread_messages': unread_messages_count,
            'pending_requests': pending_requests_count
        }), 200
        
    except Exception as e:
        print(f"Error checking notifications: {e}")
        return jsonify({'error': 'Failed to check notifications'}), 500
