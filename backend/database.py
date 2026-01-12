import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

DATABASE_PATH = "./data/resumes.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create resumes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id TEXT PRIMARY KEY,
            job_title TEXT NOT NULL,
            job_description TEXT,
            resume_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create chat_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_resume(resume_id: str, job_title: str, job_description: str, resume_data: dict):
    """Save a generated resume to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO resumes (id, job_title, job_description, resume_data, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (resume_id, job_title, job_description, json.dumps(resume_data), datetime.now()))
    
    conn.commit()
    conn.close()

def get_resume(resume_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a resume by ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "job_title": row[1],
            "job_description": row[2],
            "resume_data": json.loads(row[3]),
            "created_at": row[4]
        }
    return None

def get_all_resumes() -> List[Dict[str, Any]]:
    """Get all resumes (summary only, without full data for performance)."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, job_title, created_at, resume_data 
        FROM resumes 
        ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    resumes = []
    for row in rows:
        resume_data = json.loads(row[3])
        resumes.append({
            "id": row[0],
            "job_title": row[1],
            "created_at": row[2],
            "name": resume_data.get("name", "Unknown")
        })
    return resumes

def delete_resume(resume_id: str) -> bool:
    """Delete a resume and its chat history."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM chat_history WHERE resume_id = ?', (resume_id,))
    cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def save_chat_message(resume_id: str, role: str, content: str):
    """Save a chat message."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_history (resume_id, role, content)
        VALUES (?, ?, ?)
    ''', (resume_id, role, content))
    
    conn.commit()
    conn.close()

def get_chat_history(resume_id: str) -> List[Dict[str, str]]:
    """Get chat history for a resume."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, content FROM chat_history 
        WHERE resume_id = ? 
        ORDER BY created_at ASC
    ''', (resume_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [{"role": row[0], "content": row[1]} for row in rows]

# Initialize database on module import
init_db()

