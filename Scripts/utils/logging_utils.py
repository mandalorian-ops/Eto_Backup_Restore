import logging
import os

"""
Logging Utilities for ETO Backup & Restore Application

Functions:
1. setup_logging(log_file_path): Initializes logging and ensures logs are written to the specified file.
2. test_logging(): Writes a test log entry to verify that logging is functional.
"""

# 1. Initialize logging and ensure logs are written
def setup_logging(log_file_path):
    """
    (1) Sets up logging configuration.

    - Creates the log directory if it does not exist.
    - Configures logging to write logs to the specified file.
    - Logs an initialization message.
    """
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Logging initialized successfully.")

# 2. Function to test logging functionality
def test_logging():
    """
    (2) Writes a test log entry to verify logging functionality.

    - Prints confirmation to the console.
    - Logs a test message to confirm logging works.
    """
    print("Testing logging system...")
    logging.info("Test log entry: Logging is working correctly.")
    print(f"? Log entry written to log file.")

# Example Usage
if __name__ == "__main__":
    setup_logging("E:\\Eto_Backup_Restore\\Logs\\restore_process.log")  # (1)
    test_logging()  # (2)
