import imaplib
import email
from bs4 import BeautifulSoup
import pandas as pd
import re
from email.utils import parsedate_to_datetime
import quopri
import urllib.parse
import config

# Define your email account settings
EMAIL_HOST = config.EMAIL_HOST
EMAIL_PORT = config.EMAIL_PORT
EMAIL_USERNAME = config.EMAIL_USERNAME
EMAIL_PASSWORD = config.EMAIL_PASSWORD

def decode_quoted_printable(encoded_string):
    return quopri.decodestring(encoded_string).decode('utf-8')


def extract_links_from_email(email_message):
    links = []
    email_content = ""

    for part in email_message.walk():
        content_type = part.get_content_type()
        payload = part.get_payload(decode=True)

        if payload is not None:
            payload = payload.decode('utf-8')

        if content_type == "text/html":
            soup = BeautifulSoup(payload, 'html.parser')
            links.extend([a['href'] for a in soup.find_all('a', href=True)])
        elif content_type == "text/plain":
            email_content += payload

    urls = re.findall(r'(https?://\S+|\bwww\.\S+\.\w+\b|\b\S+\.\w+\b)', email_content)
    urls = [url if url.startswith(('http://', 'https://')) else f'http://{url}' for url in urls]

    links.extend(urls)
    return links


# Create a connection to the email server
def connect_to_email_server():
    try:
        mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
        mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("Connected to the email server successfully.")
        return mail
    except Exception as e:
        print(f"Error connecting to the email server: {e}")
        return None


# Create a DataFrame from email content
def create_dataframe(mail, mailbox='inbox'):
    # Select the mailbox you want to analyze (e.g., 'inbox')
    mail.select(mailbox)

    # Search for emails that match specific criteria (e.g., unread emails)
    status, email_ids = mail.search(None, 'ALL')

    columns = ['Email ID', 'Sender Name', 'Sender Email', 'Subject', 'Received Time', 'Link']
    df = pd.DataFrame(columns=columns)

    # Create an empty list to store DataFrames for each email
    dfs = []

    # Create a set to store unique links per email
    unique_links = set()

    # Loop through the email IDs
    for email_id in email_ids[0].split():
        if email_id.decode('utf-8') in ['40','41','42']: #== '5':
            # Getting mail content, decoding it to string, and storing it as an object
            status, email_data = mail.fetch(email_id, '(RFC822)')
            raw_email = email_data[0][1].decode('utf-8')
            email_message = email.message_from_string(raw_email)

            # Extract subject and received time
            subject = decode_quoted_printable(email_message['subject'])
            received_time = parsedate_to_datetime(email_message['date'])

            # Extract the sender's name from the "From" field
            sender_name, sender_email = email.utils.parseaddr(email_message['from'])

            # Extract links from the email
            links = extract_links_from_email(email_message)

            # Add links to the DataFrame
            if links:
                link_dicts = [{'Email ID': email_id.decode('utf-8'), 'Sender Name': sender_name, 'Sender Email': sender_email, 'Subject': subject, 'Received Time': received_time, 'Link': link} for link in links]
                df = pd.DataFrame(link_dicts)
                dfs.append(df)

    # Concatenate all DataFrames into a single DataFrame
    df = pd.concat(dfs, ignore_index=True)
    return df
