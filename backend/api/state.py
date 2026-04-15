"""State API routes."""

<<<<<<< HEAD
from flask import jsonify
from datetime import datetime
from . import state_bp
from database import load_agents_from_db
=======
from flask import Blueprint, jsonify
from datetime import datetime
from services.database_service import get_db_service

state_bp = Blueprint('state', __name__, url_prefix='/api/state')
>>>>>>> origin/master

@state_bp.route('', methods=['GET'])
def get_current_state():
    """Get current office state."""
    try:
<<<<<<< HEAD
        agents = load_agents_from_db()
=======
        db = get_db_service()
        agents = db.load_all_agents()
>>>>>>> origin/master
        
        # Find main agent or first agent
        main_agent = None
        for agent in agents:
<<<<<<< HEAD
            if agent.get("isMain"):
=======
            if agent.role == "main":
>>>>>>> origin/master
                main_agent = agent
                break
        
        if not main_agent and agents:
            main_agent = agents[0]
        
        state = {
<<<<<<< HEAD
            "state": main_agent["state"] if main_agent else "idle",
            "detail": main_agent["detail"] if main_agent else "等待任务中...",
            "progress": main_agent.get("task_progress", 0) if main_agent else 0,
=======
            "state": main_agent.state if main_agent else "idle",
            "detail": main_agent.detail if main_agent else "等待任务中...",
            "progress": main_agent.task_progress if main_agent else 0,
>>>>>>> origin/master
            "updated_at": datetime.now().isoformat(),
        }
        
        return jsonify({
            "ok": True,
<<<<<<< HEAD
            "state": state
        })
=======
            "msg": "获取状态成功",
            "data": state
        }), 200
>>>>>>> origin/master
    
    except Exception as e:
        return jsonify({
            "ok": False,
<<<<<<< HEAD
            "msg": str(e)
        }), 500
=======
            "msg": str(e),
            "data": None
        }), 500
>>>>>>> origin/master
