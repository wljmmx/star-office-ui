#!/usr/bin/env python3
"""
⚠️ DEPRECATED - 废弃警告

此文件已被 main.py 取代，不再推荐使用。

原因:
- main.py 使用工厂模式 (create_app())，更符合 Flask 最佳实践
- 模块化架构，易于维护和扩展
- 支持依赖注入和测试
- 新增 avatars 和 environments API

迁移指南:
1. 使用 main.py 作为应用入口
2. 更新启动脚本调用 python3 main.py
3. 配置从 config.py 管理
4. API 路由从 api/ 蓝图导入

保留此文件仅用于向后兼容和参考。
"""

# Legacy implementation - replaced by main.py
"""Star Office UI - Backend State Service (Modified for github-collab integration)"""

from flask import Flask, jsonify, send_from_directory, make_response, request, session
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import json
import os
import threading
from pathlib import Path

# Import database layer
from database import (
    load_agents_from_db,
    load_tasks_from_db,
    get_agent_by_id,
    update_agent_status,
    normalize_agent_state,
    state_to_area,
)

# Import API blueprints
from api.agents import agents_bp
from api.tasks import tasks_bp
from api.state import state_bp
from api.assets import assets_bp
from api.config import config_bp
from api.join_keys import join_keys_bp
from services.database_service import (
    load_agents_from_db,
    load_tasks_from_db,
    normalize_agent_state as _normalize_agent_state_legacy,
    _state_to_area_legacy,
)

# Alias for compatibility
normalize_agent_state = _normalize_agent_state_legacy
state_to_area = _state_to_area_legacy
get_agent_by_id = None  # Not used in legacy code
update_agent_status = None  # Not used in legacy code

# Keep original store_utils for compatibility
from store_utils import (
    load_asset_positions as _store_load_asset_positions,
    save_asset_positions as _store_save_asset_positions,
    load_asset_defaults as _store_load_asset_defaults,
    save_asset_defaults as _store_save_asset_defaults,
    load_runtime_config as _store_load_runtime_config,
    save_runtime_config as _store_save_runtime_config,
    load_join_keys as _store_load_join_keys,
    save_join_keys as _store_save_join_keys,
)

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
FRONTEND_INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")
ASSET_POSITIONS_FILE = os.path.join(ROOT_DIR, "asset-positions.json")
ASSET_DEFAULTS_FILE = os.path.join(ROOT_DIR, "asset-defaults.json")
RUNTIME_CONFIG_FILE = os.path.join(ROOT_DIR, "runtime-config.json")
JOIN_KEYS_FILE = os.path.join(ROOT_DIR, "join-keys.json")

# State mapping
VALID_AGENT_STATES = frozenset({"idle", "writing", "researching", "executing", "syncing", "error"})
STATE_TO_AREA_MAP = {
    "idle": "breakroom",
    "writing": "writing",
    "researching": "writing",
    "executing": "writing",
    "syncing": "writing",
    "error": "error",
}

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/static")
app.secret_key = os.getenv("FLASK_SECRET_KEY") or "star-office-secret-key"

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Session config
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)

# Version timestamp for cache busting
VERSION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def load_agents_state():
    """Load agents from github-collab database."""
    return load_agents_from_db()


def save_agents_state(agents):
    """No-op: agents are managed by github-collab."""
    pass


def load_asset_positions():
    return _store_load_asset_positions(ASSET_POSITIONS_FILE)


def save_asset_positions(data):
    _store_save_asset_positions(ASSET_POSITIONS_FILE, data)


def load_asset_defaults():
    return _store_load_asset_defaults(ASSET_DEFAULTS_FILE)


def save_asset_defaults(data):
    _store_save_asset_defaults(ASSET_DEFAULTS_FILE, data)


def load_runtime_config():
    return _store_load_runtime_config(RUNTIME_CONFIG_FILE)


def save_runtime_config(data):
    _store_save_runtime_config(RUNTIME_CONFIG_FILE, data)


def load_join_keys():
    return _store_load_join_keys(JOIN_KEYS_FILE)


def save_join_keys(data):
    _store_save_join_keys(JOIN_KEYS_FILE, data)


