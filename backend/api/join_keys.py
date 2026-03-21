"""Join keys API routes."""

from flask import jsonify
from . import join_keys_bp
from utils.json_utils import load_json_file
from config import Config

@join_keys_bp.route('', methods=['GET'])
def get_join_keys():
    """Get join keys."""
    try:
        data = load_json_file(Config.JOIN_KEYS_FILE, {"keys": []})
        return jsonify({
            "ok": True,
            "keys": data.get("keys", [])
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
