#!/bin/bash

# Script to fix all merge conflicts by removing conflict markers
# and keeping the HEAD (local) version

cd /home/wljmmx/.openclaw/workspace/main/github-collab-officeUI

echo "Fixing merge conflicts..."

# List of files with conflicts
FILES=(
    "backend/store_utils.py"
    "backend/api/state.py"
    "backend/api/tasks.py"
    "backend/api/join_keys.py"
    "backend/app.py"
    "backend/tests/test_models.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        
        # Remove conflict markers and keep HEAD version
        # This is a simple approach - remove everything between <<<<<<< HEAD and =======
        # and remove ======= and >>>>>>> lines
        
        # Create backup
        cp "$file" "$file.backup"
        
        # Use sed to remove conflict markers and keep HEAD version
        sed -i '/^<<<<<<< HEAD$/,/^=======$/ {
            /^<<<<<<< HEAD$/d
            /^=======$/d
            /^>>>>>>>.*$/d
        }
        /^=======$/d
        /^>>>>>>>.*$/d' "$file"
        
        echo "✓ Fixed $file"
    fi
done

echo ""
echo "All conflicts fixed!"
echo ""
echo "Files fixed:"
git status --short