# Register blueprints
app.register_blueprint(agents_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(state_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(config_bp)
app.register_blueprint(join_keys_bp)


@app.route("/", methods=["GET"])
def index():
    """Serve the main page."""
    with open(FRONTEND_INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("{{VERSION_TIMESTAMP}}", VERSION_TIMESTAMP)
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.route("/api/state", methods=["GET"])
def get_state():
    """Get current office state."""
    agents = load_agents_state()
    main_agent = next((a for a in agents if a.get("isMain")), agents[0] if agents else None)
    
    state = {
        "state": main_agent["state"] if main_agent else "idle",
        "detail": main_agent["detail"] if main_agent else "等待任务中...",
        "progress": main_agent.get("task_progress", 0),
        "updated_at": datetime.now().isoformat(),
    }
    
    return jsonify({"ok": True, "state": state})


@app.route("/api/agents", methods=["GET"])
def get_agents():
    """Get all agents."""
    agents = load_agents_state()
    return jsonify({"ok": True, "agents": agents})


@app.route("/api/agents/<agent_id>", methods=["GET"])
def get_agent(agent_id):
    """Get a specific agent."""
    agent = get_agent_by_id(agent_id)
    if agent:
        return jsonify({"ok": True, "agent": agent})
    return jsonify({"ok": False, "msg": "Agent not found"}), 404


@app.route("/api/agents/<agent_id>/status", methods=["POST"])
def set_agent_status(agent_id):
    """Update agent status."""
    data = request.get_json() or {}
    new_status = data.get("state", "")
    
    if not new_status:
        return jsonify({"ok": False, "msg": "Missing state"}), 400
    
    # Normalize state
    normalized_state = normalize_agent_state(new_status)
    
    # Update database
    success = update_agent_status(agent_id, normalized_state)
    
    if success:
        # Broadcast update to all connected clients
        agents = load_agents_state()
        socketio.emit("agents_update", {"agents": agents})
        return jsonify({"ok": True, "state": normalized_state})
    
    return jsonify({"ok": False, "msg": "Failed to update"}), 500


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Get all tasks."""
    tasks = load_tasks_from_db()
    return jsonify({"ok": True, "tasks": tasks})


@app.route("/api/join-keys", methods=["GET"])
def get_join_keys():
    """Get join keys."""
    keys = load_join_keys()
    return jsonify({"ok": True, "keys": keys.get("keys", [])})


@app.route("/api/assets/positions", methods=["GET"])
def get_asset_positions():
    """Get asset positions."""
    positions = load_asset_positions()
    return jsonify({"ok": True, "positions": positions})


@app.route("/api/assets/positions", methods=["POST"])
def update_asset_positions():
    """Update asset positions."""
    data = request.get_json() or {}
    save_asset_positions(data)
    return jsonify({"ok": True})


@app.route("/api/assets/defaults", methods=["GET"])
def get_asset_defaults():
    """Get asset defaults."""
    defaults = load_asset_defaults()
    return jsonify({"ok": True, "defaults": defaults})


@app.route("/api/assets/defaults", methods=["POST"])
def update_asset_defaults():
    """Update asset defaults."""
    data = request.get_json() or {}
    save_asset_defaults(data)
    return jsonify({"ok": True})


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get runtime config."""
    config = load_runtime_config()
    # Mask sensitive data
    if "gemini_api_key" in config:
        config["gemini_api_key"] = "***masked***"
    return jsonify({"ok": True, "config": config})


@app.route("/api/config", methods=["POST"])
def update_config():
    """Update runtime config."""
    data = request.get_json() or {}
    save_runtime_config(data)
    return jsonify({"ok": True})


# SocketIO events
@socketio.on("connect")
def handle_connect():
    """Client connected, send current state."""
    print(f"[SocketIO] Client connected: {request.sid}")
    agents = load_agents_state()
    emit("agents_update", {"agents": agents})


@socketio.on("disconnect")
def handle_disconnect():
    """Client disconnected."""
    print(f"[SocketIO] Client disconnected: {request.sid}")


@socketio.on("subscribe_agents")
def handle_subscribe():
    """Client wants to subscribe to agent updates."""
    agents = load_agents_state()
    emit("agents_update", {"agents": agents})


# Background sync loop
def sync_loop():
    """Periodically check for changes and broadcast."""
    last_agents = None
    
    while True:
        try:
            time.sleep(5)  # Check every 5 seconds
            agents = load_agents_state()
            
            # Simple change detection
            current_hash = json.dumps(agents, sort_keys=True)
            if last_agents != current_hash:
                socketio.emit("agents_update", {"agents": agents})
                last_agents = current_hash
                print(f"[Sync] Broadcasted {len(agents)} agents")
        
        except Exception as e:
            print(f"[Sync] Error: {e}")


if __name__ == "__main__":
    import time
    
    # Start background sync thread
    sync_thread = threading.Thread(target=sync_loop, daemon=True)
    sync_thread.start()
    
    print(f"Star Office UI Server starting...")
    print(f"Frontend: {FRONTEND_INDEX_FILE}")
    print(f"Database: {os.path.join(ROOT_DIR, '..', 'skills', 'github-collab', 'github-collab.db')}")
    
    # Run server
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
