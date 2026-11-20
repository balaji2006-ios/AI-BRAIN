import sqlite3
import uuid
from datetime import datetime
from assistant.config import CONVERSATION_DIR


class ConversationMemory:

    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.database_folder = CONVERSATION_DIR
        self.database_folder.mkdir(parents=True, exist_ok=True)
        self.db_path = self.database_folder / "ai_brain.db"
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    def create_session(self, title="New Conversation"):
        with self.get_connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO conversations
                (session_id, title, created_at)
                VALUES (?, ?, ?)
                """,
                (self.session_id, title, datetime.now().isoformat())
            )

    def add_user_message(self, content):
        self.save_message("user", content)

    def add_assistant_message(self, content):
        self.save_message("assistant", content)

    def save_message(self, role, content):
        self.create_session()
        with self.get_connection() as connection:
            if role == "user":
                cursor = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM messages
                    WHERE session_id = ? AND role = 'user'
                    """,
                    (self.session_id,)
                )
                user_message_count = cursor.fetchone()[0]
                if user_message_count == 0:
                    title = " ".join(content.split())
                    if len(title) > 40:
                        title = title[:37] + "..."
                    connection.execute(
                        """
                        UPDATE conversations
                        SET title = ?
                        WHERE session_id = ?
                        """,
                        (title, self.session_id)
                    )

            connection.execute(
                """
                INSERT INTO messages
                (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (self.session_id, role, content, datetime.now().isoformat())
            )

    def get_history(self):
        with self.get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (self.session_id,)
            )
            rows = cursor.fetchall()

        return [{"role": row[0], "content": row[1]} for row in rows]

    def get_message_count(self):
        with self.get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE session_id = ?
                """,
                (self.session_id,)
            )
            return cursor.fetchone()[0]

    def clear_history(self):
        with self.get_connection() as connection:
            connection.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (self.session_id,)
            )

    def get_all_sessions(self):
        with self.get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT c.session_id, c.title, c.created_at
                FROM conversations c
                WHERE EXISTS (
                    SELECT 1
                    FROM messages m
                    WHERE m.session_id = c.session_id
                )
                ORDER BY c.created_at DESC
                """
            )
            rows = cursor.fetchall()

        return [
            {
                "session_id": row[0],
                "title": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]

    def delete_session(self, session_id):
        with self.get_connection() as connection:
            connection.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (session_id,)
            )
            connection.execute(
                "DELETE FROM conversations WHERE session_id = ?",
                (session_id,)
            )
