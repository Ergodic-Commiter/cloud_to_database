
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



WITH k(num_tarjeta, f_posteo, num_autorizacion, monto_txn, tipo_auth) 
  AS (SELECT * FROM (VALUES 
    ('000540208T1521N4947',CAST('2025-10-24' AS date),'003457',CAST(214.48 AS decimal(19,2)),CAST(210 AS int))
    ) v(num_tarjeta, f_posteo, num_autorizacion, monto_txn, tipo_auth))
SELECT t.*
FROM dbo.v_PTLF_Token AS t
JOIN k
  ON t.num_tarjeta = k.num_tarjeta
  AND t.f_posteo = k.f_posteo
  AND t.num_autorizacion = k.num_autorizacion
  AND t.monto_txn = k.monto_txn
  AND t.tipo_auth = k.tipo_auth



SELECT t.* 
FROM dbo.v_PTLF_Token AS t 
JOIN (VALUES 
    ('000540208T1521N4947',CAST('2025-10-24' AS date),'003457',CAST(214.48 AS decimal(19,2)),CAST(210 AS int))
    ) AS k(num_tarjeta, f_posteo, num_autorizacion, monto_txn, tipo_auth)
  ON  t.num_tarjeta = k.num_tarjeta
  AND t.f_posteo = k.f_posteo
  AND t.num_autorizacion = k.num_autorizacion
  AND t.monto_txn = k.monto_txn
  AND t.tipo_auth = k.tipo_auth