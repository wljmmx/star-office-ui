"""Join keys API routes."""

from flask import Blueprint, jsonify
from utils.json_utils import load_json_file
from config import Config

join_keys_bp = Blueprint('join_keys', __name__, url_prefix='/api/join-keys')

@join_keys_bp.route('', methods=['GET'])
def get_join_keys():
    """Get join keys."""
    try:
        data = load_json_file(Config.JOIN_KEYS_FILE, {"keys": []})
        return jsonify({
            "ok": True,
            "msg": "获取成功",
            "data": {
                "keys": data.get("keys", [])
            }
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e),
            "data": None
        }), 500
