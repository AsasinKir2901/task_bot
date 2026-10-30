import sqlite3
from datetime import datetime
from contextlib import closing

class TaskManager:
    def __init__(self, database):
        self.database = database

    def connect(self):
        return sqlite3.connect(self.database)

    def create_table(self):
        with closing(self.connect()) as conn:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        user_id INTEGER NOT NULL,
                        remind_at TEXT,
                        reminded INTEGER DEFAULT 0,
                        created_at TEXT
                    )
                """)

                columns = {
                    row[1]
                    for row in conn.execute(
                        "PRAGMA table_info(tasks)"
                    )
                }

                if "remind_at" not in columns:
                    conn.execute(
                        "ALTER TABLE tasks ADD COLUMN remind_at TEXT"
                    )

                if "reminded" not in columns:
                    conn.execute("""
                        ALTER TABLE tasks
                        ADD COLUMN reminded INTEGER DEFAULT 0
                    """)

                if "created_at" not in columns:
                    conn.execute(
                        "ALTER TABLE tasks ADD COLUMN created_at TEXT"
                    )

    def add_task(self, user_id, name, description=""):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with closing(self.connect()) as conn:
            with conn:
                conn.execute("""
                    INSERT INTO tasks
                        (name, description, user_id, created_at)
                    VALUES (?, ?, ?, ?)
                """, (name, description, user_id, created_at))

    def delete_task(self, task_name, user_id):
        with closing(self.connect()) as conn:
            with conn:
                cursor = conn.execute("""
                    DELETE FROM tasks
                    WHERE name = ? AND user_id = ?
                """, (task_name, user_id))

                return cursor.rowcount > 0

    def show_task(self, user_id):
        with closing(self.connect()) as conn:
            return conn.execute("""
                SELECT name
                FROM tasks
                WHERE user_id = ?
                ORDER BY id
            """, (user_id,)).fetchall()

    def show_task_all(self, user_id):
        return self.show_task(user_id)

    def show_task_many(self, user_id, num):
        with closing(self.connect()) as conn:
            return conn.execute("""
                SELECT name
                FROM tasks
                WHERE user_id = ?
                ORDER BY id
                LIMIT ?
            """, (user_id, num)).fetchall()
