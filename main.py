# Import necessary functions from mail_gathering.py and mail_parser.py
from mail_gathering import connect_to_email_server, create_dataframe
from mail_parser import apply_and_print_caution

def main():
    # Connect to the email server
    mail = connect_to_email_server()

    # Create the DataFrame
    df_unprocessed = create_dataframe(mail)

    # Close the connection to the email server
    mail.logout()

    df = df_unprocessed.copy()
    df = df[df['Link'].notna()].reset_index(drop=True)

    # Apply parsing and caution function to create the subset DataFrame
    subset_df = df.groupby('Email ID', group_keys=False).apply(apply_and_print_caution).reset_index(drop=True)

    # You can further process or save the subset_df as needed

if __name__ == "__main__":
    main()
