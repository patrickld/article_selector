# Article Selector
The "Article Selector" is a Python-based tool designed to streamline the process of curating and delivering newsletters containing top-selected articles. This README provides an overview of the tool's functionalities and the code snippets utilized to achieve them.

## Planned Approach
1. Newsletter Selection
Start by selecting a set of newsletters (initially around 20).
2. Proof of Concept (POC)
2.1 Create Mail Account, Signup & Receive Newsletters
Set up a mail account, sign up for newsletters, and receive sample newsletters for testing.
2.2 Parse Newsletters for Article Links
Implement parsing logic to extract article links from received newsletters.
2.3 Create Database for Timeframe
Establish a database structure to store curated articles within a specified timeframe. The database should include attributes like newsletter name, date, link ID, links, journal name, and paywall information.
2.4 Bucketize Weekly and Select Top Articles
Organize articles by week and select the top articles based on predefined criteria.
2.5 Create Newsletter Template
Develop a newsletter template that can be populated with the selected articles.
2.6 Send Newsletter to Your Mail Account
Automate the process of sending the newsletter, filled with the top 5 selected links, to your designated mail account.
## Code Snippets
1. Create a DataFrame from Email Content (IMAP Retrieval)
File: create_dataframe_imap.py
Description: This code snippet demonstrates how to create a pandas DataFrame from email content using IMAP retrieval. It connects to an email server, retrieves emails, and extracts information such as email ID, sender name, sender email, subject, received time, and links from email messages.
2. Process Email Links and Append to CSV
File: process_and_append_to_csv.py
Description: This code snippet extends the DataFrame creation by processing email links. It applies a process_links function to each link, performs URL validation, checks for duplicate links, and extracts the final URL. Processed links are then appended to an existing CSV file or created in a new one.
3. Limit Rows per Email ID and Apply Process Links
File: limit_rows_and_apply_process_links.py
Description: This code snippet limits the number of rows per Email ID group to a specified limit. It also applies the process_links function to each link in the limited subset of rows while preserving the original DataFrame structure.
4. Improved Process Links Function
File: improved_process_links_function.py
Description: This code snippet refines the process_links function by addressing issues related to unique link tracking across rows within a group. It ensures that the unique_links set and final_links list are initialized outside the function to correctly process and replace links.
5. Error Handling in Process Links Function
File: error_handling_in_process_links.py
Description: This code snippet enhances the process_links function by adding a try-except block to catch errors during URL validation. It provides the flexibility to handle specific exceptions and print error messages when validation issues arise.
## Requirements
Python 3.x
pandas library
imaplib library (for IMAP email retrieval)
Other dependencies specific to your email parsing and link processing implementation
## Usage
Start by selecting a set of newsletters for your curation process.

Implement the planned approach, including setting up a mail account, parsing newsletters, and curating articles.

Integrate the provided code snippets into your workflow, customizing them as needed for your specific use case.

Run the code within your Python environment.

Utilize the "Article Selector" tool to streamline the process of curating and delivering newsletters containing top-selected articles.

Note
These code snippets serve as examples and may require additional customization based on your specific email data and processing logic.

