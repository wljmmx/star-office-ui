#!/usr/bin/env python3
"""
Star Office UI - Main Application Entry Point

Modern modular architecture with:
- Separation of concerns
- Dependency injection
- Clean API layering
- Real-time synchronization
"""

from flask import Flask, make_response, send_from_directory
from flask_socketio import SocketIO
from pathlib import Path
import os

# Import configuration
from config import Config

# Import API blueprints
from api import (
    agents_bp,
    tasks_bp,
    state_bp,
    assets_bp,
    config_bp,
    join_keys_bp,
)

# Import services
from utils import get_sync_service

def create_app():
    """Create and configure Flask application."""
    
    app = Flask(
        __name__,
        static_folder=str(Config.FRONTEND_DIR),
        static_url_path="/static"
    )
    
    # Configure Flask
    app.secret_key = Config.SECRET_KEY
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )
    
    # Initialize SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins=Config.SOCKETIO_CORS_ORIGINS,
        async_mode=Config.SOCKETIO_ASYNC_MODE
    )
    
    # Register API blueprints
    app.register_blueprint(agents_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(state_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(join_keys_bp)
    
    # Initialize sync service
    sync_service = get_sync_service(socketio)
    
    # Register SocketIO event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        sync_service.on_connect()
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        sync_service.on_disconnect()
    
    @socketio.on('subscribe_agents')
    def handle_subscribe():
        """Handle subscription request."""
        sync_service.on_subscribe()
    
    # Main page route
    @app.route("/", methods=["GET"])
    def index():
        """Serve the main page."""
        index_file = Config.FRONTEND_DIR / "index.html"
        if not index_file.exists():
            return "Frontend not found", 404
        
        with open(index_file, "r", encoding="utf-8") as f:
            html = f.read()
        
        # Add version timestamp for cache busting
        from datetime import datetime
        version_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        html = html.replace("{{VERSION_TIMESTAMP}}", version_ts)
        
        resp = make_response(html)
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        return resp
    
    # Static files route
    @app.route("/static/<path:filename>")
    def serve_static(filename):
        """Serve static files."""
        return send_from_directory(Config.FRONTEND_DIR, filename)
    
    # Store socketio in app for later access
    app.socketio = socketio
    app.sync_service = sync_service
    
    return app

def main():
    """Main entry point."""
    app = create_app()
    
    # Start sync service
    app.sync_service.start(interval=Config.SYNC_INTERVAL)
    
    # Print startup info
    print("=" * 60)
    print("🌟 Star Office UI Server")
    print("=" * 60)
    print(f"📁 Frontend: {Config.FRONTEND_DIR}")
    print(f"🗄️  Database: {Config.DATABASE_PATH}")
    print(f"🌐 Host: {Config.HOST}")
    print(f"🔢 Port: {Config.PORT}")
    print(f"🔧 Debug: {Config.DEBUG}")
    print(f"🔄 Sync Interval: {Config.SYNC_INTERVAL}s")
    print("=" * 60)
    print(f"🚀 Starting server at http://{Config.HOST}:{Config.PORT}")
    print("=" * 60)
    
    # Run server
    app.socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False  # Disable reloader to avoid double sync threads
    )
    
    # Cleanup
    app.sync_service.stop()

if __name__ == "__main__":
    main()
