"""Agents API routes."""

from flask import jsonify, request
from . import agents_bp
from services.database_service import get_db_service
from config import Config

@agents_bp.route('', methods=['GET'])
def get_all_agents():
    """Get all agents."""
    try:
        db = get_db_service()
        agents = db.load_all_agents()
        return jsonify({
            "ok": True,
            "agents": [agent.to_dict() for agent in agents]
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent."""
    try:
        db = get_db_service()
        agent = db.get_agent_by_id(agent_id)
        
        if agent:
            return jsonify({
                "ok": True,
                "agent": agent.to_dict()
            })
        
        return jsonify({
            "ok": False,
            "msg": "Agent not found"
        }), 404
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@agents_bp.route('/<agent_id>/status', methods=['POST'])
def update_agent_status(agent_id):
    """Update agent status."""
    try:
        data = request.get_json() or {}
        new_status = data.get('state', '')
        
        if not new_status:
            return jsonify({
                "ok": False,
                "msg": "Missing state parameter"
            }), 400
        
        # Normalize state
        db = get_db_service()
        normalized_state = db.normalize_agent_state(new_status)
        
        # Update database
        success = db.update_agent_status(agent_id, normalized_state)
        
        if success:
            return jsonify({
                "ok": True,
                "state": normalized_state
            })
        
        return jsonify({
            "ok": False,
            "msg": "Failed to update agent status"
        }), 500
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
