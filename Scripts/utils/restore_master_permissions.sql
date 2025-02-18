-- Ensure Master-Level Logins Exist
USE master;
GO

-- Ensure the ETOAuto Service Account Exists in Master
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'BPHCAD\ETOAuto')
    CREATE LOGIN [BPHCAD\ETOAuto] FROM WINDOWS;
ALTER SERVER ROLE sysadmin ADD MEMBER [BPHCAD\ETOAuto];
GRANT ALTER ANY LOGIN TO [BPHCAD\ETOAuto];
GRANT VIEW SERVER STATE TO [BPHCAD\ETOAuto];

-- Ensure Other Users Exist in Master
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'BPHCAD\CJeanty')
    CREATE LOGIN [BPHCAD\CJeanty] FROM WINDOWS;

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'BPHCAD\AMarkoe')
    CREATE LOGIN [BPHCAD\AMarkoe] FROM WINDOWS;

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'BPHCAD\KSchouten')
    CREATE LOGIN [BPHCAD\KSchouten] FROM WINDOWS;

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'BPHCAD\pkumar')
    CREATE LOGIN [BPHCAD\pkumar] FROM WINDOWS;

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'SQLETO')
    CREATE LOGIN [SQLETO] FROM WINDOWS;

-- Verify Master-Level Logins Were Restored
SELECT name, type_desc, create_date, is_disabled 
FROM sys.server_principals 
WHERE name IN ('BPHCAD\ETOAuto', 'BPHCAD\CJeanty', 'BPHCAD\AMarkoe', 'BPHCAD\KSchouten', 'BPHCAD\pkumar', 'SQLETO');
