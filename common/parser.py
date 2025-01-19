import email
import email.message
import re

import pandas as pd


def parse_raw_message(msg: email.message.Message, email_id: str) -> pd.DataFrame:
    """
    Parse a raw email message into a pandas DataFrame with key email metadata.

    Args:
        msg (email.message.Message): The raw email message to parse
        email_id (str): The ID of the email message

    Returns:
        DataFrame: A single-row DataFrame containing the parsed email metadata with columns:
            - Email ID: The decoded email ID
            - Sender Name: The sender's display name
            - Sender Email: The sender's email address
            - Subject: The email subject line
            - Received Time: The email received timestamp
            - Message: The email body as a string
    """
    sender_name, sender_email = email.utils.parseaddr(msg.get("From"))
    subject = msg.get("Subject", "No Subject")
    received_time = msg.get("Date")

    body = extract_email_body(msg)

    return pd.DataFrame(
        [
            {
                "email_id": email_id.decode(),
                "sender_name": sender_name,
                "sender_email": sender_email,
                "subject": subject,
                "received_time": received_time,
                "message": body,
            }
        ]
    )


def extract_email_body(msg: email.message.Message) -> str:
    """
    Extract the body of an email message.

    Args:
        msg (email.message.Message): The email message object.

    Returns:
        str: The extracted email body as a string.
    """
    if msg.is_multipart():
        # Walk through parts of the email
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
            elif (
                content_type == "text/html" and "attachment" not in content_disposition
            ):
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        # Non-multipart email
        return msg.get_payload(decode=True).decode("utf-8", errors="ignore")

    return ""


def compile_raw_links(message: str) -> list:
    """
    Extract all links from a message string and return them as a list.

    Args:
        message (str): The message text to extract links from

    Returns:
        list: A list of extracted URLs
    """
    if not isinstance(message, str):
        return []

    # Split message into lines and clean up
    lines = message.split("\r\n")

    # More specific URL pattern that handles parentheses
    url_pattern = r"(?:https?://[^\s\(\)]+|(?<=\()[^\s\(\)]+(?=\)))"

    urls = []
    for line in lines:
        # Remove leading/trailing parentheses and whitespace
        line = line.strip("() \t")

        # Find all URLs in the line
        found_urls = re.findall(url_pattern, line)
        urls.extend(found_urls)

    # Normalize URLs
    normalized_urls = []
    for url in urls:
        # Remove any remaining parentheses
        url = url.strip("()")

        # Add http:// prefix if missing
        if not url.startswith(("http://", "https://")):
            if url.startswith("www."):
                url = "http://" + url
            else:
                continue  # Skip non-URL strings

        normalized_urls.append(url)

    # Remove duplicates while preserving order
    unique_urls = list(dict.fromkeys(normalized_urls))

    # Filter out tracking/redirect URLs (optional)
    filtered_urls = [
        url
        for url in unique_urls
        if not any(
            tracker in url.lower()
            for tracker in ["convertkit-mail2.com", "click.convertkit", "unsubscribe"]
        )
    ]

    return filtered_urls