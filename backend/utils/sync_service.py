"""Real-time sync service for SocketIO."""

import json
import threading
import time
from typing import Optional

from flask_socketio import SocketIO, emit
from services.database_service import get_db_service

class SyncService:
    """Service for real-time synchronization."""
    
    def __init__(self, socketio: SocketIO):
        """Initialize sync service."""
        self.socketio = socketio
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_agents_hash: str = ""
    
    def start(self, interval: int = 5):
        """Start background sync loop."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._sync_loop,
            args=(interval,),
            daemon=True
        )
        self.thread.start()
        print(f"[SyncService] Started with {interval}s interval")
    
    def stop(self):
        """Stop background sync loop."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[SyncService] Stopped")
    
    def _sync_loop(self, interval: int):
        """Background sync loop."""
        while self.running:
            try:
                time.sleep(interval)
                
                # Load current agents
                db = get_db_service()
                agents = db.load_all_agents()
                
                # Calculate hash for change detection
                current_hash = json.dumps(
                    [a.to_dict() for a in agents],
                    sort_keys=True
                )
                
                # Broadcast if changed
                if current_hash != self.last_agents_hash:
                    self.broadcast_agents(agents)
                    self.last_agents_hash = current_hash
            
            except Exception as e:
                print(f"[SyncService] Error: {e}")
    
    def broadcast_agents(self, agents):
        """Broadcast agent updates to all clients."""
        try:
            agent_dicts = [agent.to_dict() for agent in agents]
            self.socketio.emit("agents_update", {"agents": agent_dicts})
            print(f"[SyncService] Broadcasted {len(agents)} agents")
        except Exception as e:
            print(f"[SyncService] Broadcast error: {e}")
    
    def on_connect(self):
        """Handle client connection."""
        try:
            db = get_db_service()
            agents = db.load_all_agents()
            emit("agents_update", {"agents": [a.to_dict() for a in agents]})
            print(f"[SyncService] Client connected, sent {len(agents)} agents")
        except Exception as e:
            print(f"[SyncService] Connect error: {e}")
    
    def on_disconnect(self):
        """Handle client disconnection."""
        print("[SyncService] Client disconnected")
    
    def on_subscribe(self):
        """Handle subscription request."""
        try:
            db = get_db_service()
            agents = db.load_all_agents()
            emit("agents_update", {"agents": [a.to_dict() for a in agents]})
            print(f"[SyncService] Subscription: sent {len(agents)} agents")
        except Exception as e:
            print(f"[SyncService] Subscribe error: {e}")

# Singleton instance
_sync_service: Optional[SyncService] = None

def get_sync_service(socketio: SocketIO) -> SyncService:
    """Get sync service singleton."""
    global _sync_service
    if _sync_service is None:
        _sync_service = SyncService(socketio)
    return _sync_service
