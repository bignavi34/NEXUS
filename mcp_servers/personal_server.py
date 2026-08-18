import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from app.calendar.database import (
    initialize_database,
    create_event as db_create_event,
    list_events as db_list_events,
    get_event as db_get_event,
    update_event as db_update_event,
    delete_event as db_delete_event,
)
initialize_database()
from app.filesystem.files import (
    list_files as fs_list_files,
    read_file as fs_read_file,
    create_file as fs_create_file,
    update_file as fs_update_file,
    delete_file as fs_delete_file,
    search_files as fs_search_files,
)
from app.email.client import (
    list_emails as email_list,
    read_email as email_read,
    search_emails as email_search,
    send_email as email_send,
    reply_email as email_reply,
)
# ---------------------------------------------------------
# Make project root importable when MCP launches this file
# directly.
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from mcp.server.fastmcp import FastMCP

from app.memory.database import (
    initialize_database,
    create_task as db_create_task,
    list_tasks as db_list_tasks,
    complete_task as db_complete_task,
)


# ---------------------------------------------------------
# MCP SERVER
# ---------------------------------------------------------

mcp = FastMCP(
    "NEXUS Personal Server"
)


# ---------------------------------------------------------
# STARTUP
# ---------------------------------------------------------

initialize_database()


# ---------------------------------------------------------
# TIME TOOL
# ---------------------------------------------------------

@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time in India."""

    now = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return now.strftime(
        "%Y-%m-%d %H:%M:%S IST"
    )


# ---------------------------------------------------------
# CREATE TASK
# ---------------------------------------------------------

@mcp.tool()
def create_task(title: str) -> str:
    """Create a new personal task."""

    task_id = db_create_task(title)

    return (
        f"Task created successfully. "
        f"Task ID: {task_id}. "
        f"Title: {title}."
    )


# ---------------------------------------------------------
# LIST TASKS
# ---------------------------------------------------------

@mcp.tool()
def list_tasks() -> str:
    """List all personal tasks."""

    tasks = db_list_tasks()

    if not tasks:
        return "No tasks found."

    lines = []

    for task in tasks:
        lines.append(
            f"ID: {task['id']} | "
            f"Title: {task['title']} | "
            f"Completed: {task['completed']}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------
# COMPLETE TASK
# ---------------------------------------------------------

@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a personal task as completed."""

    success = db_complete_task(task_id)

    if success:
        return (
            f"Task {task_id} completed successfully."
        )

    return (
        f"Task {task_id} was not found."
    )
@mcp.tool()
def create_event(
    title: str,
    start_time: str,
    end_time: str = "",
    description: str = "",
    location: str = "",
) -> str:
    """
    Create a calendar event.

    start_time and end_time should be ISO-style datetime strings,
    for example: 2026-08-20 10:00.
    """

    event_id = db_create_event(
        title=title,
        start_time=start_time,
        end_time=end_time or None,
        description=description or None,
        location=location or None,
    )

    return (
        f"Event created successfully. "
        f"Event ID: {event_id}. "
        f"Title: {title}."
    )


@mcp.tool()
def list_events() -> str:
    """
    List all calendar events.
    """

    events = db_list_events()

    if not events:
        return "No calendar events found."

    output = []

    for event in events:
        item = (
            f"ID: {event['id']}\n"
            f"Title: {event['title']}\n"
            f"Start: {event['start_time']}\n"
            f"End: {event['end_time'] or 'N/A'}\n"
            f"Location: {event['location'] or 'N/A'}"
        )

        if event["description"]:
            item += f"\nDescription: {event['description']}"

        output.append(item)

    return "\n\n".join(output)


@mcp.tool()
def get_event(event_id: int) -> str:
    """
    Get a calendar event by ID.
    """

    event = db_get_event(event_id)

    if event is None:
        return f"Event {event_id} not found."

    return (
        f"ID: {event['id']}\n"
        f"Title: {event['title']}\n"
        f"Start: {event['start_time']}\n"
        f"End: {event['end_time'] or 'N/A'}\n"
        f"Location: {event['location'] or 'N/A'}\n"
        f"Description: {event['description'] or 'N/A'}"
    )


@mcp.tool()
def update_event(
    event_id: int,
    title: str = "",
    start_time: str = "",
    end_time: str = "",
    description: str = "",
    location: str = "",
) -> str:
    """
    Update an existing calendar event.
    """

    result = db_update_event(
        event_id=event_id,
        title=title or None,
        start_time=start_time or None,
        end_time=end_time or None,
        description=description or None,
        location=location or None,
    )

    if result is None:
        return f"Event {event_id} not found."

    return f"Event {event_id} updated successfully."

