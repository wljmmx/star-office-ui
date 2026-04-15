"""Projects API endpoints."""

from flask import Blueprint, jsonify
from services.database_service import get_db_service

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('', methods=['GET'])
def list_projects():
    """List all projects."""
    try:
        db_service = get_db_service()
        projects = db_service.load_all_projects()
        
        return jsonify({
            'success': True,
            'data': [project.to_dict() for project in projects],
            'count': len(projects)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id: int):
    """Get a specific project by ID."""
    try:
        db_service = get_db_service()
        project = db_service.get_project_by_id(project_id)
        
        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': project.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
