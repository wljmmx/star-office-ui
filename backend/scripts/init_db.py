#!/usr/bin/env python3
"""Initialize github-collab database for testing."""

import sqlite3
import os
from datetime import datetime

# Database path (relative to scripts/ directory)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "skills", "github-collab", "github-collab.db")

# Resolve relative path
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.abspath(DB_PATH)

# Create directory if needed
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """Initialize database with tables and sample data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables to allow fresh initialization
    cursor.execute("DROP TABLE IF EXISTS tasks")
    cursor.execute("DROP TABLE IF EXISTS agents")

    # Create agents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            pixel_character TEXT,
            avatar_url TEXT,
            role TEXT DEFAULT 'dev',
            status TEXT DEFAULT 'idle',
            current_task_id TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (current_task_id) REFERENCES tasks(id)
        )
    """)

    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            assigned_to TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (assigned_to) REFERENCES agents(id)
        )
    """)

    # Insert sample agents
    sample_agents = [
        ("star", "Star", "star.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Star", "main", "idle", None),
        ("dev1", "CoderBot", "coder.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Coder", "dev", "writing", "task1"),
        ("test1", "TestMaster", "tester.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Test", "test", "researching", "task2"),
        ("deploy1", "DeployBot", "deployer.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Deploy", "dev", "executing", "task3"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO agents (id, name, pixel_character, avatar_url, role, status, current_task_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(aid, name, pixel, avatar, role, status, task_id, datetime.now().isoformat(), datetime.now().isoformat()) 
          for aid, name, pixel, avatar, role, status, task_id in sample_agents])

    # Insert sample tasks
    sample_tasks = [
        ("task1", "实现用户登录功能", "writing", 45, "dev1"),
        ("task2", "调研 AI 代码生成方案", "researching", 70, "test1"),
        ("task3", "部署前端到生产环境", "executing", 20, "deploy1"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO tasks (id, title, status, progress, assigned_to, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [(tid, title, status, progress, assigned, datetime.now().isoformat(), datetime.now().isoformat()) 
          for tid, title, status, progress, assigned in sample_tasks])

    conn.commit()
    conn.close()

    print(f"✅ Database initialized: {DB_PATH}")
    print(f"   - Created tables: agents, tasks")
    print(f"   - Inserted {len(sample_agents)} agents")
    print(f"   - Inserted {len(sample_tasks)} tasks")

if __name__ == "__main__":
    init_db()
