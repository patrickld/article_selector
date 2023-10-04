import requests
import urllib.parse
import html2text
from difflib import SequenceMatcher
import re
import pandas as pd  # Assuming you're using pandas for DataFrame operations


# Function to check if a URL is accessible and return the final URL
def get_final_url(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            return response.url
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        pass
    return None


# Function to calculate similarity between two URLs using SequenceMatcher
def url_similarity(url1, url2):
    return SequenceMatcher(None, url1, url2).ratio()


# Function to check similarity between two URLs
def check_similarity(link1, link2):
    similarity = url_similarity(link1, link2)
    return similarity > 0.95


# Function to convert HTML to plain text
def html_to_text(link):
    h = html2text.HTML2Text()
    h.ignore_links = False  # Preserve URLs in the HTML content
    parsed_link = urllib.parse.urlparse(link)

    if not parsed_link.scheme:
        link = "http://" + link

    return h.handle(link).strip()


# Function to parse and clean URLs
def remove_url_params(url):
    parsed_url = urllib.parse.urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path
    query = urllib.parse.urlencode([(k, v) for k, v in urllib.parse.parse_qsl(parsed_url.query) if not k.startswith('utm_')])
    fragment = parsed_url.fragment
    return urllib.parse.urlunparse((scheme, netloc, path, '', query, fragment))

# Define the process_links function
def process_links(link):
    unique_links = set()
    final_links = []

    try:
        # Check if the link is a valid URL
        if re.match(r'https?://\S+', link):
            # Convert HTML to plain text
            plain_text_link = html_to_text(link)

            # Check for similarity with existing unique links
            is_duplicate = any(check_similarity(link, unique_link) for unique_link in unique_links)

            if not is_duplicate:
                unique_links.add(link)
                final_link = get_final_url(link)
                if final_link:
                    final_link = remove_url_params(final_link)
                    final_links.append(final_link)
    except Exception as e:
        # Handle the specific error(s) that may occur during URL validation
        print(f"An error occurred during URL validation: {e}")
        # You can choose to return None or handle the error differently here

    return final_links[0] if final_links else None


def apply_and_print_caution(group, limit = 50):
    processed_rows = 0

    for index, row in group.iterrows():
        link = row['Link']
        processed_link = process_links(link)

        if processed_link:
            group.at[index, 'Link'] = processed_link
            processed_rows += 1

            if processed_rows >= limit:
                break

    if len(group) > limit:
        print(f"Caution: Only the first {limit} rows for Email ID {group['Email ID'].iloc[0]} have been transformed.")

    return group.head(limit)
