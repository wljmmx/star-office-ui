"""Environments API routes."""

import sqlite3
import json
from flask import Blueprint, jsonify, request
from datetime import datetime
from config import Config
from services.environment_manager import Environment, EnvironmentManager, AgentDesk, DeskManager

environments_bp = Blueprint('environments', __name__, url_prefix='/api/environments')

@environments_bp.route('', methods=['GET'])
def get_all_environments():
    """Get all environments."""
    try:
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, theme, background_image, 
                   layout_config, settings, is_active, created_at, updated_at
            FROM environments
            ORDER BY is_active DESC, created_at ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        environments = [Environment.from_db(dict(row)).to_dict() for row in rows]
        
        return jsonify({
            "ok": True,
            "data": {
                "environments": environments,
            }
        }), 200
    
    except sqlite3.OperationalError:
        # Table doesn't exist, return default
        return jsonify({
            "ok": True,
            "data": {
                "environments": [EnvironmentManager.get_default_environment().to_dict()],
            }
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@environments_bp.route('/<env_id>', methods=['GET'])
def get_environment(env_id):
    """Get a specific environment."""
    try:
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, theme, background_image, 
                   layout_config, settings, is_active, created_at, updated_at
            FROM environments
            WHERE id = ?
        """, (env_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                "ok": False,
                "msg": "Environment not found",
                "data": None
            }), 404
        
        return jsonify({
            "ok": True,
            "data": {
                "environment": Environment.from_db(dict(row)).to_dict(),
            }
        }), 200
    
    except sqlite3.OperationalError:
        # Return default if table doesn't exist
        if env_id == "default":
            return jsonify({
                "ok": True,
                "data": {
                    "environment": EnvironmentManager.get_default_environment().to_dict(),
                }
            }), 200
        return jsonify({
            "ok": False,
            "msg": "Environment not found",
            "data": None
        }), 404
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@environments_bp.route('', methods=['POST'])
def create_environment():
    """Create a new environment."""
    try:
        data = request.get_json() or {}
        
        if not data.get('name'):
            return jsonify({
                "ok": False,
                "msg": "Name is required",
                "data": None
            }), 400
        
        env = Environment(
            id=data.get('id', data.get('name', '').lower().replace(' ', '-')),
            name=data['name'],
            description=data.get('description', ''),
            theme=data.get('theme', 'default'),
            background_image=data.get('background_image'),
            layout_config=json.dumps(data.get('layout_config', {})),
            settings=json.dumps(data.get('settings', {})),
            is_active=False,
        )
        
        if not EnvironmentManager.validate_environment(env):
            return jsonify({
                "ok": False,
                "msg": "Invalid environment configuration",
                "data": None
            }), 400
        
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO environments (id, name, description, theme, background_image, 
                                     layout_config, settings, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            env.id, env.name, env.description, env.theme, env.background_image,
            env.layout_config, env.settings, env.is_active
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "ok": True,
            "msg": "Environment created successfully",
            "data": {
                "environment": env.to_dict(),
            }
        }), 201
    
    except sqlite3.OperationalError:
        return jsonify({
            "ok": False,
            "msg": "Environments table not found. Run migration first.",
            "data": None
        }), 500
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@environments_bp.route('/<env_id>', methods=['PUT'])
def update_environment(env_id):
    """Update an environment."""
    try:
        data = request.get_json() or {}
        
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT id FROM environments WHERE id = ?", (env_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                "ok": False,
                "msg": "Environment not found",
                "data": None
            }), 404
        
        # Build update query
        updates = []
        params = []
        
        if 'name' in data:
            updates.append("name = ?")
            params.append(data['name'])
        if 'description' in data:
            updates.append("description = ?")
            params.append(data.get('description', ''))
        if 'theme' in data:
            updates.append("theme = ?")
            params.append(data['theme'])
        if 'background_image' in data:
            updates.append("background_image = ?")
            params.append(data.get('background_image'))
        if 'layout_config' in data:
            updates.append("layout_config = ?")
            params.append(json.dumps(data['layout_config']))
        if 'settings' in data:
            updates.append("settings = ?")
            params.append(json.dumps(data['settings']))
        if 'is_active' in data:
            updates.append("is_active = ?")
            params.append(1 if data['is_active'] else 0)
        
        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(env_id)
            
            cursor.execute(f"""
                UPDATE environments
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
            conn.commit()
        
        conn.close()
        
        return jsonify({
            "ok": True,
            "msg": "Environment updated successfully",
            "data": {
                "env_id": env_id,
            }
        }), 200
    
    except sqlite3.OperationalError:
        return jsonify({
            "ok": False,
            "msg": "Environments table not found",
            "data": None
        }), 500
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@environments_bp.route('/<env_id>/activate', methods=['POST'])
def activate_environment(env_id):
    """Activate an environment (deactivate others)."""
    try:
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        # Deactivate all
        cursor.execute("UPDATE environments SET is_active = 0")
        
        # Activate selected
        cursor.execute("""
            UPDATE environments SET is_active = 1, updated_at = datetime('now')
            WHERE id = ?
        """, (env_id,))
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        
        if updated:
            return jsonify({
                "ok": True,
                "msg": f"Environment '{env_id}' activated",
                "data": {
                    "env_id": env_id,
                }
            }), 200
        
        return jsonify({
            "ok": False,
            "msg": "Environment not found",
            "data": None
        }), 404
    
    except sqlite3.OperationalError:
        return jsonify({
            "ok": False,
            "msg": "Environments table not found",
            "data": None
        }), 500
        }), 500
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@environments_bp.route('/themes', methods=['GET'])
def get_themes():
    """Get all available themes."""
    return jsonify({
        "ok": True,
        "data": {
            "themes": EnvironmentManager.THEMES,
        }
    }), 200

