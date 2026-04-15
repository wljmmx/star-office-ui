#!/usr/bin/env python3
"""Initialize github-collab database for testing."""

import sqlite3
import os
from datetime import datetime

# Database path - use environment variable or default
DB_PATH = os.getenv("DATABASE_PATH", "/data/github-collab.db")

# Create directory if needed
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """Initialize database with tables and sample data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            github_url TEXT,
            description TEXT,
            status TEXT DEFAULT 'active',
            work_dir TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

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
            project_id TEXT,
            project_name TEXT,
            project_url TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (current_task_id) REFERENCES tasks(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
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
            project_id TEXT,
            project_name TEXT,
            project_url TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (assigned_to) REFERENCES agents(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Insert sample project
    sample_project = (
        "project1",
        "Star Office UI",
        "https://github.com/wljmmx/star-office-ui.git",
        "Star Office UI 项目",
        "active",
        "/home/wljmmx/.openclaw/workspace/main/github-collab-officeUI",
        datetime.now().isoformat(),
        datetime.now().isoformat()
    )
    cursor.execute("""
        INSERT OR REPLACE INTO projects (id, name, github_url, description, status, work_dir, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_project)

    # Insert sample agents
    sample_agents = [
        ("star", "Star", "star.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Star", "main", "idle", None, "project1", "Star Office UI", "https://github.com/wljmmx/star-office-ui.git"),
        ("dev1", "CoderBot", "coder.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Coder", "dev", "writing", "task1", "project1", "Star Office UI", "https://github.com/wljmmx/star-office-ui.git"),
        ("test1", "TestMaster", "tester.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Test", "test", "researching", "task2", "project1", "Star Office UI", "https://github.com/wljmmx/star-office-ui.git"),
        ("deploy1", "DeployBot", "deployer.png", "https://api.dicebear.com/7.x/avataaars/svg?seed=Deploy", "dev", "executing", "task3", "project1", "Star Office UI", "https://github.com/wljmmx/star-office-ui.git"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO agents (id, name, pixel_character, avatar_url, role, status, current_task_id, project_id, project_name, project_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(aid, name, pixel, avatar, role, status, task_id, pid, pname, purl, datetime.now().isoformat(), datetime.now().isoformat()) 
          for aid, name, pixel, avatar, role, status, task_id, pid, pname, purl in sample_agents])

    # Insert sample tasks
    sample_tasks = [
        ("task1", "实现用户登录功能", "writing", 45, "dev1", "project1", "Star Office UI", "https://github.com/wljmmx/star-office-ui.git"),
        ("task2", "调研 AI 代码生成方案", "researching", 70, "test1", "project1", "Star Office UI", "https://github.com/wljmmx/star-office-ui.git"),
        ("task3", "部署前端到生产环境", "executing", 20, "deploy1", "project1", "Star Office UI", "https://github.com/wljmmx/star-office-ui.git"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO tasks (id, title, status, progress, assigned_to, project_id, project_name, project_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(tid, title, status, progress, assigned, pid, pname, purl, datetime.now().isoformat(), datetime.now().isoformat()) 
          for tid, title, status, progress, assigned, pid, pname, purl in sample_tasks])

    conn.commit()
    conn.close()

    print(f"✅ Database initialized: {DB_PATH}")
    print(f"   - Created tables: projects, agents, tasks")
    print(f"   - Inserted 1 project")
    print(f"   - Inserted {len(sample_agents)} agents")
    print(f"   - Inserted {len(sample_tasks)} tasks")

if __name__ == "__main__":
    init_db()
