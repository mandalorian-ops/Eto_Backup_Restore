import os
import configparser
import logging

"""
Configuration Utilities for ETO Backup & Restore Application

Functions:
1. load_config(): Loads configuration from `config.ini`.
2. test_config(): Prints and logs key configuration values for verification.
"""

# 1. Load configuration from `config.ini`
def load_config():
    """
    (1) Loads configuration from the specified config file.
    
    - Reads and parses `config.ini`.
    - Returns a dictionary of key configuration values.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "Config", "config.ini")

    if not os.path.exists(config_path):
        logging.error(f"? Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    config.read(config_path)
    return config

# 2. Function to test configuration loading
def test_config():
    """
    (2) Reads the configuration and prints/logs key values for verification.
    
    - Confirms critical values like backup directory, S3 bucket, and DSN.
    """
    config = load_config()

    backup_dir = config.get("Paths", "backup_directory", fallback="Not Set")
    s3_bucket = config.get("Paths", "s3_bucket_name", fallback="Not Set")
    dsn = config.get("Database", "dsn", fallback="Not Set")

    print("? Configuration Loaded Successfully!")
    print(f"Backup Directory: {backup_dir}")
    print(f"S3 Bucket: {s3_bucket}")
    print(f"DSN: {dsn}")

    logging.info("? Configuration Loaded Successfully!")
    logging.info(f"Backup Directory: {backup_dir}")
    logging.info(f"S3 Bucket: {s3_bucket}")
    logging.info(f"DSN: {dsn}")

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(filename="E:\\Eto_Backup_Restore\\Logs\\restore_process.log",
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    
    test_config()