# Desk assignment endpoints
@environments_bp.route('/desks', methods=['GET'])
def get_all_desks():
    """Get all desk assignments."""
    try:
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ad.*, a.name as agent_name
            FROM agent_desks ad
            LEFT JOIN agents a ON ad.agent_id = a.id
            ORDER BY ad.desk_number
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        desks = []
        for row in rows:
            desk = AgentDesk.from_db(dict(row))
            desk_dict = desk.to_dict()
            desk_dict["agent_name"] = row.get("agent_name")
            desks.append(desk_dict)
        
        return jsonify({
            "ok": True,
            "desks": desks,
        })
    
    except sqlite3.OperationalError:
        return jsonify({
            "ok": True,
            "desks": [],
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@environments_bp.route('/desks/<agent_id>', methods=['POST'])
def assign_desk(agent_id):
    """Assign a desk to an agent."""
    try:
        data = request.get_json() or {}
        
        desk_number = data.get('desk_number')
        if not desk_number:
            return jsonify({
                "ok": False,
                "msg": "Desk number is required",
                "data": None
            }), 400
        
        desk = DeskManager.create_desk_assignment(agent_id, desk_number)
        
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_desks (id, agent_id, desk_number, position_x, position_y, assigned_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (desk.id, desk.agent_id, desk.desk_number, desk.position_x, desk.position_y))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "ok": True,
            "msg": f"Desk {desk_number} assigned to agent {agent_id}",
            "desk": desk.to_dict(),
        })
    
    except sqlite3.OperationalError:
        return jsonify({
            "ok": False,
            "msg": "agent_desks table not found"
        }), 500
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500

@environments_bp.route('/desks/<agent_id>', methods=['DELETE'])
def unassign_desk(agent_id):
    """Unassign desk from an agent."""
    try:
        conn = sqlite3.connect(str(Config.DATABASE_PATH))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM agent_desks WHERE agent_id = ?", (agent_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        if deleted:
            return jsonify({
                "ok": True,
                "msg": f"Desk unassigned from agent {agent_id}",
                "data": {
                    "agent_id": agent_id,
                }
            }), 200
        
        return jsonify({
            "ok": False,
            "msg": "No desk assignment found",
            "data": None
        }), 404
    
    except sqlite3.OperationalError:
        return jsonify({
            "ok": False,
            "msg": "agent_desks table not found",
            "data": None
        }), 500
    except Exception as e:
        return jsonify({
            "ok": False,
            "msg": str(e)
        }), 500
