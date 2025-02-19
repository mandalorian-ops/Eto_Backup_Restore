import logging
import os
import time
from utils.s3_utils import get_latest_s3_keys, download_file, extract_file, clear_old_backups
from utils.db_utils import (
    connect_to_database, restore_full_backup, restore_diff_backup, 
    wait_for_database, validate_backup_lsn
)

# ======================
# Required Functions Checklist
# 1. configure_logging() - Configures logging for the script
# 2. force_restore_mode(cursor, database_name, full_backup_path) - Ensures no active connections before transitioning to RESTORING mode
# 3. restore_database() - Orchestrates the database restoration process
# ======================

# Load configuration
backup_directory = "E:\\Eto_Backup_Restore\\Backups\\ETO"
log_file_path = "E:\\Eto_Backup_Restore\\Logs\\restore_process.log"
dsn = "DSN=ETO_DSN"
database_name = "ETO"
s3_bucket_name = "ssg-etobphc"

# 1 Configure Logging Function
def configure_logging():
    """
    Configures logging for the script.
    """
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging initialized successfully.")

# 2 Force Restore Mode Function
def force_restore_mode(cursor, database_name, full_backup_path):
    """
    Ensures no active connections exist before transitioning the database into RESTORING mode.
    If connections exist, they are forcibly terminated before proceeding.
    """
    try:
        logging.info(f"Checking if database {database_name} is stuck in SINGLE_USER mode...")

        for attempt in range(3):  # Retry up to 3 times
            cursor.execute(f"SELECT state_desc FROM sys.databases WHERE name = '{database_name}'")
            db_state = cursor.fetchone()[0]

            if db_state == "SINGLE_USER":
                logging.warning(f"Attempt {attempt + 1}/3: Database {database_name} is in SINGLE_USER mode but may have an active connection.")
                logging.info(f"Terminating all active connections before retrying SINGLE_USER mode...")

                # Fetch and kill all active session IDs for the database
                cursor.execute(f"SELECT spid FROM sys.sysprocesses WHERE dbid = DB_ID('{database_name}');")
                active_sessions = cursor.fetchall()

                for session in active_sessions:
                    spid = session[0]
                    logging.info(f"Killing session {spid}...")
                    cursor.execute(f"KILL {spid};")

                time.sleep(5)  # Allow SQL Server to process kill commands

            logging.info(f"Switching database {database_name} to SINGLE_USER mode for restore...")
            cursor.execute(f"ALTER DATABASE [{database_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;")
            time.sleep(2)

            print("Checkpoint 1")

            # Verify if SINGLE_USER mode was successfully set
            cursor.execute(f"SELECT state_desc FROM sys.databases WHERE name = '{database_name}'")
            new_state = cursor.fetchone()[0]
            if new_state == "SINGLE_USER":
                break  # Exit loop if successful

            print("Checkpoint 2") 

        # Restore database into RESTORING mode
        logging.info(f"Restoring FULL backup from {full_backup_path}...")
        cursor.execute(f"RESTORE DATABASE [{database_name}] FROM DISK = '{full_backup_path}' WITH NORECOVERY, REPLACE;")

        print("Checkpoint 3")

        # Ensure the database transitions correctly
        if not wait_for_database(cursor, database_name, expected_state="RESTORING"):
            raise RuntimeError(f"Database {database_name} did not transition to RESTORING state after FULL restore.")

        logging.info(f"Database {database_name} is now in RESTORING mode. Continuing restore process...")

    except Exception as e:
        logging.error(f"Failed to transition database into RESTORING mode: {e}")
        raise

# 3 Restore Database Function
def restore_database():
    """
    Main function to orchestrate the database restoration process.
    Automatically handles missing backups and ensures correct restore state.
    """
    try:
        logging.info("Starting the database restoration process...")
        clear_old_backups(backup_directory)

        # Connect to the database
        conn = connect_to_database(dsn)
        cursor = conn.cursor()

        # Check the database state
        logging.info("Checking database state...")
        cursor.execute(f"SELECT state_desc FROM sys.databases WHERE name = '{database_name}'")
        db_state = cursor.fetchone()[0]

        # If database is ONLINE, force it into RESTORING mode
        if db_state == "ONLINE":
            logging.warning(f"Database {database_name} is already ONLINE. Automatically forcing restore...")

            # Dynamically retrieve the latest FULL backup for restore
            latest_full_backup = get_latest_s3_keys(s3_bucket_name)[0]
            full_backup_path = os.path.join(backup_directory, os.path.basename(latest_full_backup))

            force_restore_mode(cursor, database_name, full_backup_path)

        elif db_state != "RESTORING":
            logging.error(f"Database {database_name} is in unexpected state: {db_state}. Restore cannot proceed.")
            raise RuntimeError(f"Database {database_name} is in an unexpected state: {db_state}. Reset it before running the restore.")

        # Get latest FULL and DIFF backup keys from S3 dynamically
        logging.info("Fetching latest backups from S3...")
        full_backup_key, diff_backup_keys = get_latest_s3_keys(s3_bucket_name)

        if not full_backup_key:
            logging.critical("No FULL backup found in S3! Restore process cannot continue.")
            raise RuntimeError("No FULL backup available in S3.")

        # Download and extract FULL backup dynamically
        full_backup_path = download_file(full_backup_key, os.path.join(backup_directory, os.path.basename(full_backup_key)))
        extracted_full_path = extract_file(full_backup_path, expected_type="FULL")

        # Identify LSN of the FULL backup
        logging.info(f"Identifying DifferentialBaseLSN of restored FULL backup...")
        differential_base_lsn = validate_backup_lsn(extracted_full_path, backup_type="FULL")

        # Match it with the correct DIFF backup
        valid_diff_backup = None
        for diff_backup_key in diff_backup_keys:
            extracted_diff_path = os.path.join(backup_directory, os.path.basename(diff_backup_key))
            first_lsn = validate_backup_lsn(extracted_diff_path, backup_type="DIFF")

            if first_lsn >= differential_base_lsn:
                valid_diff_backup = extracted_diff_path
                logging.info(f"Matching DIFF Backup Found: {valid_diff_backup} (FirstLSN: {first_lsn})")
                break

        if not valid_diff_backup:
            logging.critical("No matching DIFF backup found! Restore cannot continue.")
            raise RuntimeError("No matching DIFF backup found for the selected FULL backup.")

        # Restore FULL backup dynamically
        restore_full_backup(cursor, database_name, extracted_full_path)

        # Restore the valid DIFF backup dynamically
        restore_diff_backup(cursor, database_name, valid_diff_backup)

        # Finalize recovery
        logging.info("Finalizing database recovery...")
        cursor.execute(f"RESTORE DATABASE [{database_name}] WITH RECOVERY;")
        logging.info("Database restoration completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the restoration process: {e}")
        raise

if __name__ == "__main__":
    configure_logging()
    restore_database()
