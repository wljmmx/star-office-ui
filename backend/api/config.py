"""Config API routes with input validation."""

from flask import jsonify, request
from . import config_bp
from utils.json_utils import load_json_file, save_json_file
from config import Config
from validators import ConfigUpdateRequest

@config_bp.route('', methods=['GET'])
def get_config():
    """Get runtime config."""
    try:
        config = load_json_file(Config.RUNTIME_CONFIG_FILE, {})
        
        # Mask sensitive data
        if "gemini_api_key" in config:
            config["gemini_api_key"] = "***masked***"
        
        return jsonify({
            "ok": True,
            "config": config
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500


@config_bp.route('', methods=['POST'])
def update_config():
    """Update runtime config with validated input."""
    try:
        data = request.get_json() or {}
        
        # Validate request body
        try:
            ConfigUpdateRequest(**data)
        except Exception as e:
            return jsonify({
                "ok": False,
                "msg": f"Invalid config: {str(e)}"
            }), 400
        
        save_json_file(Config.RUNTIME_CONFIG_FILE, data)
        return jsonify({
            "ok": True
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
