"""Agents API routes with input validation."""

from flask import jsonify, request
from . import agents_bp
from services.database_service import get_db_service
from validators import AgentStatusUpdateRequest, AgentIDPath, ValidationErrorResponse

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
    """Get a specific agent by ID."""
    try:
        # Validate agent_id path parameter
        try:
            AgentIDPath(agent_id=agent_id)
        except Exception as e:
            return jsonify({
                "ok": False,
                "msg": f"Invalid agent_id: {str(e)}"
            }), 400
        
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
    """Update agent status with validated input."""
    try:
        # Validate agent_id path parameter
        try:
            AgentIDPath(agent_id=agent_id)
        except Exception as e:
            return jsonify({
                "ok": False,
                "msg": f"Invalid agent_id: {str(e)}"
            }), 400
        
        # Validate request body
        try:
            data = request.get_json() or {}
            validation = AgentStatusUpdateRequest(**data)
            normalized_state = validation.state
        except Exception as e:
            return jsonify({
                "ok": False,
                "msg": f"Invalid request: {str(e)}"
            }), 400
        
        # Update database
        db = get_db_service()
        success = db.update_agent_status(agent_id, normalized_state)
        
        if success:
            return jsonify({
                "ok": True,
                "state": normalized_state
            })
        
        return jsonify({
            "ok": False,
            "msg": "Failed to update agent status - agent not found"
        }), 404
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
