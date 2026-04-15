"""
Migration: Add project associations to tasks and agents tables

This migration adds project_id fields to enable direct project associations.
"""

import sqlite3
from pathlib import Path
from typing import Optional

def migrate(db_path: Path):
    """Apply migration to add project associations."""
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if migration already applied
        cursor.execute("PRAGMA table_info(tasks)")
        tasks_columns = [row[1] for row in cursor.fetchall()]
        
        if 'project_id' in tasks_columns:
            print("✓ Migration already applied: tasks.project_id exists")
        else:
            # Add project_id to tasks table
            print("Adding project_id to tasks table...")
            cursor.execute("""
                ALTER TABLE tasks ADD COLUMN project_id INTEGER
            """)
            cursor.execute("""
                CREATE INDEX idx_tasks_project_id ON tasks(project_id)
            """)
            cursor.execute("""
                ALTER TABLE tasks ADD COLUMN project_name TEXT
            """)
            cursor.execute("""
                ALTER TABLE tasks ADD COLUMN project_url TEXT
            """)
            print("✓ Added project_id, project_name, project_url to tasks")
        
        # Check agents table
        cursor.execute("PRAGMA table_info(agents)")
        agents_columns = [row[1] for row in cursor.fetchall()]
        
        if 'current_project_id' in agents_columns:
            print("✓ Migration already applied: agents.current_project_id exists")
        else:
            # Add project fields to agents table
            print("Adding project fields to agents table...")
            cursor.execute("""
                ALTER TABLE agents ADD COLUMN current_project_id INTEGER
            """)
            cursor.execute("""
                CREATE INDEX idx_agents_project_id ON agents(current_project_id)
            """)
            cursor.execute("""
                ALTER TABLE agents ADD COLUMN project_name TEXT
            """)
            cursor.execute("""
                ALTER TABLE agents ADD COLUMN project_url TEXT
            """)
            print("✓ Added current_project_id, project_name, project_url to agents")
        
        conn.commit()
        print("✓ Migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()

def rollback(db_path: Path):
    """Rollback migration (remove project association fields)."""
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # SQLite doesn't support DROP COLUMN in older versions
        # We'll need to recreate tables without the columns
        print("⚠️  Warning: SQLite rollback requires table recreation")
        print("⚠️  Manual intervention may be required")
        
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    # Default database path
    db_path = Path(__file__).parent.parent.parent / "github-collab.db"
    
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    
    print(f"Database path: {db_path}")
    
    if not db_path.exists():
        print(f"✗ Database not found: {db_path}")
        sys.exit(1)
    
    confirm = input("Apply migration? (y/N): ")
    if confirm.lower() == 'y':
        migrate(db_path)
    else:
        print("Migration cancelled")
