import imaplib
import email
from email.header import decode_header
import os
import time
import asyncio
from multi_tool_agent.agent import call_agent_async
from dotenv import load_dotenv

# Load environment variables from .env file
print("Loading environment variables from .env file...")
load_dotenv()

# CONFIGURATION using .env variables
USERNAME = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
POLLING_INTERVAL = 30  # seconds
DESIRED_SUBJECT = "My Special Trigger"  # Change as needed

if not USERNAME or not PASSWORD or not IMAP_SERVER:
    print("Error: One or more environment variables are missing. Please check your .env file.")
    exit(1)

# Global variable to hold the initial max UID, so only new emails are processed.
INITIAL_MAX_UID = None

async def trigger_function(email_message, pdf_contents):
    """
    Custom function triggered when an email with the specified subject and PDF attachments is received.
    - email_message: email.message.Message object representing the full email.
    - pdf_contents: list of tuples (filename, pdf_data_bytes).
    """
    print(">>> Trigger function called!")
    # Print Email Subject
    subject = email_message.get("Subject")
    print("Email subject:", subject)
    
    # Extract and print email content (preferring plain text)
    print("\n--- Email Content Start ---")
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            # skip any attachments
            if content_type == "text/plain" and "attachment" not in content_disposition.lower():
                try:
                    body = part.get_payload(decode=True)
                    print(body.decode("utf-8"))
                except Exception as e:
                    print("Error decoding email content:", e)
    else:
        try:
            body = email_message.get_payload(decode=True)
            print(body.decode("utf-8"))
        except Exception as e:
            print("Error decoding email content:", e)
    print("--- Email Content End ---\n")
    
    download_dir = r"C:\Users\madha\Downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    # Print PDF attachments info.
    print("Number of PDF attachments:", len(pdf_contents))
    saved_file_path = []
    
    for filename, pdf_data in pdf_contents:
        file_path = os.path.join(download_dir, filename)
        with open(file_path, "wb") as f:
            f.write(pdf_data)
            
        print(f"Attachment '{filename}' has been saved.")
        saved_file_path.append(file_path)
        print(f"Attachment saved to: {file_path}")
        
        if file_path:
            print("Calling agent with PDF path...")
            response = await call_agent_async(f"parse the path:{file_path}")
            print("\n--- Agent Response ---")
            print(response)
            print("--- End Agent Response ---\n")
    
    return saved_file_path

def decode_str(s):
    """Helper function to decode email header fields."""
    if s is None:
        return ""
    decoded_bytes, encoding = decode_header(s)[0]
    if isinstance(decoded_bytes, bytes):
        try:
            return decoded_bytes.decode(encoding if encoding else "utf-8")
        except Exception as e:
            print("Error decoding header:", e)
            return decoded_bytes.decode("utf-8", errors="replace")
    return decoded_bytes

def get_initial_max_uid(mail):
    """Retrieve the highest UID in the inbox and set the INITIAL_MAX_UID global variable."""
    print("Fetching initial maximum UID to process only new emails...")
    result, data = mail.uid("search", None, "ALL")
    if result != "OK":
        print("Error fetching UIDs. Processing all emails may occur.")
        return 0
    uid_list = data[0].split()
    if not uid_list:
        print("No emails found in the mailbox.")
        return 0
    max_uid = max(int(uid.decode()) if isinstance(uid, bytes) else int(uid) for uid in uid_list)
    print("Initial maximum UID:", max_uid)
    return max_uid

async def process_mailbox(mail, last_seen_uid):
    """
    Search the mailbox for unseen messages with UID greater than last_seen_uid
    that match the specified subject.
    """
    print("Searching for new unseen emails (UID greater than {})...".format(last_seen_uid))
    # Use UID search to process only new messages.
    result, messages = mail.uid("search", None, f"UNSEEN UID {last_seen_uid + 1}:*")
    if result != "OK":
        print("Error: Unable to search the mailbox.")
        return last_seen_uid

    uid_list = messages[0].split()
    if not uid_list:
        print("No new unseen messages found.")
        return last_seen_uid

    print(f"Found {len(uid_list)} new unseen message(s).")
    current_max_uid = last_seen_uid

    for uid in uid_list:
        uid_int = int(uid.decode() if isinstance(uid, bytes) else uid)
        if uid_int > current_max_uid:
            current_max_uid = uid_int

        print("\nProcessing message with UID:", uid_int)
        result, data = mail.uid("fetch", uid, "(RFC822)")
        if result != "OK":
            print(f"ERROR: Could not fetch message UID {uid_int}.")
            continue

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = decode_str(msg.get("Subject"))
        print("Email subject:", subject)
        if subject != DESIRED_SUBJECT:
            print("Subject does not match. Skipping this email.")
            mail.uid("store", uid, '+FLAGS', '\\Seen')
            continue

        # Look for PDF attachments.
        pdf_contents = []
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            content_disposition = part.get("Content-Disposition")
            if content_disposition and "attachment" in content_disposition.lower():
                filename = part.get_filename()
                if filename:
                    filename = decode_str(filename)
                    if filename.lower().endswith(".pdf"):
                        pdf_data = part.get_payload(decode=True)
                        pdf_contents.append((filename, pdf_data))
                        print(f"PDF attachment found: {filename}")

        if pdf_contents:
            print("PDF attachments found. Calling trigger function.")
            # Wait for the trigger function to complete
            await trigger_function(msg, pdf_contents)
        else:
            print("Email matched the subject but no PDF attachments were found.")
        
        # Mark this email as seen to avoid processing it again.
        mail.uid("store", uid, '+FLAGS', '\\Seen')
        print("Marked message UID {} as seen.".format(uid_int))

    return current_max_uid

async def main_async():
    global INITIAL_MAX_UID
    while True:
        print("\n--- Starting new polling cycle ---")
        try:
            print("Connecting to IMAP server...")
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            print("Logging in as:", USERNAME)
            mail.login(USERNAME, PASSWORD)
            print("Selecting INBOX...")
            mail.select("inbox")

            # On first cycle, get the initial max UID so that only newer messages are processed.
            if INITIAL_MAX_UID is None:
                INITIAL_MAX_UID = get_initial_max_uid(mail)

            # Process mailbox and update the current maximum UID if new messages arrive.
            INITIAL_MAX_UID = await process_mailbox(mail, INITIAL_MAX_UID)
            print("Logging out...")
            mail.logout()
        except Exception as e:
            print("Error during polling cycle:", e)
        
        print(f"Waiting {POLLING_INTERVAL} seconds before next check...\n")
        await asyncio.sleep(POLLING_INTERVAL)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()