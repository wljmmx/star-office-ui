"""State API routes."""

from flask import jsonify
from datetime import datetime
from . import state_bp
from services.database_service import get_db_service

@state_bp.route('', methods=['GET'])
def get_current_state():
    """Get current office state."""
    try:
        db = get_db_service()
        agents = db.load_all_agents()
        
        # Find main agent or first agent
        main_agent = None
        for agent in agents:
            if agent.role == "main":
                main_agent = agent
                break
        
        if not main_agent and agents:
            main_agent = agents[0]
        
        state = {
            "state": main_agent.state if main_agent else "idle",
            "detail": main_agent.detail if main_agent else "等待任务中...",
            "progress": main_agent.task_progress if main_agent else 0,
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
