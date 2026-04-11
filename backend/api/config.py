"""Config API routes."""

from flask import jsonify, request
from . import config_bp
from utils.json_utils import load_json_file, save_json_file
from config import Config

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
            "msg": "Config retrieved successfully",
            "data": config
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e),
            "data": None
        }), 500

@config_bp.route('', methods=['POST'])
def update_config():
    """Update runtime config."""
    try:
        data = request.get_json() or {}
        save_json_file(Config.RUNTIME_CONFIG_FILE, data)
        return jsonify({
            "ok": True,
            "msg": "Config updated successfully",
            "data": data
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e),
            "data": None
        }), 500
