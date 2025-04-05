# src/services/database_service.py

import sqlite3
from datetime import datetime

class DatabaseService:
    def __init__(self, db_path="emails.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_schema()

    def create_schema(self):
        query = '''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            timestamp TEXT,
            body TEXT
        );
        '''
        self.conn.execute(query)
        self.conn.commit()

    def save_email(self, email_id, sender, recipient, subject, timestamp, body):
        self.conn.execute(
            "INSERT OR IGNORE INTO emails (id, sender, recipient, subject, timestamp, body) VALUES (?, ?, ?, ?, ?, ?)",
            (email_id, sender, recipient, subject, timestamp.isoformat(), body)
        )
        self.conn.commit()
