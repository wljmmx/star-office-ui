"""Assets API routes."""

from flask import jsonify, request
from pathlib import Path
from . import assets_bp
from utils.json_utils import load_json_file, save_json_file
from config import Config

@assets_bp.route('/positions', methods=['GET'])
def get_asset_positions():
    """Get asset positions."""
    try:
        positions = load_json_file(Config.ASSET_POSITIONS_FILE, {})
        return jsonify({
            "ok": True,
            "positions": positions
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@assets_bp.route('/positions', methods=['POST'])
def update_asset_positions():
    """Update asset positions."""
    try:
        data = request.get_json() or {}
        save_json_file(Config.ASSET_POSITIONS_FILE, data)
        return jsonify({
            "ok": True
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@assets_bp.route('/defaults', methods=['GET'])
def get_asset_defaults():
    """Get asset defaults."""
    try:
        defaults = load_json_file(Config.ASSET_DEFAULTS_FILE, {})
        return jsonify({
            "ok": True,
            "defaults": defaults
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@assets_bp.route('/defaults', methods=['POST'])
def update_asset_defaults():
    """Update asset defaults."""
    try:
        data = request.get_json() or {}
        save_json_file(Config.ASSET_DEFAULTS_FILE, data)
        return jsonify({
            "ok": True
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
