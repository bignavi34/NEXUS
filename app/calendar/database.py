import sqlite3
from pathlib import Path
from typing import Optional


DB_PATH = Path("app/calendar/calendar.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def initialize_database():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def create_event(
    title: str,
    start_time: str,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO events
        (
            title,
            description,
            start_time,
            end_time,
            location
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            title,
            description,
            start_time,
            end_time,
            location,
        ),
    )

    event_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return event_id


def list_events():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            title,
            description,
            start_time,
            end_time,
            location,
            created_at
        FROM events
        ORDER BY start_time
        """
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_event(event_id: int):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            id,
            title,
            description,
            start_time,
            end_time,
            location,
            created_at
        FROM events
        WHERE id = ?
        """,
        (event_id,),
    ).fetchone()

    conn.close()

    if row is None:
        return None

    return dict(row)


def update_event(
    event_id: int,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
):
    conn = get_connection()

    current = conn.execute(
        """
        SELECT *
        FROM events
        WHERE id = ?
        """,
        (event_id,),
    ).fetchone()

    if current is None:
        conn.close()
        return None

    conn.execute(
        """
        UPDATE events
        SET
            title = ?,
            start_time = ?,
            end_time = ?,
            description = ?,
            location = ?
        WHERE id = ?
        """,
        (
            title if title is not None else current["title"],
            start_time if start_time is not None else current["start_time"],
            end_time if end_time is not None else current["end_time"],
            description if description is not None else current["description"],
            location if location is not None else current["location"],
            event_id,
        ),
    )

    conn.commit()
    conn.close()

    return event_id


def delete_event(
    event_id: int | None = None,
    title: str | None = None,
):
    conn = get_connection()

    if event_id is not None:
        cursor = conn.execute(
            """
            DELETE FROM events
            WHERE id = ?
            """,
            (event_id,),
        )

    elif title is not None:
        cursor = conn.execute(
            """
            DELETE FROM events
            WHERE LOWER(title) = LOWER(?)
            """,
            (title,),
        )

    else:
        conn.close()
        return False

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted
