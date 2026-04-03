"""State API routes."""

from flask import jsonify
from datetime import datetime
from . import state_bp
from database import load_agents_from_db

@state_bp.route('', methods=['GET'])
def get_current_state():
    """Get current office state."""
    try:
        agents = load_agents_from_db()
        
        # Find main agent or first agent
        main_agent = None
        for agent in agents:
            if agent.get("isMain"):
                main_agent = agent
                break
        
        if not main_agent and agents:
            main_agent = agents[0]
        
        state = {
            "state": main_agent["state"] if main_agent else "idle",
            "detail": main_agent["detail"] if main_agent else "等待任务中...",
            "progress": main_agent.get("task_progress", 0) if main_agent else 0,
            "updated_at": datetime.now().isoformat(),
        }
        
        return jsonify({
            "ok": True,
            "state": state
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
