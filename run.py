import os

import pandas as pd

from common.parser import compile_raw_links
from common.utils import gather_email_statistics, logger
from mail_gathering import connect_to_email_server, create_dataframe


def main(overwrite=True):

    processed_data_dir = "processed_data"
    processed_data_file = os.path.join(processed_data_dir, "RAW_DATA.csv")

    os.makedirs(processed_data_dir, exist_ok=True)

    if os.path.exists(processed_data_file) and not overwrite:
        logger.info(f"Using existing processed data from {processed_data_file}")
        df = pd.read_csv(processed_data_file)
    else:
        logger.info(
            "No existing data found or overwrite requested. Processing emails..."
        )
        mail = connect_to_email_server()
        RAW_DATA = create_dataframe(mail, time_span=7)
        mail.logout()

    df = RAW_DATA.copy()
    df["links"] = df["message"].apply(compile_raw_links)

    df.to_csv(processed_data_file, index=False)

    logger.info(f"Processed data saved to {processed_data_file}")

    logger.info("Calculating email statistics...")
    gather_email_statistics(df).to_csv(
        os.path.join(processed_data_dir, "DATA_SUMMARY.csv"), index=False
    )

    logger.info("Processing complete.")


if __name__ == "__main__":
    main()
