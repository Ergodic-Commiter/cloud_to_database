-- Instrucciones recopiladas por el desarrollador, con ayuda de ChatGPT. 

-- dbo.PTLF_track: one row per source file (or per run)
CREATE TABLE dbo.PTLF_track (
    track_id           BIGINT IDENTITY(1,1) PRIMARY KEY,
    -- Identity of the file/run
    file_name          NVARCHAR(260)       NOT NULL,    -- e.g. PTLF_20250814.txt
    file_path          NVARCHAR(1024)      NULL,        -- optional full/path
    file_size          BIGINT              NULL,
    file_hash          CHAR(80)            NULL,        -- compute in Python; prevents dup loads
    -- The date embedded in the file name (business date) and the original string
    data_date          VARCHAR(6)          NOT NULL,    -- Solía ser DATE_STR, Ver comentario 
    date_file          DATE                NOT NULL,       -- date form filename
    n_records          INT                 NULL,
    -- RAW load phase
    raw_start          DATETIME2(0)        NULL,
    raw_finish         DATETIME2(0)        NULL,        -- 'pending'|'running'|'success'|'failed'
    raw_status         VARCHAR(16)         NOT NULL DEFAULT 'pending',  
    -- OPS/transform phase
    ops_start          DATETIME2(0)        NULL,
    ops_finish         DATETIME2(0)        NULL,        -- 'pending'|'running'|'success'|'failed'
    ops_status         VARCHAR(16)         NOT NULL DEFAULT 'pending',  
    -- Audit
    created_at         DATETIME2(0)        NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at         DATETIME2(0)        NOT NULL DEFAULT SYSUTCDATETIME(),
);
-- antes pasamos de FILE_NAME a DATE_FILE a DATE_STR y todas eran iguales. 
-- como se hace match con POSTING_DATE y no siempre corresponden, cambiamos
-- DATE_STR a DATA_DATE.  
-- con eso también podemos rapidamente explorar las que matchean y las que no. 
GO

-- Keep statuses constrained
ALTER TABLE dbo.PTLF_track WITH CHECK ADD
    CONSTRAINT CK_PTLF_track_raw_status
    CHECK (raw_status IN ('pending', 'running', 'success', 'failed')),
    CONSTRAINT CK_PTLF_track_ops_status
    CHECK (ops_status IN ('pending', 'running', 'success', 'failed'));
GO

-- Sanity constraints on timestamps
ALTER TABLE dbo.PTLF_track WITH CHECK ADD
    CONSTRAINT CK_PTLF_track_raw_time
    CHECK (raw_finish IS NULL OR raw_start IS NULL OR raw_complete >= raw_start),
    CONSTRAINT CK_PTLF_track_ops_time
    CHECK (ops_finish IS NULL OR ops_start IS NULL OR ops_complete >= ops_start);
GO

-- Unique-ness: pick ONE of these based on how you identify a file
-- 1) Strongest: hash (if you compute it)
CREATE UNIQUE INDEX UX_PTLF_track_hash
    ON dbo.PTLF_track (file_hash)
    WHERE file_hash IS NOT NULL;

-- Cambiar definición del índice con nueva columna FILE_DUPLICATE



-- 2) Or by (file_name, file_size_bytes)
-- CREATE UNIQUE INDEX UX_PTLF_track_file ON dbo.PTLF_track(file_name, file_size_bytes);

-- Helpful filters & lookups
CREATE INDEX IX_PTLF_track_date ON dbo.PTLF_track(date_file);
CREATE INDEX IX_PTLF_track_raw_status ON dbo.PTLF_track(raw_status);
CREATE INDEX IX_PTLF_track_ops_status ON dbo.PTLF_track(ops_status);
GO

-- Keep updated_at fresh
CREATE TRIGGER dbo.trg_PTLF_track_touch
ON dbo.PTLF_track
AFTER UPDATE AS
BEGIN
    SET NOCOUNT ON;
    UPDATE t
    SET updated_at = SYSUTCDATETIME()
    FROM dbo.PTLF_track t
    JOIN inserted i 
    ON i.track_id = t.track_id;
END
GO

-- Round 2:  Agregar DATE_STR para KEY con PTLF_RAW

-- Quitamos esta porque hay muchos archivos que no. 
-- UPDATE dbo.PTLF_track  
-- SET date_str = CONVERT(char(6), date_file, 12); 

-- No está renombrada, pero la cambiamos nominalmente. 
ALTER TABLE dbo.PTLF_track
ADD CONSTRAINT UQ_PTLF_track_data_date UNIQUE (data_date); 
GO

-- ✅ Round3: Ajustar DATE_STR -> DATA_DATE, y mantener FILE_DATE a partir de FILE_NAME. 

ALTER TABLE dbo.PTLF_track
ADD CONSTRAINT CK_PTLF_track_data_date_YYMMDD
CHECK (data_date LIKE '[0-9][0-9][0-9][0-9][0-9][0-9]');

-- Assumes last 10 chars are 'YYYY_MM_DD'
SELECT file_name,
    TRY_CONVERT(date, REPLACE(RIGHT(file_name, 10), '_','-'), 120) AS computed_file_date
FROM dbo.PTLF_track
WHERE TRY_CONVERT(date, REPLACE(RIGHT(file_name, 10), '_','-'), 120) IS NULL;
GO

--- 3.1 Safer SWAP (no downtime on reads)
-- If any rows appear, fix those filenames before proceeding.
BEGIN TRAN;

-- 1) Add a computed column (new name temporarily) 
-- ❌ más complicado recordarlo, que calcularlo cada vez. 
ALTER TABLE dbo.PTLF_track
ADD file_date_from_name AS (
    CONVERT(date, RIGHT([file_name], 10), 23)
) PERSISTED;
GO

-- 2) Optional: check current stored file_date agrees
SELECT file_name, date_file, data_date
FROM dbo.PTLF_track
WHERE date_file IS NOT NULL
  AND date_file <> CONVERT(date, RIGHT([file_name], 10), 23);
GO 

-- ✅ If mismatches > 0, decide if you want to overwrite or inspect:
UPDATE dbo.PTLF_track 
SET date_file = CONVERT(date, RIGHT([file_name], 10), 23);
GO

-- 3) Drop anything depending on old file_date (indexes/constraints) if they exist
-- Example:
-- DROP INDEX IX_track_file_date ON dbo.PTLF_track;

-- 5) Recreate any dropped indexes on the (now computed) file_date if needed
-- CREATE INDEX IX_track_file_date ON dbo.PTLF_track(file_date);
COMMIT;
GO

-- AJUSTAR LA COLUMNA file_date. ❌ en esas andamos. 
UPDATE t
SET date_file = v.new_date
FROM dbo.PTLF_track AS t
CROSS APPLY (
  SELECT TRY_CONVERT(date, RIGHT(t.file_name, 10), 23)
) AS v(new_date)
WHERE v.new_date IS NOT NULL
  AND (t.date_file IS NULL OR t.date_file <> v.new_date);

-- If data_date is CHAR(6) NOT NULL:  ❌ No lo hemos corrido.  
-- STYLE 12:  YYMMDD
ALTER TABLE dbo.PTLF_track
ADD CONSTRAINT CK_track_data_date_valid
CHECK (TRY_CONVERT(date, data_date, 12) IS NOT NULL);