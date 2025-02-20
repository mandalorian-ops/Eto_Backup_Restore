### **ETO Database Restore Process**  

This document provides an overview of the **ETO database restore process**, including project structure, configuration details, what works, known issues, and commands to troubleshoot or reset the environment. The purpose of this document is to transition ownership of the restore process to the data engineering team.  

---

## **Table of Contents**  
- [1. Overview](#1-overview)  
- [2. Project Structure](#2-project-structure)  
- [3. Configuration Details](#3-configuration-details)  
- [4. What Works](#4-what-works)  
- [5. Known Issues](#5-known-issues)  
- [6. Commands for Troubleshooting & Resetting](#6-commands-for-troubleshooting--resetting)  
- [7. Required Actions](#7-required-actions)  
- [8. Contact & Next Steps](#8-contact--next-steps)  

---

## **1. Overview**  
The **ETO database restore process** automates the full recovery of the database using the latest FULL and DIFF backups stored in AWS S3. The script performs the following operations:  
- **Download** the latest backups from S3  
- **Extract** and locate the correct `.bak` files  
- **Restore** the FULL backup with `WITH NORECOVERY`  
- **Restore** the DIFF backup with `WITH RECOVERY`  
- **Ensure** the database transitions to `ONLINE`  

Despite improvements, the process has encountered **technical limitations** related to SQL Server's rollforward requirements, preventing DIFF backups from being restored in certain cases.  

[Back to Top](#-readme-eto-database-restore-process)  

---

## **2. Project Structure**  
The project follows a structured organization for automation and logging.  

```
Eto_Backup_Restore/
│── Scripts/
│   ├── restore_script.py           # Main restore automation script
│   ├── utils/
│   │   ├── s3_utils.py             # Handles S3 file operations
│   │   ├── db_utils.py             # Contains restore functions for SQL Server
│── Backups/
│   ├── ETO/
│   │   ├── *.bak                   # Extracted FULL & DIFF backup files
│   │   ├── *.7z                    # Compressed backup archives from S3
│── Logs/
│   ├── restore_process.log         # Logs from the restore script
```
**Scripts are modular**, keeping database and S3 functions separate for better maintainability.  

[Back to Top](#-readme-eto-database-restore-process)  

---

## **3. Configuration Details**  
The following **configuration settings** are required for the restore process:  

### **🔹 Environment Variables**  
Run the following command to **check if required environment variables are set**:  
```powershell
echo $Env:ZIP_PASSWORD
echo $Env:AWS_ACCESS_KEY_ID
echo $Env:AWS_SECRET_ACCESS_KEY
echo $Env:AWS_DEFAULT_REGION
```
**Expected Output:**  
- If correctly set, the values should be displayed (except for sensitive credentials which may be masked).  
- If `ZIP_PASSWORD` is missing, the script will **fail to extract backups from `.7z` files**.  

### **🔹 Configuration in `restore_script.py`**
- **S3 Bucket Name:** `ssg-etobphc`  
- **Local Backup Directory:** `E:\Eto_Backup_Restore\Backups\ETO`  
- **Log File Location:** `E:\Eto_Backup_Restore\Logs\restore_process.log`  
- **SQL Server DSN (for authentication):** `DSN=ETO_DSN`  

[Back to Top](#-readme-eto-database-restore-process)  

---

## **4. What Works**  
The following components of the restore process are **fully functional and verified**:  

### **Database Detection & State Validation**  
- If the database **does not exist**, the script **automatically triggers a FULL restore**.  
- If the database is **already ONLINE**, the script **skips unnecessary restores** and exits gracefully.  
- If the database is **in RESTORING mode**, the script **continues the restore process**.  

### **Backup Selection & Download from S3**  
- The script correctly **fetches the latest FULL and DIFF backups** from S3.  
- **Existing backups are overwritten** to ensure the latest version is always used.  

### **Dynamic Extraction & File Selection**  
- The script **dynamically extracts and selects the correct FULL and DIFF `.bak` files**.  
- It **does not rely on static filenames**, ensuring compatibility with naming differences.  

[Back to Top](#-readme-eto-database-restore-process)  

---

## **5. Known Issues**  
While most of the restore process works as expected, the script encounters **issues related to SQL Server’s rollforward requirement**.  

### **DIFF Restore Failure Due to Rollforward Requirements**  
- **Issue:** The DIFF restore fails if the database is not in `RESTORING` mode after a FULL restore.  
- **SQL Error Message:**  
  ```
  The log or differential backup cannot be restored because no files are ready to rollforward. (3117)
  ```
- **Root Cause:**  
  - SQL Server **requires** a FULL restore to be completed with `WITH NORECOVERY` before a DIFF restore can be applied.  
  - If SQL Server **automatically transitions the database to ONLINE after a FULL restore**, the DIFF restore cannot be applied.  

[Back to Top](#-readme-eto-database-restore-process)  

---

## **6. Commands for Troubleshooting & Resetting**  

### **Check Current Database State**
```sql
SELECT name, state_desc FROM sys.databases WHERE name = 'ETO';
```
If `ONLINE`**, no restore is needed.  
If `RESTORING`**, the restore process is in progress.  

### **Drop & Recreate the Database for Testing**
```sql
USE master;
GO
ALTER DATABASE [ETO] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
GO
DROP DATABASE [ETO];
GO
```
Use this if you need to force the restore script to fully automate from scratch.**  

### **Verify Restore History**
```sql
SELECT TOP 5 destination_database_name, restore_date, restore_type 
FROM msdb.dbo.restorehistory 
WHERE destination_database_name = 'ETO' 
ORDER BY restore_date DESC;
```
Ensures the latest FULL and DIFF restores were applied.**  

[Back to Top](#-readme-eto-database-restore-process)  

---

## **7. Required Actions**  
### **Immediate Next Steps for Troubleshooting**
**Test Running the Restore Script from Scratch**  
- Drop the `ETO` database using the SQL commands above.  
- Run:
  ```powershell
  python restore_script.py
  ```
- Verify that the database is fully restored and transitions to `ONLINE`.  

Improve Handling of the Rollforward Requirement**  
- Modify the script to **force `WITH NORECOVERY` after a FULL restore** to ensure DIFF restores succeed.  

*Enhance Logging for SQL Errors**  
- Modify the script to **capture full SQL error messages** for better debugging.  

[Back to Top](#-readme-eto-database-restore-process)  

---

## **8. Contact & Next Steps**  
For any questions or troubleshooting, refer to:  
- **Restore Logs:** `E:\Eto_Backup_Restore\Logs\restore_process.log`  
- **SQL Commands for Troubleshooting:** See the [Technical Details](#6-commands-for-troubleshooting--resetting) section  
- **S3 Backup Source:** `ssg-etobphc`  

This document serves as the official handoff to ensure **a smooth transition and ongoing maintainability of the restore process**.  

[Back to Top](#-readme-eto-database-restore-process)  
