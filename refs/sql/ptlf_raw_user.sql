
-- create unique index ... 
-- create nonclustered index
-- alter table ... add constraint ... primary key clustered (...)
-- alter table ... add constraint ... foreign key (...) references 
-- alter table ... add ... persisted
-- alter table ... alter column 

-- begin tran update ... set ... where ... 
--     alter table ... alter column ... 
--     commit tran 



-- FOREIGN KEY a PTLF_TRACK  ✅
CREATE NONCLUSTERED INDEX IX_PTLX_raw_date_key 
	ON dbo.PTLF_raw([NGBBSE24-AUTH-POST-DAT]); 

ALTER TABLE dbo.PTLF_raw -- ✅
ADD CONSTRAINT FK_PTLF_raw_track
    FOREIGN KEY ([NGBBSE24-AUTH-POST-DAT]) REFERENCES dbo.PTLF_track([date_str]); 

-- LOOKUP BUCKETS: 
ALTER TABLE dbo.PTLF_raw
ADD member_prefix AS LEFT([NGBBSE24-HEAD-MBR-NUM], 6) PERSISTED, 
	member_bucket AS (ABS(CHECKSUM([NGBBSE24-HEAD-MBR-NUM])) % 256) PERSISTED; -- 256 buckets. 

CREATE NONCLUSTERED INDEX IX_PTLF_raw_member_prefix
ON dbo.PTLF_raw(member_prefix);


-- unique key, en caso de necesitar updates 
ALTER TABLE dbo.PTLF_raw
ADD row_id BIGINT IDENTITY(1,1) NOT NULL;

ALTER TABLE dbo.PTLF_raw
ADD CONSTRAINT PK_PTLF_raw PRIMARY KEY CLUSTERED (row_id);


-- Por TERMINAL, sólo si se llega a necesitar. 
-- Pero de hecho no es único, así que bye. ❌
CREATE UNIQUE INDEX UX_PTLF_terminal
ON dbo.PTLF_raw ([NGBBSE24-AUTH-POST-DAT], [NGBBSE24-HEAD-TERM-TERM-ID], [NGBBSE24-AUTH-SEQ-NUM]); 


-- Cambios a partir de la definición:  
-- S9(15)V99: Se tomó con 9 decimales, y se cambia por 2.  
-- 'NGBBSE24-AUTH-AMT-1'       'decimal.Decimal'
-- 'NGBBSE24-AUTH-AMT-2'       'decimal.Decimal'
BEGIN TRAN

-- 2) Fix scale: move decimal point 7 places to the RIGHT
UPDATE dbo.PTLF_raw
SET [NGBBSE24-AUTH-AMT-1] = ROUND([NGBBSE24-AUTH-AMT-1] * POWER(10.0, 7), 2)
WHERE [NGBBSE24-AUTH-AMT-1] IS NOT NULL;

UPDATE dbo.PTLF_raw
SET [NGBBSE24-AUTH-AMT-2] = ROUND([NGBBSE24-AUTH-AMT-2] * POWER(10.0, 7), 2)
WHERE [NGBBSE24-AUTH-AMT-2] IS NOT NULL;


ALTER TABLE dbo.PTLF_raw
ALTER COLUMN [NGBBSE24-AUTH-AMT-1] DECIMAL(17,2) NULL; 
ALTER TABLE dbo.PTLF_raw
ALTER COLUMN [NGBBSE24-AUTH-AMT-2] DECIMAL(17,2) NULL;  -- or NOT NULL if appropriate

COMMIT TRAN
GO;


ALTER TABLE [PTLF_raw] ALTER COLUMN 	[NGBBSE24-HEAD-RETL-ID] NVARCHAR(19) NULL;
ALTER TABLE [PTLF_raw] ALTER COLUMN 	[NGBBSE24-TKEY-RKEY-RTL-ID] NVARCHAR(19) NULL;
ALTER TABLE [PTLF_raw] ALTER COLUMN 	[NGBBSE24-AUTH-TERM-NAME-LOC] NVARCHAR(25) NULL;
ALTER TABLE [PTLF_raw] ALTER COLUMN 	[NGBBSE24-AUTH-TERM-OWNER-NAME] NVARCHAR(22) NULL;
ALTER TABLE [PTLF_raw] ALTER COLUMN 	[NGBBSE24-AUTH-TERM-CITY] NVARCHAR(13) NULL;
ALTER TABLE [PTLF_raw] ALTER COLUMN 	[NGBBSE24-AUTH-TRACK2] NVARCHAR(40) NULL;
ALTER TABLE [PTLF_raw] ALTER COLUMN 	[NGBBSE24-C0-TERM-POSTAL-CDE] NVARCHAR(10) NULL;
