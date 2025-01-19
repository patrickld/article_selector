import email
import imaplib
from datetime import datetime, timedelta

import pandas as pd

from common.parser import parse_raw_message
from common.utils import logger
from config import EMAIL_HOST, EMAIL_PASSWORD, EMAIL_PORT, EMAIL_USERNAME


def connect_to_email_server() -> imaplib.IMAP4_SSL | None:
    """
    Establishes a secure SSL connection to an email server using credentials from config.

    Uses EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME and EMAIL_PASSWORD from config file
    to create an IMAP4 SSL connection and authenticate.

    Returns:
        imaplib.IMAP4_SSL: Connected and authenticated IMAP mail object if successful
        None: If connection or authentication fails

    Logs success or failure via logger.
    """
    try:
        mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
        mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        logger.info("Connected to the email server successfully.")
        return mail
    except Exception as e:
        logger.info(f"Error connecting to the email server: {e}")
        return None


def create_dataframe(
    mail: imaplib.IMAP4_SSL, label: str = "test", time_span: int = 7
) -> pd.DataFrame:
    """
    Creates a DataFrame containing email data from the specified label and time period.

    Args:
        mail (imaplib.IMAP4_SSL): Connected and authenticated IMAP mail object
        label (str, optional): Email label/folder to search. Defaults to "test". If None, searches inbox.
        time_span (int, optional): Number of days to look back for emails. Defaults to 7.

    Returns:
        pd.DataFrame: DataFrame containing email data with columns:
            - Email ID: The decoded email ID
            - Sender Name: The sender's display name
            - Sender Email: The sender's email address
            - Subject: The email subject line
            - Received Time: The email received timestamp
            - Message: The email body as a string

    Raises:
        Exception: If unable to access the specified label
        Exception: If error occurs while searching emails
    """
    search_date = (datetime.now() - timedelta(days=time_span)).strftime("%d-%b-%Y")
    if label:
        status, data = mail.select(label)
        if status != "OK":
            raise Exception(
                f"Unable to access label '{label}'. Check if the label exists."
            )
        try:
            status, email_ids = mail.search(
                None, f'(SINCE "{search_date}")'
            )  # mail.search(None, "ALL")
        except Exception as e:
            logger.error(f"Error searching emails for label '{label}': {e}")
            raise e
    else:
        mail.select("inbox")
        status, email_ids = mail.search(None, "ALL")

    email_ids = email_ids[0].split()
    df = pd.DataFrame(
        columns=[
            "email_id",
            "sender_name",
            "sender_email",
            "subject",
            "received_time",
            "message",
        ]
    )

    for email_id in email_ids:
        status, data = mail.fetch(
            email_id, "(RFC822)"
        )  # RFC822 is the standard format of the email
        if status != "OK":
            logger.error(f"Error when processing email {email_id}, status: {status}")
            continue

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        df = pd.concat([df, parse_raw_message(msg, email_id)], ignore_index=True)

    return df