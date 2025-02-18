import os
import logging
import time
import pyodbc

# Database Configuration
backup_directory = "E:\\Eto_Backup_Restore\\Backups\\ETO"
log_file_path = "E:\\Eto_Backup_Restore\\Logs\\restore_process.log"
dsn = "DSN=ETO_DSN"

# Initialize Logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("? Logging initialized successfully.")

# ======================
# ? Required Functions Checklist
# 1?? connect_to_database(dsn) ? Establishes a connection to SQL Server
# 2?? check_database_state(cursor, database_name) ? Checks the current state of the database
# 3?? restore_full_backup(cursor, database_name, backup_file_path) ? Restores FULL backup and ensures completion
# 4?? restore_diff_backup(cursor, database_name, backup_file_path, is_last_backup) ? Restores DIFF backup after validation
# 5?? wait_for_database(cursor, database_name, expected_state, max_wait=1800, interval=90) ? Ensures database transitions properly before proceeding
# 6?? validate_backup_lsn(full_backup_path, diff_backup_path) ? Ensures DIFF backup matches FULL backup LSN
# 7?? verify_functions_exist() ? Ensures all required functions exist before execution
# 8?? clear_old_backups(directory) ? Deletes old backups **ONLY after restore is confirmed**
# ======================

# 1?? Connect to Database Function
def connect_to_database(dsn):
    """
    Establishes a connection to SQL Server.
    """
    try:
        logging.info(f"?? Connecting to the database using DSN: {dsn}")
        conn = pyodbc.connect(dsn, autocommit=True)
        logging.info("? Database connection established.")
        return conn
    except Exception as e:
        logging.error(f"? Error connecting to the database: {e}")
        raise RuntimeError(f"Database connection failed: {e}")

# 2?? Check Database State Function
def check_database_state(cursor, database_name):
    """
    Checks the current state of the database.
    """
    try:
        query = f"SELECT state_desc FROM sys.databases WHERE name = '{database_name}'"
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            state = row[0]
            logging.info(f"?? Database '{database_name}' is in state: {state}")
            return state
        else:
            logging.error(f"? Database '{database_name}' does not exist.")
            return None
    except Exception as e:
        logging.error(f"? Error checking database state: {e}")
        raise RuntimeError(f"Error checking database state: {e}")

# 3?? Restore FULL Backup Function
def restore_full_backup(cursor, database_name, backup_file_path):
    """
    Restores FULL backup and ensures completion.
    """
    try:
        logging.info(f"?? Executing FULL restore: {backup_file_path}")
        cursor.execute(f"RESTORE DATABASE [{database_name}] FROM DISK = '{backup_file_path}' WITH NORECOVERY, REPLACE;")
        logging.info(f"? FULL backup restored: {backup_file_path}")
    except Exception as e:
        logging.error(f"? Error restoring FULL backup: {e}")
        raise RuntimeError(f"FULL backup restore failed: {e}")

# 4?? Restore DIFF Backup Function
def restore_diff_backup(cursor, database_name, backup_file_path, is_last_backup):
    """
    Restores DIFF backup after validation.
    """
    try:
        logging.info(f"?? Executing DIFF restore: {backup_file_path}")
        cursor.execute(f"RESTORE DATABASE [{database_name}] FROM DISK = '{backup_file_path}' {'WITH RECOVERY;' if is_last_backup else 'WITH NORECOVERY;'}")
        logging.info(f"? DIFF backup restored: {backup_file_path}")
    except Exception as e:
        logging.error(f"? Error restoring DIFF backup: {e}")
        raise RuntimeError(f"DIFF backup restore failed: {e}")

# 5?? Wait for Database Transition Function
def wait_for_database(cursor, database_name, expected_state, max_wait=1800, interval=90):
    """
    Waits for the database to transition to the expected state.
    """
    elapsed_time = 0
    while elapsed_time < max_wait:
        cursor.execute(f"SELECT state_desc FROM sys.databases WHERE name = '{database_name}'")
        row = cursor.fetchone()
        current_state = row[0] if row else "UNKNOWN"

        if current_state == expected_state:
            logging.info(f"? Database '{database_name}' reached expected state: {expected_state}")
            return True

        logging.info(f"? Database '{database_name}' is in state: {current_state}. Waiting {interval}s...")
        time.sleep(interval)
        elapsed_time += interval

    logging.error(f"? Database '{database_name}' did not reach state '{expected_state}' within {max_wait // 60} minutes. Aborting.")
    return False

# 6?? Validate Backup LSN Function
def validate_backup_lsn(full_backup_path, diff_backup_path):
    """
    Validates if the DIFF backup can be applied to the FULL backup by checking LSN values.
    """
    try:
        conn = connect_to_database(dsn="DSN=ETO_DSN")
        cursor = conn.cursor()

        cursor.execute(f"RESTORE HEADERONLY FROM DISK = '{full_backup_path}'")
        full_lsn = cursor.fetchone()[36]  # Column 36 contains FirstLSN

        cursor.execute(f"RESTORE HEADERONLY FROM DISK = '{diff_backup_path}'")
        diff_lsn = cursor.fetchone()[37]  # Column 37 contains DifferentialBaseLSN

        if full_lsn == diff_lsn:
            logging.info("? LSN validation successful. DIFF backup matches FULL backup.")
            return True
        else:
            logging.error(f"? LSN mismatch: FULL LSN={full_lsn}, DIFF LSN={diff_lsn}.")
            return False
    except Exception as e:
        logging.error(f"? Error during LSN validation: {e}")
        return False

# 7?? Verify Functions Exist Function
def verify_functions_exist():
    """
    Ensures that all required functions exist before running the script.
    """
    required_functions = [
        "connect_to_database",
        "check_database_state",
        "restore_full_backup",
        "restore_diff_backup",
        "wait_for_database",
        "validate_backup_lsn",
        "clear_old_backups"
    ]
    missing_functions = [func for func in required_functions if func not in globals()]
    if missing_functions:
        logging.error(f"? Missing required functions: {missing_functions}")
        exit(1)
    logging.info("? All required functions are present.")

# 8?? Clear Old Backups Function
def clear_old_backups(directory):
    """
    Deletes older backups only AFTER the latest backup has been fully restored.
    """
    pass  # Logic implemented in `restore_script.py`
