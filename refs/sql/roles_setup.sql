-- #### 0. 
-- Identity Model:  Humans, Service Principal, with Azure Groups. 
-- Automation from Docker with Serv. Ppal. 
-- Check role strategy with Azure - SQL... (groups, Admin, etc). 


-- #### 1. Roles ✅
CREATE ROLE r_admin AUTHORIZATION dbo;
CREATE ROLE r_dev   AUTHORIZATION dbo;
CREATE ROLE r_ops   AUTHORIZATION dbo;
CREATE ROLE r_etl   AUTHORIZATION dbo;

-- ## Grant permissions. ✅
ALTER ROLE db_owner ADD MEMBER r_admin;

-- Optional: allow creating temp/dev objects in a dedicated schema
-- (recommended instead of letting devs create stuff under dbo) ✅
GO
CREATE SCHEMA dev AUTHORIZATION dbo;
GO


GRANT SELECT ON OBJECT::dbo.PTLF_ops TO r_dev;  --❌ (no hay tabla OPS todavía)
GRANT SELECT, INSERT, UPDATE ON OBJECT::dbo.PTLF_track TO r_dev; --✅
GRANT SELECT ON OBJECT::dbo.PTLF_raw TO r_dev;  -- ✅
GRANT SELECT ON OBJECT::dbo.PTLF_raw TO r_ops;  -- ✅
GRANT CREATE TABLE, CREATE VIEW, CREATE PROCEDURE TO r_dev;   -- ❌
GRANT ALTER ON SCHEMA::dev TO r_dev;    -- ❌

GRANT SELECT ON OBJECT::dbo.PTLF_ops   TO r_ops; -- ❌
DENY  SELECT ON OBJECT::dbo.PTLF_raw   TO r_ops; -- ❌
GRANT SELECT ON OBJECT::dbo.PTLF_track TO r_ops; -- ✅


GRANT SELECT, INSERT, UPDATE ON OBJECT::dbo.PTLF_track TO r_etl;
GRANT SELECT, INSERT         ON OBJECT::dbo.PTLF_ops   TO r_etl;
GRANT SELECT                 ON OBJECT::dbo.PTLF_raw   TO r_etl; -- read raw to transform

--Tip: For easier permissioning, consider moving tables into schemas by layer (e.g., stage.PTLF_raw, ops.PTLF_ops, meta.PTLF_track) and grant per-schema. For now I kept your dbo names.


-- ### Azure AD userts or groups by email. 

-- These names must match AAD display names or object names.
-- Si uso Cloud.Admin
-- ❌ : Only connections established with AD accounts can create other AD users.

-- Pero uso dumdv001: 
CREATE USER [dumdv001@bineo.com] FROM EXTERNAL PROVIDER;  -- ✅ 
CREATE USER [diego.v@bineo.com]  FROM EXTERNAL PROVIDER; -- ✅
CREATE USER [diego.villamil.pesqueira@banorte.com] FROM EXTERNAL PROVIDER; -- ❌
CREATE USER [ptlf-etl-sp] FROM EXTERNAL PROVIDER;   -- medios-pago-sp   ❌

ALTER ROLE r_admin ADD MEMBER [dumdv001@bineo];     -- ❌ 
ALTER ROLE r_dev   ADD MEMBER [diego.v@bineo.com];  -- ✅
ALTER ROLE r_etl   ADD MEMBER [ptlf-etl-sp];

CREATE USER [liliana.hernandez] WITH PASSWORD = 'Backtrack-Buckshot-Prorate';
ALTER ROLE r_ops ADD MEMBER [liliana.hernandez];  -- ❌
GRANT SELECT ON dbo.v_PTLF_Fraudes TO r_ops; 

-- ### 5. Sanity Checks. 
-- See who you are (login/user as seen by SQL)
SELECT SUSER_SNAME() AS login_name, USER_NAME() AS db_user;

-- List role membership
SELECT r.name AS role_name, m.name AS member_name
FROM sys.database_role_members drm
JOIN sys.database_principals r ON r.principal_id = drm.role_principal_id
JOIN sys.database_principals m ON m.principal_id = drm.member_principal_id
ORDER BY r.name, m.name;

-- See AAD users/groups in the DB
SELECT name, type_desc
FROM sys.database_principals
WHERE type_desc IN ('EXTERNAL_USER','EXTERNAL_GROUP')
ORDER BY type_desc, name;
