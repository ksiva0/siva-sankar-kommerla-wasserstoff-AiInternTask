# src/services/database_service.py

import sqlite3
from datetime import datetime

class DatabaseService:
    def __init__(self, db_path='emails.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_emails (
                    id TEXT PRIMARY KEY
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    sender TEXT,
                    recipient TEXT,
                    subject TEXT,
                    timestamp INTEGER,
                    body TEXT
                )
            """)

    def is_email_processed(self, email_id):
        cursor = self.conn.execute("SELECT 1 FROM processed_emails WHERE id = ?", (email_id,))
        return cursor.fetchone() is not None

    def mark_email_as_processed(self, email_id):
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO processed_emails (id) VALUES (?)", (email_id,))

    def save_email(self, email_id, sender, recipient, subject, timestamp, body):
        with self.conn:
            self.conn.execute("""
                INSERT OR IGNORE INTO emails (id, sender, recipient, subject, timestamp, body)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email_id, sender, recipient, subject, int(timestamp), body))
