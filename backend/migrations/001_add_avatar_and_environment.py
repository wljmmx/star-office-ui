#!/usr/bin/env python3
"""
Migration 001: Add avatar and environment support

Changes:
1. Add avatar_type, avatar_data columns to agents table
2. Add list_id, position, checklist columns to tasks table
3. Create environments table
4. Create agent_desks table
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).resolve().parent.parent / "github-collab" / "github-collab.db"

if not DB_PATH.exists():
    # Try alternative paths
    ALT_PATHS = [
        Path(__file__).resolve().parent.parent.parent / "github-collab" / "github-collab.db",
        Path("/home/wljmmx/.openclaw/workspace/coder/skills/github-collab/github-collab.db"),
    ]
    for alt_path in ALT_PATHS:
        if alt_path.exists():
            DB_PATH = alt_path
            break

def migrate():
    """Run migration."""
    print(f"Database path: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # 1. Add avatar columns to agents table
        print("Adding avatar columns to agents table...")
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN avatar_type TEXT DEFAULT 'pixel'")
            print("  - Added avatar_type column")
        except sqlite3.OperationalError:
            print("  - avatar_type column already exists")
        
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN avatar_data TEXT DEFAULT NULL")
            print("  - Added avatar_data column")
        except sqlite3.OperationalError:
            print("  - avatar_data column already exists")
        
        # 2. Add task list management columns to tasks table
        print("Adding task list management columns to tasks table...")
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN list_id TEXT DEFAULT NULL")
            print("  - Added list_id column")
        except sqlite3.OperationalError:
            print("  - list_id column already exists")
        
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN position INTEGER DEFAULT 0")
            print("  - Added position column")
        except sqlite3.OperationalError:
            print("  - position column already exists")
        
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN checklist TEXT DEFAULT NULL")
            print("  - Added checklist column (JSON)")
        except sqlite3.OperationalError:
            print("  - checklist column already exists")
        
        # 3. Create environments table
        print("Creating environments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                theme TEXT DEFAULT 'default',
                background_image TEXT DEFAULT NULL,
                layout_config TEXT DEFAULT NULL,
                settings TEXT DEFAULT NULL,
                is_active INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  - environments table created")
        
        # Insert default environment
        cursor.execute("""
            INSERT OR IGNORE INTO environments (id, name, description, theme, is_active)
            VALUES ('default', 'Default Office', 'Default office environment', 'default', 1)
        """)
        print("  - Default environment inserted")
        
        # 4. Create agent_desks table
        print("Creating agent_desks table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_desks (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                desk_number INTEGER NOT NULL,
                position_x REAL DEFAULT 0,
                position_y REAL DEFAULT 0,
                assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)
        print("  - agent_desks table created")
        
        # Commit changes
        conn.commit()
        print("\nMigration completed successfully!")
        
        # Print summary
        print("\nSchema summary:")
        cursor.execute("PRAGMA table_info(agents)")
        print(f"  agents columns: {[row[1] for row in cursor.fetchall()]}")
        
        cursor.execute("PRAGMA table_info(tasks)")
        print(f"  tasks columns: {[row[1] for row in cursor.fetchall()]}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        print(f"  tables: {[row[0] for row in cursor.fetchall()]}")
        
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
