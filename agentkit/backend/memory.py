"""
Manages short-term (conversation) and long-term (key/value) memory
using a local SQLite database.
"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Define the path for the SQLite database in the project root.
DB_PATH = Path(__file__).resolve().parent.parent.parent / "agentkit.db"

class MemoryManager:
    """Handles all interactions with the SQLite database for memory."""

    def __init__(self, db_path: Path = DB_PATH):
        """
        Initializes the MemoryManager and ensures the database tables are created.
        """
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a new database connection."""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Creates the necessary tables if they don't already exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Table for short-term conversation memory per run
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_memory (
                run_id TEXT NOT NULL,
                message_idx INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                PRIMARY KEY (run_id, message_idx)
            );
        """)

        # Table for long-term key-value storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

        conn.commit()
        conn.close()

    # --- Short-Term Memory Methods ---

    def add_message(self, run_id: str, role: str, content: str):
        """Adds a message to the conversation history for a specific run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Get the next message index for this run
            cursor.execute("SELECT COALESCE(MAX(message_idx), -1) + 1 FROM conversation_memory WHERE run_id = ?", (run_id,))
            next_idx = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO conversation_memory (run_id, message_idx, role, content) VALUES (?, ?, ?, ?)",
                (run_id, next_idx, role, content)
            )

    def get_messages(self, run_id: str) -> List[Dict[str, Any]]:
        """Retrieves all messages for a specific run, in order."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM conversation_memory WHERE run_id = ? ORDER BY message_idx ASC",
                (run_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # --- Long-Term Memory Methods ---

    def set_value(self, key: str, value: Any):
        """
        Sets a key-value pair in the long-term store.
        The value is stored as a JSON string.
        """
        json_value = json.dumps(value)
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO long_term_memory (key, value) VALUES (?, ?)",
                (key, json_value)
            )

    def get_value(self, key: str) -> Any:
        """

        Retrieves a value from the long-term store.
        Returns None if the key does not exist.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM long_term_memory WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

# A global instance for easy access from other modules
memory_manager = MemoryManager()
