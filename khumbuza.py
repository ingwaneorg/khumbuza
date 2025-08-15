#!/usr/bin/env python3
"""
Khumbuza - Simple Task Management Tool
"""

import click
import sqlite3
import os
import json
from datetime import datetime, timedelta, date
from pathlib import Path

# Configuration
DB_FILE = Path('/mnt/ssd/Applications/khumbuza/tasks.db')


def init_database():
    """Initialise the SQLite database"""
    if not DB_FILE.exists():
        click.echo("Database not found. Run 'python setup_db.py' first.")
        exit(1)
    
    # Database exists, just return
    return

def get_db_connection():
    """Get database connection"""
    if not DB_FILE.exists():
        click.echo("Database not found. Run 'python setup_db.py' first.")
        exit(1)

    conn = sqlite3.connect(DB_FILE)
    return conn

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Khumbuza - Simple Task Management Tool"""
    init_database()

@cli.command()
@click.argument('title')
@click.option('--due', help='Due date (YYYY-MM-DD)')
@click.option('--description', '--desc', help='Task description')
@click.option('--weekly', is_flag=True, help='Repeat weekly')
@click.option('--monthly', is_flag=True, help='Repeat monthly') 
@click.option('--yearly', is_flag=True, help='Repeat yearly')
@click.option('--remind', type=int, help='Advance notice days')
def add(title, due, description, weekly, monthly, yearly, remind):
    """Add a new task"""


    # Parse due date if provided
    due_date = None
    if due:
        try:
            datetime.strptime(due, '%Y-%m-%d').date()
            due_date = due # Stored as a string
        except ValueError:
            click.echo(f"Error: Invalid date format. Use YYYY-MM-DD")
            return

    # Check only one recurrence type is set
    recurrence_flags = [weekly, monthly, yearly]
    if sum(recurrence_flags) > 1:
        click.echo("Error: Only one recurrence type allowed")
        return

    # Set recurrence type
    if weekly:
        recurrence_type = 'weekly'
    elif monthly :
        recurrence_type = 'monthly'
    elif yearly:
        recurrence_type = 'yearly'
    else:
        recurrence_type = None

    # Add reminder
    advance_notice_days = 0
    if remind:
        if remind < 0:
            click.echo("Error: Reminder days cannot be negative")
            return
        advance_notice_days = remind

    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO task (title, description, due_date, recurrence_type, advance_notice_days)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, description, due_date, recurrence_type, advance_notice_days))
    
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    due_str = f" due {due_date}" if due_date else ""
    click.echo(f"Added task #{task_id}: '{title}'{due_str}")

@cli.command()
@click.option('--days', default=30, help='Show tasks due in next N days')
@click.option('--all', 'show_all', is_flag=True, help='Show all incomplete tasks')
def list(days, show_all):
    """List tasks"""
    conn = get_db_connection()

    if show_all:
        query = '''
            SELECT id, title, due_date, description
            FROM task
            WHERE completed = 0
            ORDER BY due_date ASC, id ASC
        '''
        params = []
    else:
        cutoff_date = (date.today() + timedelta(days=days)).isoformat()
        query = '''
            SELECT id, title, due_date, description
            FROM task
            WHERE completed = 0 
            AND (due_date IS NULL OR due_date <= ?)
            ORDER BY due_date ASC, id ASC
        '''
        params = [cutoff_date]
    
    results = conn.execute(query, params).fetchall()
    conn.close()
    
    if not results:
        period = "all tasks" if show_all else f"next {days} days"
        click.echo(f"No tasks due in the {period}.")
        return
    
    period = "All incomplete tasks" if show_all else f"Tasks due in next {days} days"
    click.echo(f"\n{period}:")
    click.echo("-" * 50)
    
    for task_id, title, due_date, description in results:
        due_str = f" (due: {due_date})" if due_date else ""
        click.echo(f"#{task_id}: {title}{due_str}")
        if description:
            click.echo(f"    {description}")

@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark a task as complete"""
    conn = get_db_connection()
    
    # Check if task exists and is not already completed
    result = conn.execute('''
        SELECT title, completed 
        FROM task
        WHERE id = ?
        AND deleted_date IS NULL
    ''', (task_id,)).fetchone()
    
    if not result:
        click.echo(f"Task #{task_id} not found")
        conn.close()
        return

    title, is_completed = result
    if is_completed:
        click.echo(f"Task #{task_id} is already completed")
        conn.close()
        return
    
    # Mark as complete
    conn.execute('''
        UPDATE task 
        SET completed = 1, 
            completed_date = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (task_id,))
    
    conn.commit()
    conn.close()
    
    click.echo(f"Completed task #{task_id}: '{title}'")

@cli.command()
@click.argument('task_id', type=int)
@click.option('--force', is_flag=True, help='Force deletion on task not completed') 
def remove(task_id, force):
    """Remove a task completely"""
    conn = get_db_connection()
    
    # Check if task exists
    result = conn.execute('''
        SELECT title, completed
        FROM task
        WHERE id = ?
        AND deleted_date IS NULL
    ''', (task_id,)).fetchone()

    if not result:
        click.echo(f"Task #{task_id} not found")
        conn.close()
        return
    
    title, is_completed = result

    # Don't delete tasks that are not completed
    if not is_completed and not force:
        click.echo(f"Task #{task_id} is not completed.")
        click.echo(f"Mark as complete or use --force")
        return
    
    # Mark as deleted
    conn.execute('''
        UPDATE task 
        SET deleted_date = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (task_id,))

    conn.commit()
    conn.close()
    
    click.echo(f"Removed task #{task_id}: '{title}'")

if __name__ == '__main__':
    cli()