
SELECT top 1000 * FROM PTLF_RAW; 
GO


-- EL QUERY MÁS FACIL 
SELECT file_name, date_file, n_records, data_date FROM PTLF_track
ORDER BY file_name
GO


-- N_RECORDS OK. 
SELECT t.file_name, 
  CONVERT(DATE, t.data_date, 12) as data_date, 
  t.n_records as n_meta, r.n_data, 
  'cargado' as estatus
FROM PTLF_track t
LEFT JOIN (SELECT
    [NGBBSE24-AUTH-POST-DAT] as date_str, 
  COUNT(*) as n_data
    FROM PTLF_raw 
    GROUP BY [NGBBSE24-AUTH-POST-DAT]
    ) r
ON t.data_date = r.date_str
--WHERE n_records <> n_rows
ORDER BY file_name DESC
GO


DELETE FROM PTLF_raw 
WHERE [NGBBSE24-AUTH-POST-DAT] in ('250904', '250603'); 
GO

DELETE FROM PTLF_track
WHERE data_date in ('250904', '250603'); 
GO 

-- Para encontrar las dependencias de DATE_STR. 
SELECT OBJECT_SCHEMA_NAME(referencing_id) AS schema_name,
       OBJECT_NAME(referencing_id)        AS object_name,
       referenced_entity_name             AS referenced_column
FROM sys.sql_expression_dependencies
WHERE referenced_id = OBJECT_ID('dbo.PTLF_track')
  AND referenced_minor_name = 'date_str';
GO


-- Para encontrar archivos en cuyas fechas en la data y en el título se corresponden:
SELECT * 
FROM dbo.PTLF_track
WHERE CONVERT(char(6), date_file, 12) = data_date; 

SELECT * 
FROM dbo.PTLF_track
WHERE TRYCONVERT(date, date_file, 12) = date_file; 
GO 



