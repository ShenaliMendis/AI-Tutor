import sqlite3
import json
import os
from contextlib import contextmanager

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'aitutor.db')

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS session_data (
            key TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
        ''')
        conn.commit()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def set_data(key, data):
    with get_db_connection() as conn:
        conn.execute('INSERT OR REPLACE INTO session_data (key, data) VALUES (?, ?)',
                    (key, json.dumps(data)))
        conn.commit()

def get_data(key):
    with get_db_connection() as conn:
        cur = conn.execute('SELECT data FROM session_data WHERE key = ?', (key,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

def delete_data(key):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM session_data WHERE key = ?', (key,))
        conn.commit()

def clear_all():
    with get_db_connection() as conn:
        conn.execute('DELETE FROM session_data')
        conn.commit()
