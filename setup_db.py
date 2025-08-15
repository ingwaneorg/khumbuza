#!/usr/bin/env python3
"""
khumbuza Database Setup
One-time initialization of the SQLite database
"""

import sqlite3
from pathlib import Path

# Configuration - must match khumbuza.py
DB_FILE = Path('/mnt/ssd/Applications/khumbuza/schedule.db')

def setup_database():
    """Create the database and tables"""
    
    # Ensure the directory exists
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating database at: {DB_FILE}")
    
    # Create database and tables
    conn = sqlite3.connect(DB_FILE)

    # Table: task
    conn.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            completed BOOLEAN DEFAULT 0,
            recurrence_type TEXT, -- NULL, 'weekly', 'monthly', 'yearly'
            recurrence_interval INTEGER DEFAULT 1,
            advance_notice_days INTEGER DEFAULT 0,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_date DATETIME
        );    
        ''')

    conn.commit()
    conn.close()
    
    print("✓ Database created successfully!")
    print("✓ Table 'tasks' created")
    print(f"✓ Database location: {DB_FILE}")

if __name__ == '__main__':
    setup_database()