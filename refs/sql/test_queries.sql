
-- ### Para buscar usuarios. 
SELECT name, type_desc, authentication_type_desc
FROM sys.database_principals
WHERE type IN ('S', 'E', 'X')  -- S = SQL user, E = External (AAD), X = external group
AND name NOT LIKE '##%';

-- ### Para crear un usuario, se usa más bien el nombre del Serv.Princ. 
-- ### Habría que hacer pruebas si con el Obj-ID. 
-- CREATE USER [medios-pago-data-dev] FROM EXTERNAL PROVIDER;
-- ALTER ROLE db_owner ADD MEMBER [medios-pago-data-dev];


-- DROP TABLE PTLF

-- ### El query lo dice todo. 
-- SELECT COUNT(*) AS column_count
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_SCHEMA = 'dbo'
--   AND TABLE_NAME = 'PTLF';

-- ### Este no necesita explicación
-- SELECT * from PTLF_raw

-- ## Este tampoco. 
-- TRUNCATE TABLE dbo.YourTable;

-- ## Cambiar el nombre de la tabla. 
-- EXEC sp_rename 'dbo.PTLF', 'PTLF_raw';


