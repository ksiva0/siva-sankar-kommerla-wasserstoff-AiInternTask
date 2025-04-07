# Email_Assistant/src/utils/db.py

import sqlite3

conn = sqlite3.connect("emails.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS emails (
    id TEXT PRIMARY KEY,
    sender TEXT,
    subject TEXT,
    snippet TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

conn.commit()


def save_email(email):
    c.execute("INSERT INTO emails (id, sender, subject, snippet) VALUES (?, ?, ?, ?)",
              (email["id"], email["sender"], email["subject"], email["snippet"]))
    conn.commit()


def email_exists(email_id):
    c.execute("SELECT id FROM emails WHERE id = ?", (email_id,))
    return c.fetchone() is not None
