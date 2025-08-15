-- Archivo generado por ChatGPT, para ayuda d

-- dbo.PTLF_track: one row per source file (or per run)
CREATE TABLE dbo.PTLF_track (
    track_id           BIGINT IDENTITY(1,1) PRIMARY KEY,
    -- Identity of the file/run
    file_name          NVARCHAR(260)       NOT NULL,      -- e.g. PTLF_20250814.txt
    file_path          NVARCHAR(1024)      NULL,          -- optional full/path
    file_size_bytes    BIGINT              NULL,
    file_hash_sha256   VARBINARY(32)       NULL,          -- compute in Python; prevents dup loads
    -- The date embedded in the file name (business date) and the original string
    date_str           NVARCHAR(32)        NULL,          -- original token (e.g. '2025-08-14')
    date_file          DATE                NULL,          -- parsed date if applicable
    -- RAW load phase
    raw_start          DATETIME2(0)        NULL,
    raw_complete       DATETIME2(0)        NULL,
    raw_status         VARCHAR(16)         NOT NULL DEFAULT 'pending',  -- 'pending'|'running'|'success'|'failed'
    n_records          INT                 NULL,          -- rows written to PTLF_raw
    raw_error          NVARCHAR(MAX)       NULL,
    -- OPS/transform phase
    ops_start          DATETIME2(0)        NULL,
    ops_complete       DATETIME2(0)        NULL,
    ops_status         VARCHAR(16)         NOT NULL DEFAULT 'pending',  -- 'pending'|'running'|'success'|'failed'
    inserted_rows      INT                 NULL,
    updated_rows       INT                 NULL,
    rejected_rows      INT                 NULL,
    ops_error          NVARCHAR(MAX)       NULL,
    -- Audit
    created_at         DATETIME2(0)        NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at         DATETIME2(0)        NOT NULL DEFAULT SYSUTCDATETIME(),
    -- Optional: who/what ran it
    run_by             NVARCHAR(128)       NULL,
    run_host           NVARCHAR(128)       NULL
);
GO

-- Keep statuses constrained
ALTER TABLE dbo.PTLF_track WITH CHECK ADD
    CONSTRAINT CK_PTLF_track_raw_status
    CHECK (raw_status IN ('pending','running','success','failed')),
    CONSTRAINT CK_PTLF_track_ops_status
    CHECK (ops_status IN ('pending','running','success','failed'));
GO

-- Sanity constraints on timestamps
ALTER TABLE dbo.PTLF_track WITH CHECK ADD
    CONSTRAINT CK_PTLF_track_raw_time
    CHECK (raw_complete IS NULL OR raw_start IS NULL OR raw_complete >= raw_start),
    CONSTRAINT CK_PTLF_track_ops_time
    CHECK (ops_complete IS NULL OR ops_start IS NULL OR ops_complete >= ops_start);
GO

-- Unique-ness: pick ONE of these based on how you identify a file
-- 1) Strongest: hash (if you compute it)
CREATE UNIQUE INDEX UX_PTLF_track_hash
    ON dbo.PTLF_track (file_hash_sha256)
    WHERE file_hash_sha256 IS NOT NULL;
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
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE t
    SET updated_at = SYSUTCDATETIME()
    FROM dbo.PTLF_track t
    JOIN inserted i ON i.track_id = t.track_id;
END
GO