import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "nexus.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    connection.commit()
    connection.close()


def create_task(title: str):

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO tasks (title, completed)
        VALUES (?, 0)
        """,
        (title,),
    )

    task_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return task_id


def list_tasks():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, title, completed
        FROM tasks
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "completed": bool(row["completed"]),
        }
        for row in rows
    ]


def complete_task(task_id: int):

    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        """,
        (task_id,),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated
