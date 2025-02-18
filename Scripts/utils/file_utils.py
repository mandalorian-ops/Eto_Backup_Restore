import shutil
import logging
import os

# Ensure logging is set up
log_file_path = "E:\\Eto_Backup_Restore\\Logs\\restore_process.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def check_disk_space(directory, min_free_space_gb):
    """
    Checks if there is enough free space in the given directory.
    Raises an error if free space is below `min_free_space_gb` GB.
    """
    total, used, free = shutil.disk_usage(directory)
    free_gb = free // (2**30)  # Convert bytes to GB

    if free_gb < min_free_space_gb:
        logging.error(f"? Not enough disk space! Only {free_gb}GB free, but {min_free_space_gb}GB required.")
        raise RuntimeError(f"Not enough disk space: {free_gb}GB available, {min_free_space_gb}GB required.")
    
    logging.info(f"Sufficient disk space: {free_gb}GB free.")
    print(f"Sufficient disk space: {free_gb}GB free.")  # Ensures immediate feedback

# Example Usage
if __name__ == "__main__":
    check_disk_space("E:\\", 10)
