"""Assets API routes with input validation."""

from flask import jsonify, request
from . import assets_bp
from utils.json_utils import load_json_file, save_json_file
from config import Config
from validators import AssetPositionsRequest, AssetDefaultsRequest

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
    """Update asset positions with validated input."""
    try:
        # Validate request body
        try:
            data = request.get_json() or {}
            AssetPositionsRequest(positions=data)
        except Exception as e:
            return jsonify({
                "ok": False,
                "msg": f"Invalid positions: {str(e)}"
            }), 400
        
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
    """Update asset defaults with validated input."""
    try:
        # Validate request body
        try:
            data = request.get_json() or {}
            AssetDefaultsRequest(defaults=data)
        except Exception as e:
            return jsonify({
                "ok": False,
                "msg": f"Invalid defaults: {str(e)}"
            }), 400
        
        save_json_file(Config.ASSET_DEFAULTS_FILE, data)
        return jsonify({
            "ok": True
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