@mcp.tool()
def delete_event(
    event_id: int = 0,
    title: str = "",
) -> str:
    """
    Delete a calendar event.

    Use event_id when the ID is known.
    Otherwise use the exact event title.
    """

    if event_id > 0:

        deleted = db_delete_event(
            event_id=event_id
        )

        if not deleted:
            return f"Event {event_id} not found."

        return f"Event {event_id} deleted successfully."

    if title:

        deleted = db_delete_event(
            title=title
        )

        if not deleted:
            return f'Event "{title}" not found.'

        return f'Event "{title}" deleted successfully.'

    return "Please provide an event ID or event title."

# ---------------------------------------------------------
@mcp.tool()
def list_files(path: str = ".") -> str:
    """
    List files and directories inside the NEXUS workspace.
    """

    try:
        files = fs_list_files(path)

        if not files:
            return "The directory is empty."

        return "\n".join(files)

    except Exception as e:
        return f"Unable to list files: {e}"
@mcp.tool()
def read_file(path: str) -> str:
    """
    Read a text file from the NEXUS workspace.
    """

    try:
        content = fs_read_file(path)

        return (
            f"Contents of {path}:\n\n"
            f"{content}"
        )

    except Exception as e:
        return f"Unable to read file: {e}"
@mcp.tool()
def create_file(
    path: str,
    content: str,
) -> str:
    """
    Create a new text file inside the NEXUS workspace.
    """

    try:
        created = fs_create_file(
            path,
            content,
        )

        return (
            f"File created successfully: "
            f"{created}"
        )

    except Exception as e:
        return f"Unable to create file: {e}"
@mcp.tool()
def update_file(
    path: str,
    content: str,
) -> str:
    """
    Replace the contents of an existing text file.
    """

    try:
        updated = fs_update_file(
            path,
            content,
        )

        return (
            f"File updated successfully: "
            f"{updated}"
        )

    except Exception as e:
        return f"Unable to update file: {e}"
@mcp.tool()
def delete_file(path: str) -> str:
    """
    Delete a file from the NEXUS workspace.
    """

    try:
        fs_delete_file(path)

        return (
            f"File deleted successfully: {path}"
        )

    except Exception as e:
        return f"Unable to delete file: {e}"
@mcp.tool()
def search_files(query: str) -> str:
    """
    Search for text inside files in the NEXUS workspace.
    """

    try:
        results = fs_search_files(query)

        if not results:
            return (
                f'No files contain "{query}".'
            )

        return (
            f'Files containing "{query}":\n'
            + "\n".join(
                f"- {path}"
                for path in results
            )
        )

    except Exception as e:
        return f"Unable to search files: {e}"
@mcp.tool()
def list_emails(limit: int = 10) -> str:
    """
    List recent emails from the inbox.
    """

    try:

        emails = email_list(limit)

        if not emails:
            return "No emails found."

        output = []

        for email in emails:

            output.append(
                f"ID: {email['id']}\n"
                f"From: {email['from']}\n"
                f"Subject: {email['subject']}\n"
                f"Date: {email['date']}"
            )

        return "\n\n".join(output)

    except Exception as e:

        return f"Unable to list emails: {e}"
@mcp.tool()
def read_email(email_id: int) -> str:
    """
    Read a specific email using its email ID.
    """

    try:

        email = email_read(email_id)

        if not email:
            return "Email not found."

        return (
            f"From: {email['from']}\n"
            f"To: {email['to']}\n"
            f"Subject: {email['subject']}\n"
            f"Date: {email['date']}\n\n"
            f"{email['body']}"
        )

    except Exception as e:

        return f"Unable to read email: {e}"
@mcp.tool()
def search_emails(
    query: str,
    limit: int = 10,
) -> str:
    """
    Search emails by text.
    """

    try:

        emails = email_search(
            query,
            limit,
        )

        if not emails:
            return (
                f'No emails found for "{query}".'
            )

        output = []

        for email in emails:

            output.append(
                f"ID: {email['id']}\n"
                f"From: {email['from']}\n"
                f"Subject: {email['subject']}\n"
                f"Date: {email['date']}"
            )

        return "\n\n".join(output)

    except Exception as e:

        return f"Unable to search emails: {e}"
@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
) -> str:
    """
    Send an email.
    """

    try:

        email_send(
            to=to,
            subject=subject,
            body=body,
        )

        return (
            f"Email sent successfully to {to}."
        )

    except Exception as e:

        return f"Unable to send email: {e}"
@mcp.tool()
def reply_email(
    email_id: int,
    body: str,
) -> str:
    """
    Reply to an existing email.
    """

    try:

        email_reply(
            email_id=email_id,
            body=body,
        )

        return (
            f"Reply sent successfully "
            f"to email {email_id}."
        )

    except Exception as e:

        return f"Unable to reply to email: {e}"
if __name__ == "__main__":
    mcp.run(transport="stdio")

