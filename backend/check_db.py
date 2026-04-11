#!/usr/bin/env python3
import sqlite3

db_path = "/workspace/star-office-ui/github-collab/github-collab.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(agents);")
cols = cursor.fetchall()
print("Agents columns:", [c[1] for c in cols])

cursor.execute("PRAGMA table_info(tasks);")
cols = cursor.fetchall()
print("Tasks columns:", [c[1] for c in cols])

cursor.execute("SELECT * FROM agents LIMIT 2;")
rows = cursor.fetchall()
print("\nSample agents:")
for r in rows:
    print(" ", r)

cursor.execute("SELECT * FROM tasks LIMIT 2;")
rows = cursor.fetchall()
print("\nSample tasks:")
for r in rows:
    print(" ", r)

conn.close()
