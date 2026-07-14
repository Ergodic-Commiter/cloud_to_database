-- TRUNCATE TABLE dbo.PTLF_raw; 
TRUNCATE TABLE dbo.PTLF_raw; 

DELETE FROM dbo.PTLF_track;
DBCC CHECKIDENT ([dbo.PTLF_track], RESEED, 0);  

-- DELETE bad dates:
WITH bad_dates AS (
SELECT f_posteo, 
  k_positivos
FROM (
  SELECT f_posteo, 
    SUM(IIF(monto_txn > 0, 1, 0)) AS k_positivos
  FROM v_ptlf_token
  GROUP BY f_posteo) tt
WHERE k_positivos = 0)

DELETE r 
FROM [dbo].[PTLF_raw] AS r 
JOIN bad_dates AS b
  ON r.[NGBBSE24-AUTH-POST-DAT] = b.f_posteo 


DELETE t
FROM data_track AS t
LEFT JOIN data_raw AS r
  ON r.fecha = t.fecha
WHERE r.fecha IS NULL;