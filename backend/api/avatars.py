"""Avatars API routes."""

from flask import Blueprint, jsonify, request
from utils.avatar_manager import AvatarManager, AvatarConfig, create_avatar_from_agent_type

avatars_bp = Blueprint('avatars', __name__, url_prefix='/api/avatars')

@avatars_bp.route('', methods=['GET'])
def get_all_avatar_types():
    """Get all available avatar types."""
    return jsonify({
        "ok": True,
        "avatar_types": [
            {"id": "pixel", "name": "像素风格", "description": "简单像素化角色"},
            {"id": "emoji", "name": "表情符号", "description": "使用 emoji 作为头像"},
            {"id": "image", "name": "图片", "description": "自定义图片头像"},
            {"id": "3d", "name": "3D 模型", "description": "3D 角色模型"},
        ],
        "default_avatars": AvatarManager.DEFAULT_AVATARS,
    })

@avatars_bp.route('/<agent_id>', methods=['GET'])
def get_agent_avatar(agent_id):
    """Get avatar for a specific agent."""
    try:
        from services.database_service import get_db_service
        
        db = get_db_service()
        agent = db.get_agent_by_id(agent_id)
        
        if not agent:
            return jsonify({
                "ok": False,
                "msg": "Agent not found"
            }), 404
        
        avatar_config = AvatarConfig(
            avatar_type=agent.avatar_type,
            avatar_data=agent.avatar_data,
            pixel_character=agent.pixel_character,
            avatar_url=agent.avatar_url,
        )
        
        return jsonify({
            "ok": True,
            "agent_id": agent_id,
            "avatar": avatar_config.to_dict(),
            "display": avatar_config.get_display_data(),
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@avatars_bp.route('/<agent_id>', methods=['POST', 'PUT'])
def update_agent_avatar(agent_id):
    """Update avatar for a specific agent."""
    try:
        data = request.get_json() or {}
        
        if not data:
            return jsonify({
                "ok": False,
                "msg": "No data provided"
            }), 400
        
        # Validate avatar data
        avatar_type = data.get('avatar_type', 'pixel')
        avatar_data = data.get('avatar_data', '')
        
        if not AvatarManager.validate_avatar_data(avatar_type, avatar_data):
            return jsonify({
                "ok": False,
                "msg": "Invalid avatar data format"
            }), 400
        
        # Update database
        import sqlite3
        from config import Config
        
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE agents
            SET avatar_type = ?, avatar_data = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (avatar_type, avatar_data, agent_id))
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        
        if updated:
            return jsonify({
                "ok": True,
                "msg": "Avatar updated successfully",
                "avatar_type": avatar_type,
            })
        
        return jsonify({
            "ok": False,
            "msg": "Agent not found or update failed"
        }), 404
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@avatars_bp.route('/generate/<agent_id>', methods=['POST'])
def generate_avatar(agent_id):
    """Generate a default avatar for an agent."""
    try:
        from services.database_service import get_db_service
        
        db = get_db_service()
        agent = db.get_agent_by_id(agent_id)
        
        if not agent:
            return jsonify({
                "ok": False,
                "msg": "Agent not found"
            }), 404
        
        # Generate avatar based on agent type
        avatar = create_avatar_from_agent_type(agent.agent_type, agent.name)
        
        # Update database
        import sqlite3
        from config import Config
        
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE agents
            SET avatar_type = ?, avatar_data = ?, pixel_character = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (avatar.avatar_type, avatar.avatar_data, avatar.pixel_character, agent_id))
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        
        if updated:
            return jsonify({
                "ok": True,
                "msg": "Avatar generated successfully",
                "avatar": avatar.to_dict(),
            })
        
        return jsonify({
            "ok": False,
            "msg": "Failed to generate avatar"
        }), 500
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
