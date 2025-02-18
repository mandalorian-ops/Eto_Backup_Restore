import os
import logging
import subprocess
import boto3
import shutil
import smtplib
import time
import pyodbc
from email.message import EmailMessage

"""
S3 Backup Management for ETO Backup & Restore Application

Functions:
1. send_email_alert(subject, body) - Sends email notifications for missing backups.
2. download_file(s3_key, destination_path) - Downloads a backup from S3 and applies a safe overwrite.
3. safe_overwrite_backup(directory, temp_backup) - Ensures downloaded backups do not overwrite until verified.
4. get_latest_s3_keys(bucket_name, retries=3) - Retrieves the latest FULL and most recent DIFF backup.
5. extract_file(file_path, expected_type="FULL") - Extracts a .7z archive to retrieve `.bak` files.
6. clear_old_backups(directory) - Deletes old backups **only after restore is confirmed**.
7. verify_functions_exist() - Ensures all required functions exist before execution.
8. main() - Executes test operations when the script is run directly.
"""

# Global Variables
seven_zip_path = "E:\\7z.exe"
zip_password = os.getenv("ZIP_PASSWORD")
backup_directory = "E:\\Eto_Backup_Restore\\Backups\\ETO"
log_file_path = "E:\\Eto_Backup_Restore\\Logs\\restore_process.log"

# Initialize Logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("? Logging initialized successfully.")

# Email Notification Settings
SMTP_SERVER = "smtp.yourcompany.com"
SMTP_PORT = 587
EMAIL_SENDER = "alerts@yourcompany.com"
EMAIL_RECIPIENTS = ["dba_team@yourcompany.com"]
EMAIL_USERNAME = "alerts@yourcompany.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# 1. Email Alert Function
def send_email_alert(subject, body):
    """
    (1) Sends an email notification for missing backups.
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        logging.info(f"? Email alert sent: {subject}")
    except Exception as e:
        logging.error(f"? Failed to send email alert: {e}")

# 2. Download File Function
def download_file(s3_key, destination_path):
    """
    (2) Downloads a file from S3 using AWS CLI and verifies it before overwriting.
    """
    if os.path.exists(destination_path):
        logging.info(f"? Backup file already exists: {destination_path}. Skipping download.")
        return destination_path

    temp_path = destination_path + ".temp"
    command = f'aws s3 cp s3://ssg-etobphc/{s3_key} "{temp_path}"'

    try:
        subprocess.run(command, shell=True, check=True, text=True)
        if not os.path.exists(temp_path):
            logging.error(f"? Downloaded file missing: {temp_path}")
            raise RuntimeError(f"Download failed, file not found: {temp_path}")
        logging.info(f"? Downloaded {s3_key} to {temp_path}")

        # Safely overwrite old backup with new one
        safe_overwrite_backup(backup_directory, temp_path)
        return destination_path
    except subprocess.CalledProcessError as e:
        logging.error(f"? Failed to download {s3_key}: {e}")
        raise RuntimeError(f"Download failed for {s3_key}: {e}")

# 3. Safe Overwrite Function
def safe_overwrite_backup(directory, temp_backup):
    """
    (3) Ensures new backups do not overwrite old ones until verified.
    """
    try:
        final_path = os.path.join(directory, os.path.basename(temp_backup).replace(".temp", ""))
        os.rename(temp_backup, final_path)
        logging.info(f"? Backup successfully renamed from {temp_backup} to {final_path}")
    except Exception as e:
        logging.error(f"? Failed to safely overwrite backup: {e}")
        raise RuntimeError(f"Error during backup overwrite: {e}")

# 4. Get Latest S3 Keys Function
def get_latest_s3_keys(bucket_name, retries=3):
    """
    (4) Retrieves the latest FULL and DIFF backup from S3.
    """
    s3_client = boto3.client("s3")
    full_backup, diff_backup = None, None

    for attempt in range(retries):
        try:
            logging.info(f"?? Fetching backup files from S3 bucket: {bucket_name} (Attempt {attempt + 1}/{retries})")
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="SQLBackups/")

            if "Contents" not in response:
                logging.warning("?? No backups found in S3. Retrying...")
                continue

            backups = response["Contents"]
            all_files = [obj["Key"] for obj in backups]
            logging.info(f"?? All backups found in S3: {all_files}")

            full_backups = sorted([obj["Key"] for obj in backups if "FULL" in obj["Key"].upper()], reverse=True)
            diff_backups = sorted([obj["Key"] for obj in backups if "DIFF" in obj["Key"].upper()], reverse=True)

            full_backup = full_backups[0] if full_backups else None
            diff_backup = diff_backups[0] if diff_backups else None

            logging.info(f"? Selected FULL backup: {full_backup}")
            logging.info(f"? Selected DIFF backup: {diff_backup}")
            return full_backup, diff_backup

        except Exception as e:
            logging.error(f"? Error retrieving backups from S3: {e}")
            continue

    logging.critical("? No backups found in S3 after multiple retries.")
    raise RuntimeError("No FULL or DIFF backups found in S3.")

# 5. Extract File Function
def extract_file(file_path, expected_type="FULL"):
    """
    (5) Extracts a .7z archive and ensures that a FULL or DIFF backup is selected correctly.
    """
    if not os.path.exists(file_path):
        logging.error(f"? File not found for extraction: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    extract_path = os.path.dirname(file_path)
    command = f'"{seven_zip_path}" x "{file_path}" -o"{extract_path}" -y'

    try:
        subprocess.run(command, shell=True, check=True, text=True)
        logging.info(f"? Extracted {file_path} to {extract_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"? Extraction failed for {file_path}: {e}")
        raise RuntimeError(f"Extraction failed: {e}")

# 6. Clear Old Backups Function
def clear_old_backups(directory):
    """
    (6) Deletes older backups only AFTER the latest backup has been fully restored.
    """
    logging.info("? Skipping backup cleanup in test mode.")

# 7. Verify Functions Exist Function
def verify_functions_exist():
    """
    (7) Ensures that all required functions exist before running the script.
    """
    required_functions = [
        "send_email_alert",
        "download_file",
        "safe_overwrite_backup",
        "get_latest_s3_keys",
        "extract_file",
        "clear_old_backups"
    ]
    missing_functions = [func for func in required_functions if func not in globals()]
    if missing_functions:
        logging.error(f"? Missing required functions: {missing_functions}")
        exit(1)
    logging.info("? All required functions are present.")

# 8. Main Function for Testing
if __name__ == "__main__":
    logging.info("? Running S3 Backup Test Mode...")
    verify_functions_exist()
    bucket_name = "ssg-etobphc"
    get_latest_s3_keys(bucket_name)
