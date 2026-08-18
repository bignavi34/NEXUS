import imaplib
import smtplib
import ssl
from email import message_from_bytes
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path

from app.config.settings import (
    EMAIL_ADDRESS,
    EMAIL_APP_PASSWORD,
)


IMAP_HOST = "imap.gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def _imap_connect():
    mail = imaplib.IMAP4_SSL(IMAP_HOST)

    mail.login(
        EMAIL_ADDRESS,
        EMAIL_APP_PASSWORD,
    )

    return mail


def _extract_body(msg):
    if msg.is_multipart():

        for part in msg.walk():

            content_type = part.get_content_type()

            if content_type == "text/plain":

                try:
                    return part.get_payload(
                        decode=True
                    ).decode(
                        part.get_content_charset()
                        or "utf-8",
                        errors="replace",
                    )

                except Exception:
                    continue

        return ""

    try:
        return msg.get_payload(
            decode=True
        ).decode(
            msg.get_content_charset()
            or "utf-8",
            errors="replace",
        )

    except Exception:
        return str(msg.get_payload())


def list_emails(limit: int = 10):

    mail = _imap_connect()

    try:

        mail.select("INBOX")

        status, data = mail.search(
            None,
            "ALL",
        )

        if status != "OK":
            return []

        email_ids = data[0].split()

        email_ids = email_ids[-limit:]

        results = []

        for email_id in reversed(email_ids):

            status, msg_data = mail.fetch(
                email_id,
                "(RFC822)",
            )

            if status != "OK":
                continue

            raw_email = msg_data[0][1]

            msg = message_from_bytes(raw_email)

            results.append(
                {
                    "id": int(email_id),
                    "from": msg.get("From", ""),
                    "to": msg.get("To", ""),
                    "subject": msg.get(
                        "Subject",
                        "",
                    ),
                    "date": msg.get(
                        "Date",
                        "",
                    ),
                }
            )

        return results

    finally:

        mail.logout()


def read_email(email_id: int):

    mail = _imap_connect()

    try:

        mail.select("INBOX")

        status, msg_data = mail.fetch(
            str(email_id),
            "(RFC822)",
        )

        if status != "OK":
            return None

        raw_email = msg_data[0][1]

        msg = message_from_bytes(raw_email)

        return {
            "id": email_id,
            "from": msg.get("From", ""),
            "to": msg.get("To", ""),
            "subject": msg.get(
                "Subject",
                "",
            ),
            "date": msg.get(
                "Date",
                "",
            ),
            "body": _extract_body(msg),
        }

    finally:

        mail.logout()


def search_emails(query: str, limit: int = 10):

    mail = _imap_connect()

    try:

        mail.select("INBOX")

        status, data = mail.search(
            None,
            f'TEXT "{query}"',
        )

        if status != "OK":
            return []

        email_ids = data[0].split()

        email_ids = email_ids[-limit:]

        results = []

        for email_id in reversed(email_ids):

            status, msg_data = mail.fetch(
                email_id,
                "(RFC822)",
            )

            if status != "OK":
                continue

            msg = message_from_bytes(
                msg_data[0][1]
            )

            results.append(
                {
                    "id": int(email_id),
                    "from": msg.get("From", ""),
                    "subject": msg.get(
                        "Subject",
                        "",
                    ),
                    "date": msg.get(
                        "Date",
                        "",
                    ),
                }
            )

        return results

    finally:

        mail.logout()


def send_email(
    to: str,
    subject: str,
    body: str,
):

    msg = EmailMessage()

    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to
    msg["Subject"] = subject

    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        SMTP_HOST,
        SMTP_PORT,
        context=context,
    ) as smtp:

        smtp.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD,
        )

        smtp.send_message(msg)

    return True


def reply_email(
    email_id: int,
    body: str,
):

    original = read_email(email_id)

    if not original:
        raise ValueError(
            "Email not found."
        )

    sender = parseaddr(
        original["from"]
    )[1]

    subject = original["subject"]

    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    send_email(
        to=sender,
        subject=subject,
        body=body,
    )

    return True
