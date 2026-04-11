#!/usr/bin/env python3
"""Test database connection."""
import sys
sys.path.insert(0, '/workspace/star-office-ui/backend')

from database import GITHUB_COLLAB_DB, load_agents_from_db, load_tasks_from_db
import os

print(f"Database path: {GITHUB_COLLAB_DB}")
print(f"Database exists: {os.path.exists(GITHUB_COLLAB_DB)}")
print(f"Database size: {os.path.getsize(GITHUB_COLLAB_DB) if os.path.exists(GITHUB_COLLAB_DB) else 0} bytes")

agents = load_agents_from_db()
print(f"\nLoaded {len(agents)} agents:")
for agent in agents:
    print(f"  - {agent['name']} ({agent['agentId']}): {agent['state']} @ {agent['area']}")
    if agent.get('task_title'):
        print(f"    Task: {agent['task_title']} ({agent.get('task_progress', 0)}%)")

tasks = load_tasks_from_db()
print(f"\nLoaded {len(tasks)} tasks:")
for task in tasks:
    print(f"  - {task['title']} ({task['status']}): {task['progress']}%")
