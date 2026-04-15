#!/bin/bash

# Migration script for adding project associations

DB_PATH="/home/wljmmx/.openclaw/workspace/main/skills/github-collab/github-collab.db"

echo "Database path: $DB_PATH"
echo ""

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "✗ Database not found: $DB_PATH"
    exit 1
fi

# Run migration using sqlite3 directly
echo "Checking current schema..."
echo ""

# Check if tasks table has project_id
TASKS_HAS_PROJECT=$(sqlite3 "$DB_PATH" "PRAGMA table_info(tasks);" | grep -c "project_id")

if [ "$TASKS_HAS_PROJECT" -gt 0 ]; then
    echo "✓ tasks table already has project_id column"
else
    echo "Adding project fields to tasks table..."
    sqlite3 "$DB_PATH" "ALTER TABLE tasks ADD COLUMN project_id INTEGER;"
    sqlite3 "$DB_PATH" "CREATE INDEX idx_tasks_project_id ON tasks(project_id);"
    sqlite3 "$DB_PATH" "ALTER TABLE tasks ADD COLUMN project_name TEXT;"
    sqlite3 "$DB_PATH" "ALTER TABLE tasks ADD COLUMN project_url TEXT;"
    echo "✓ Added project_id, project_name, project_url to tasks"
fi

# Check if agents table has current_project_id
AGENTS_HAS_PROJECT=$(sqlite3 "$DB_PATH" "PRAGMA table_info(agents);" | grep -c "current_project_id")

if [ "$AGENTS_HAS_PROJECT" -gt 0 ]; then
    echo "✓ agents table already has current_project_id column"
else
    echo "Adding project fields to agents table..."
    sqlite3 "$DB_PATH" "ALTER TABLE agents ADD COLUMN current_project_id INTEGER;"
    sqlite3 "$DB_PATH" "CREATE INDEX idx_agents_project_id ON agents(current_project_id);"
    sqlite3 "$DB_PATH" "ALTER TABLE agents ADD COLUMN project_name TEXT;"
    sqlite3 "$DB_PATH" "ALTER TABLE agents ADD COLUMN project_url TEXT;"
    echo "✓ Added current_project_id, project_name, project_url to agents"
fi

echo ""
echo "✓ Migration completed successfully"
echo ""

# Show updated schema
echo "Updated tasks table schema:"
sqlite3 "$DB_PATH" ".schema tasks"
echo ""
echo "Updated agents table schema:"
sqlite3 "$DB_PATH" ".schema agents"
