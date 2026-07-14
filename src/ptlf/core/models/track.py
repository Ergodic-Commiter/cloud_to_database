from datetime import datetime as dt, date

import sqlalchemy as alq
from sqlalchemy import orm
from sqlalchemy.dialects import mssql

from .base import Base


class PTLFTrack(Base):
    __tablename__ = "PTLF_track"
    __table_args__ = (
        alq.PrimaryKeyConstraint("track_id", name="PK__PTLF_tra__24ECC82EF766E320"),
        alq.Index("IX_PTLF_track_date", "date_file", mssql_clustered=False),        #
        alq.Index("IX_PTLF_track_ops_status", "ops_status", mssql_clustered=False), #
        alq.Index("IX_PTLF_track_raw_status", "raw_status", mssql_clustered=False), #
        alq.Index("UX_PTLF_track_date_str", "data_date",    # Este no está en SQL-ref
            mssql_clustered=False, unique=True),            # 
        alq.Index("UX_PTLF_track_hash", "file_hash",        # ok
            unique=True, mssql_clustered=False, mssql_where="([file_hash] IS NOT NULL)"))

    track_id: orm.Mapped[int] = orm.mapped_column(alq.BigInteger,   #
        alq.Identity(start=1, increment=1), primary_key=True)
    file_name: orm.Mapped[str] = orm.mapped_column(alq.Unicode(260), nullable=False)    #
    raw_status: orm.Mapped[str] = orm.mapped_column(alq.String(16), nullable=False,     # ??
        server_default=alq.text("('pending')"))
    ops_status: orm.Mapped[str] = orm.mapped_column(alq.String(16), nullable=False,     # ??
        server_default=alq.text("('pending')"))
    created_at: orm.Mapped[dt] = orm.mapped_column(     # ???
        mssql.DATETIME2, nullable=False, server_default=alq.text("(sysutcdatetime())"))
    updated_at: orm.Mapped[dt] = orm.mapped_column(     # ???
        mssql.DATETIME2, nullable=False, server_default=alq.text("(sysutcdatetime())"))
    data_date: orm.Mapped[str] = orm.mapped_column(alq.String(6),   
        nullable=False, server_default=alq.text("((0250806))"))    # ???
    file_path: orm.Mapped[str|None] = orm.mapped_column(alq.Unicode(1024)) #
    file_size: orm.Mapped[int|None] = orm.mapped_column(alq.BigInteger)    #
    file_hash: orm.Mapped[str|None] = orm.mapped_column(alq.CHAR(80))      #
    date_file: orm.Mapped[date|None] = orm.mapped_column(alq.Date, nullable=False) #
    n_records: orm.Mapped[int|None] = orm.mapped_column(alq.Integer)       #
    raw_start: orm.Mapped[dt|None] = orm.mapped_column(mssql.DATETIME2)    #
    raw_finish: orm.Mapped[dt|None] = orm.mapped_column(mssql.DATETIME2)   #
    ops_start: orm.Mapped[dt|None] = orm.mapped_column(mssql.DATETIME2)    #
    ops_finish: orm.Mapped[dt|None] = orm.mapped_column(mssql.DATETIME2)   #

    PTLF_raw: orm.Mapped[list["PTLFRaw"]] = orm.relationship(
        "PTLFRaw", back_populates="PTLF_track")
