# Email_Assistant/src/main.py

import time
from controllers.email_controller import process_emails


def main():
    while True:
        print("Checking for new emails...")
        process_emails()
        print("Waiting 60 seconds...")
        time.sleep(60)


if __name__ == "__main__":
    main()
