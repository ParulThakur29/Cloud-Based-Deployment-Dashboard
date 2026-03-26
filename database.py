import sqlite3

def init_db():
    conn = sqlite3.connect('apps.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            container_id TEXT
        )
    ''')

    conn.commit()
    conn.close()