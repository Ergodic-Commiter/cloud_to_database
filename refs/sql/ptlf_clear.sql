-- TRUNCATE TABLE dbo.PTLF_raw; 
TRUNCATE TABLE dbo.PTLF_raw; 

DELETE FROM dbo.PTLF_track;
DBCC CHECKIDENT ([dbo.PTLF_track], RESEED, 0);  

-- Delete bad dates:
with bad_dates as (
select f_posteo, 
  k_positivos
from (
  select f_posteo, 
    sum(iif(monto_txn > 0, 1, 0)) as k_positivos
  from v_ptlf_token
  group by f_posteo) tt
where k_positivos = 0)

delete r 
from [dbo].[PTLF_raw] as r 
join bad_dates as b
  on r.[NGBBSE24-AUTH-POST-DAT] = b.f_posteo 


DELETE t
FROM data_track AS t
LEFT JOIN data_raw AS r
  ON r.fecha = t.fecha
WHERE r.fecha IS NULL;