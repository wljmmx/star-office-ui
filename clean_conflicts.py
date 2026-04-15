#!/usr/bin/env python3
"""Clean merge conflicts from files."""

import os
import re
from pathlib import Path

def clean_file(filepath):
    """Remove merge conflict markers from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has conflicts
    if '<<<<<<<' not in content and '=====' not in content:
        return False
    
    print(f"Cleaning {filepath}...")
    
    # Split by conflict markers and keep HEAD version (between <<<<<<< HEAD and =======)
    lines = content.split('\n')
    cleaned_lines = []
    in_conflict = False
    skip_until_equals = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('<<<<<<<'):
            in_conflict = True
            skip_until_equals = True
            i += 1
            continue
        
        if skip_until_equals:
            if line.startswith('====='):
                skip_until_equals = False
                in_conflict = False
            i += 1
            continue
        
        if line.startswith('>>>>>>>'):
            in_conflict = False
            i += 1
            continue
        
        cleaned_lines.append(line)
        i += 1
    
    # Write cleaned content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    return True

def main():
    """Main function."""
    base_dir = Path(__file__).parent / 'backend'
    
    # Find all Python files
    python_files = list(base_dir.rglob('*.py'))
    
    # Exclude archived files
    python_files = [f for f in python_files if 'archived' not in str(f)]
    
    cleaned_count = 0
    for filepath in python_files:
        if clean_file(filepath):
            cleaned_count += 1
    
    print(f"\nCleaned {cleaned_count} files")

if __name__ == '__main__':
    main()
