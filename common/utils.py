import os
import quopri

import pandas as pd
from loguru import logger

# Configure Loguru
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logger.add(
    os.path.join(log_dir, "application.log"),
    rotation="2 MB",
    retention="7 days",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


def decode_quoted_printable(encoded_string):
    return quopri.decodestring(encoded_string).decode("utf-8")


def gather_email_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gather summary statistics from email DataFrame and return as a structured DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing email data with columns:
            'Email ID', 'Sender Name', 'Sender Email', 'Subject', 'Received Time', 'Message'

    Returns:
        pd.DataFrame: DataFrame containing various statistics with following structure:
            - metric: Name of the statistic
            - value: Value of the statistic
            - category: Category of the statistic (e.g., 'general', 'temporal', 'sender')
    """
    return (
        df.groupby("sender_email")
        .agg(
            sender_name=("sender_name", lambda x: x.iloc[0]),
            n_of_mails=("sender_name", "size"),
            n_of_links=("links", lambda x: x.str.count(",").add(1).sum()),
            median_links_per_mail=("links", lambda x: x.str.count(",").add(1).median()),
        )
        .reset_index()[
            [
                "sender_name",
                "sender_email",
                "n_of_mails",
                "n_of_links",
                "median_links_per_mail",
            ]
        ]
        .sort_values(by="n_of_mails", ascending=False)
        .reset_index(drop=True)
    )
