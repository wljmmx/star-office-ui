#!/usr/bin/env python3
"""Check database schema."""
import sqlite3
import os

db_path = "/workspace/star-office-ui/github-collab/github-collab.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Get agents schema
cursor.execute("PRAGMA table_info(agents);")
agents_cols = cursor.fetchall()
print("\nAgents columns:")
for col in agents_cols:
    print(f"  {col[1]} ({col[2]})")

# Get tasks schema
cursor.execute("PRAGMA table_info(tasks);")
tasks_cols = cursor.fetchall()
print("\nTasks columns:")
for col in tasks_cols:
    print(f"  {col[1]} ({col[2]})")

# Sample data
cursor.execute("SELECT * FROM agents LIMIT 1;")
sample = cursor.fetchone()
print("\nSample agent:", sample)

cursor.execute("SELECT * FROM tasks LIMIT 1;")
sample = cursor.fetchone()
print("Sample task:", sample)

conn.close()
