-- Instrucciones recopiladas por el desarrollador, con ayuda de ChatGPT. 

-- dbo.PTLF_track: one row per source file (or per run)
CREATE TABLE dbo.PTLF_track (
    -- Identity of the file/run
    -- The date embedded in the file name (business date) and the original string
    data_date          VARCHAR(6)          NOT NULL,    -- Solía ser DATE_STR, Ver comentario 
    -- RAW load phase
    raw_status         VARCHAR(16)         NOT NULL DEFAULT 'pending',  
    -- OPS/transform phase
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



-- Cambiar definición del índice con nueva columna FILE_DUPLICATE

-- 2) Or by (file_name, file_size_bytes)
-- CREATE UNIQUE INDEX UX_PTLF_track_file ON dbo.PTLF_track(file_name, file_size_bytes);


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

-- YA NO ESTÁ EN SQLACODEGEN
ALTER TABLE dbo.PTLF_track
ADD CONSTRAINT UQ_PTLF_track_data_date UNIQUE (data_date); 
GO


-- If data_date is CHAR(6) NOT NULL:  ❌ No lo hemos corrido.  
-- STYLE 12:  YYMMDD
ALTER TABLE dbo.PTLF_track
ADD CONSTRAINT CK_track_data_date_valid
CHECK (TRY_CONVERT(date, data_date, 12) IS NOT NULL);