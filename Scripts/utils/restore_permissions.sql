-- Restore User Permissions on ETO
USE ETO;
GO

-- Christherson Jeanty
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\CJeanty')
    CREATE USER [BPHCAD\CJeanty] FOR LOGIN [BPHCAD\CJeanty];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\CJeanty];
GRANT VIEW DEFINITION TO [BPHCAD\CJeanty];

-- Alicia Markoe
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\AMarkoe')
    CREATE USER [BPHCAD\AMarkoe] FOR LOGIN [BPHCAD\AMarkoe];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\AMarkoe];
GRANT VIEW DEFINITION TO [BPHCAD\AMarkoe];

-- Keenan Schouten
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\KSchouten')
    CREATE USER [BPHCAD\KSchouten] FOR LOGIN [BPHCAD\KSchouten];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\KSchouten];
GRANT VIEW DEFINITION TO [BPHCAD\KSchouten];

-- Preeti Kumar
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\pkumar')
    CREATE USER [BPHCAD\pkumar] FOR LOGIN [BPHCAD\pkumar];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\pkumar];
GRANT VIEW DEFINITION TO [BPHCAD\pkumar];

-- Service Account
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'SQLETO')
    CREATE USER [SQLETO] FOR LOGIN [SQLETO];
ALTER ROLE db_datareader ADD MEMBER [SQLETO];
GRANT VIEW DEFINITION TO [SQLETO];

-- ETOAuto Service Account (Ensure Full Access)
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\ETOAuto')
    CREATE USER [BPHCAD\ETOAuto] FOR LOGIN [BPHCAD\ETOAuto];
ALTER ROLE db_owner ADD MEMBER [BPHCAD\ETOAuto];
GRANT EXECUTE TO [BPHCAD\ETOAuto];
GRANT SELECT, INSERT, UPDATE, DELETE TO [BPHCAD\ETOAuto];

-- Restore User Permissions on ETOHSS
USE ETOHSS;
GO

-- Repeat for ETOHSS
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\CJeanty')
    CREATE USER [BPHCAD\CJeanty] FOR LOGIN [BPHCAD\CJeanty];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\CJeanty];
GRANT VIEW DEFINITION TO [BPHCAD\CJeanty];

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\AMarkoe')
    CREATE USER [BPHCAD\AMarkoe] FOR LOGIN [BPHCAD\AMarkoe];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\AMarkoe];
GRANT VIEW DEFINITION TO [BPHCAD\AMarkoe];

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\KSchouten')
    CREATE USER [BPHCAD\KSchouten] FOR LOGIN [BPHCAD\KSchouten];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\KSchouten];
GRANT VIEW DEFINITION TO [BPHCAD\KSchouten];

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\pkumar')
    CREATE USER [BPHCAD\pkumar] FOR LOGIN [BPHCAD\pkumar];
ALTER ROLE db_datareader ADD MEMBER [BPHCAD\pkumar];
GRANT VIEW DEFINITION TO [BPHCAD\pkumar];

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'SQLETO')
    CREATE USER [SQLETO] FOR LOGIN [SQLETO];
ALTER ROLE db_datareader ADD MEMBER [SQLETO];
GRANT VIEW DEFINITION TO [SQLETO];

-- ETOAuto Service Account (Ensure Full Access in ETOHSS)
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'BPHCAD\ETOAuto')
    CREATE USER [BPHCAD\ETOAuto] FOR LOGIN [BPHCAD\ETOAuto];
ALTER ROLE db_owner ADD MEMBER [BPHCAD\ETOAuto];
GRANT EXECUTE TO [BPHCAD\ETOAuto];
GRANT SELECT, INSERT, UPDATE, DELETE TO [BPHCAD\ETOAuto];

-- Verify that permissions were applied correctly
SELECT sp.name AS UserName, sp.type_desc AS UserType, sp.create_date, sp.modify_date,
       dp.permission_name, dp.state_desc, dp.class_desc
FROM sys.database_principals sp
LEFT JOIN sys.database_permissions dp ON sp.principal_id = dp.grantee_principal_id
WHERE sp.name IN ('BPHCAD\ETOAuto', 'BPHCAD\CJeanty', 'BPHCAD\AMarkoe', 'BPHCAD\KSchouten', 'BPHCAD\pkumar', 'SQLETO');
