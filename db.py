import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'mpesa.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            full_name   TEXT NOT NULL,
            phone       TEXT UNIQUE NOT NULL,
            pin_hash    TEXT NOT NULL,
            balance     REAL NOT NULL DEFAULT 0.0,
            created_at  TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id           TEXT PRIMARY KEY,
            sender_id    TEXT,
            receiver_id  TEXT,
            amount       REAL NOT NULL,
            type         TEXT NOT NULL,
            description  TEXT,
            status       TEXT NOT NULL DEFAULT 'success',
            created_at   TEXT NOT NULL,
            FOREIGN KEY (sender_id)   REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialised.")
