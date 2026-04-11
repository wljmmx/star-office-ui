"""Avatars API routes."""

from flask import Blueprint, jsonify, request
from utils.avatar_manager import AvatarManager, AvatarConfig, create_avatar_from_agent_type

avatars_bp = Blueprint('avatars', __name__, url_prefix='/api/avatars')

@avatars_bp.route('', methods=['GET'])
def get_all_avatar_types():
    """Get all available avatar types."""
    return jsonify({
        "ok": True,
        "data": {
            "avatar_types": [
                {"id": "pixel", "name": "像素风格", "description": "简单像素化角色"},
                {"id": "emoji", "name": "表情符号", "description": "使用 emoji 作为头像"},
                {"id": "image", "name": "图片", "description": "自定义图片头像"},
                {"id": "3d", "name": "3D 模型", "description": "3D 角色模型"},
            ],
            "default_avatars": AvatarManager.DEFAULT_AVATARS,
        }
    }), 200

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
                "msg": "Agent not found",
                "data": None
            }), 404
        
        avatar_config = AvatarConfig(
            avatar_type=agent.avatar_type,
            avatar_data=agent.avatar_data,
            pixel_character=agent.pixel_character,
            avatar_url=agent.avatar_url,
        )
        
        return jsonify({
            "ok": True,
            "data": {
                "agent_id": agent_id,
                "avatar": avatar_config.to_dict(),
                "display": avatar_config.get_display_data(),
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e),
            "data": None
        }), 500

@avatars_bp.route('/<agent_id>', methods=['POST', 'PUT'])
def update_agent_avatar(agent_id):
    """Update avatar for a specific agent."""
    try:
        data = request.get_json() or {}
        
        if not data:
            return jsonify({
                "ok": False,
                "msg": "No data provided",
                "data": None
            }), 400
        
        # Validate avatar data
        avatar_type = data.get('avatar_type', 'pixel')
        avatar_data = data.get('avatar_data', '')
        
        if not AvatarManager.validate_avatar_data(avatar_type, avatar_data):
            return jsonify({
                "ok": False,
                "msg": "Invalid avatar data format",
                "data": None
            }), 400
        
        # Update database using DatabaseService
        from services.database_service import get_db_service
        
        db = get_db_service()
        updated = db.update_agent_avatar(agent_id, avatar_type, avatar_data)
        
        if updated:
            return jsonify({
                "ok": True,
                "msg": "Avatar updated successfully",
                "data": {
                    "agent_id": agent_id,
                    "avatar_type": avatar_type,
                }
            }), 200
        
        return jsonify({
            "ok": False,
            "msg": "Agent not found or update failed",
            "data": None
        }), 404
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e),
            "data": None
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
                "msg": "Agent not found",
                "data": None
            }), 404
        
        # Generate avatar based on agent type
        avatar = create_avatar_from_agent_type(agent.agent_type, agent.name)
        
        # Update database using DatabaseService
        from services.database_service import get_db_service
        
        db = get_db_service()
        updated = db.update_agent_avatar(
            agent_id, 
            avatar.avatar_type, 
            avatar.avatar_data,
            pixel_character=avatar.pixel_character
        )
        
        if updated:
            return jsonify({
                "ok": True,
                "msg": "Avatar generated successfully",
                "data": {
                    "agent_id": agent_id,
                    "avatar": avatar.to_dict(),
                }
            }), 200
        
        return jsonify({
            "ok": False,
            "msg": "Failed to generate avatar",
            "data": None
        }), 404
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e),
            "data": None
        }), 500
