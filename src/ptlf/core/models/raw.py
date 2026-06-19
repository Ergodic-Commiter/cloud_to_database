from decimal import Decimal
import typing as typ

import sqlalchemy as alq
from sqlalchemy import orm

from .base import Base


class PTLFRaw(Base):
    __tablename__ = "PTLF_raw"
    __table_args__ = (
        alq.ForeignKeyConstraint(["NGBBSE24-AUTH-POST-DAT"], ["PTLF_track.data_date"],
            name="FK_PTLF_raw_track"),  #
        alq.PrimaryKeyConstraint("row_id", name="PK_PTLF_raw"),     # ok
        alq.Index("IX_PTLF_Fraudes", "NGBBSE24-AUTH-TYP", "NGBBSE24-AUTH-POST-DAT", 
            "NGBBSE24-HEAD-CRD-CARD-NUM", "NGBBSE24-AUTH-APPRV-CDE",
            mssql_clustered=False,
            mssql_include=["NGBBSE24-HEAD-CRD-FIID", "NGBBSE24-AUTH-TRAN-DAT",
                "NGBBSE24-HEAD-RETL-ID", "NGBBSE24-AUTH-TERM-OWNER-NAME",
                "NGBBSE24-AUTH-TERM-CITY", "NGBBSE24-AUTH-TERM-ST",
                "NGBBSE24-AUTH-TERM-CNTRY-CDE", "NGBBSE24-AUTH-RETL-SIC-CDE",
                "NGBBSE24-AUTH-AMT-1", "NGBBSE24-AUTH-PT-SRV-ENTRY-MDE",
                "NGBBSE24-AUTH-ORIG-CRNCY-CDE", "NGBBSE24-C0-CVD-FLD-PRESENT",
                "NGBBSE24-CRDHLDR-ID-METHOD", "NGBBSE24-CH-CRD-VRFY-FLG2",
                "NGBBSE24-B3-CVM-RSLTS"]),
        alq.Index("IX_PTLF_Token", 
            "NGBBSE24-AUTH-TYP", "NGBBSE24-AUTH-POST-DAT", "NGBBSE24-HEAD-CRD-CARD-NUM", 
            "NGBBSE24-AUTH-SEQ-NUM", "NGBBSE24-AUTH-AMT-1",
            mssql_clustered=False,
            mssql_include=["NGBBSE24-C0-E-COM-FLG", "NGBBSE24-C0-AUTHN-COLL-IND",
                "NGBBSE24-C4-TERM-ATTEND-IND", "NGBBSE24-C4-TERM-LOC-IND",
                "NGBBSE24-C4-CHLDR-PRES-IND", "NGBBSE24-C4-CHLDR-ACT-TRM-IND",
                "NGBBSE24-TERM-INPUT-CAP-IND", "NGBBSE24-CRDHLDR-ID-METHOD",
                "NGBBSE24-B2-CRYPTO-INFO-DATA", "NGBBSE24-B2-TVR",
                "NGBBSE24-B2-C-CRD-VRFY-RSLTS", "NGBBSE24-B3-CVM-RSLTS",
                "NGBBSE24-B4-TERM-ENTRY-CAP", "NGBBSE24-B4-ARQC-VRFY",
                "NZBBSE24-CE-CAP-TKN_1", "NZBBSE24-B0-PMT-INIT-CHAN",
                "NZBBSE24-S8-SF2", "NZBBSE24-CE-CAP-TKN_2"]),
        alq.Index("IX_PTLF_raw_member_bucket", "member_bucket", mssql_clustered=False),     # ok
        alq.Index("IX_PTLF_raw_member_prefix", "member_prefix", mssql_clustered=False),     # ok 
        alq.Index("IX_PTLX_raw_date_key", "NGBBSE24-AUTH-POST-DAT", mssql_clustered=False)  # ok
    )
   
    row_id: orm.Mapped[int] = orm.mapped_column(        
        alq.BigInteger, alq.Identity(start=1, increment=1), primary_key=True)
    NGBBSE24_PTLF_TRHA_LENGTH: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-PTLF-TRHA-LENGTH", alq.Integer)
    NGBBSE24_PTLF_TRHA_RECORD_TYPE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PTLF-TRHA-RECORD-TYPE", alq.String(2))
    NGBBSE24_HEAD_DAT_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-DAT-TIM", alq.String(19))
    NGBBSE24_HEAD_REC_TYP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-REC-TYP", alq.String(2))
    NGBBSE24_HEAD_CRD_LN: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-CRD-LN", alq.String(4))
    NGBBSE24_HEAD_CRD_FIID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-CRD-FIID", alq.String(4))
    NGBBSE24_HEAD_CRD_CARD_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-CRD-CARD-NUM", alq.String(19))
    NGBBSE24_HEAD_MBR_NUM: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-HEAD-MBR-NUM", alq.Integer)
    NGBBSE24_HEAD_RETL_LN: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-LN", alq.String(4))
    NGBBSE24_HEAD_RETL_FIID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-FIID", alq.String(4))
    NGBBSE24_HEAD_RETL_GRP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-GRP", alq.String(4))
    NGBBSE24_HEAD_RETL_REGN: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-REGN", alq.String(4))
    NGBBSE24_HEAD_RETL_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-ID", alq.Unicode(19))
    NGBBSE24_HEAD_RETL_TERM_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-TERM-ID", alq.String(16))
    NGBBSE24_HEAD_RETL_SHIFT_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-SHIFT-NUM", alq.String(3))
    NGBBSE24_HEAD_RETL_BATCH_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-RETL-BATCH-NUM", alq.String(3))
    NGBBSE24_HEAD_TERM_LN: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TERM-LN", alq.String(4))
    NGBBSE24_HEAD_TERM_FIID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TERM-FIID", alq.String(4))
    NGBBSE24_HEAD_TERM_TERM_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TERM-TERM-ID", alq.String(16))
    NGBBSE24_HEAD_TERM_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TERM-TIM", alq.String(8))
    NGBBSE24_HEAD_TKEY_TERM_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TKEY-TERM-ID", alq.String(16))
    NGBBSE24_HEAD_TKEY_RKEY_RFMT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TKEY-RKEY-RFMT", alq.String(1))
    NGBBSE24_TKEY_RKEY_RTL_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKEY-RKEY-RTL-ID", alq.Unicode(19))
    NGBBSE24_TKEY_RKEY_CLK_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKEY-RKEY-CLK-ID", alq.String(6))
    NGBBSE24_HEAD_DATA_FLAG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-DATA-FLAG", alq.String(1))
    NGBBSE24_AUTH_TYP: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TYP", alq.Integer)
    NGBBSE24_AUTH_RTE_STAT: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RTE-STAT", alq.Integer)
    NGBBSE24_AUTH_ORIGINATOR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIGINATOR", alq.String(1))
    NGBBSE24_AUTH_RESPONDER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RESPONDER", alq.String(1))
    NGBBSE24_AUTH_ISS_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ISS-CDE", alq.String(2))
    NGBBSE24_AUTH_ENTRY_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ENTRY-TIM", alq.String(19))
    NGBBSE24_AUTH_EXIT_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-EXIT-TIM", alq.String(19))
    NGBBSE24_AUTH_RE_ENTRY_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RE-ENTRY-TIM", alq.String(19))
    NGBBSE24_AUTH_TRAN_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TRAN-DAT", alq.String(6))
    NGBBSE24_AUTH_TRAN_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TRAN-TIM", alq.String(8))
    NGBBSE24_AUTH_POST_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-POST-DAT", alq.String(6))
    NGBBSE24_AUTH_ACQ_ICH_STL_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ACQ-ICH-STL-DAT", alq.String(6))
    NGBBSE24_AUTH_ISS_ICH_STL_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ISS-ICH-STL-DAT", alq.String(6))
    NGBBSE24_AUTH_SEQ_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-SEQ-NUM", alq.String(12))
    NGBBSE24_AUTH_TERM_NAME_LOC: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TERM-NAME-LOC", alq.Unicode(25))
    NGBBSE24_AUTH_TERM_OWNER_NAME: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TERM-OWNER-NAME", alq.Unicode(22))
    NGBBSE24_AUTH_TERM_CITY: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TERM-CITY", alq.Unicode(13))
    NGBBSE24_AUTH_TERM_ST: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TERM-ST", alq.String(3))
    NGBBSE24_AUTH_TERM_CNTRY_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TERM-CNTRY-CDE", alq.String(2))
    NGBBSE24_AUTH_BRCH_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-BRCH-ID", alq.String(4))
    NGBBSE24_AUTH_USER_FLD2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-USER-FLD2", alq.String(3))
    NGBBSE24_AUTH_TERM_TIM_OFST: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TERM-TIM-OFST", alq.String(5))
    NGBBSE24_AUTH_ACQ_INST_ID_NUM: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ACQ-INST-ID-NUM", alq.BigInteger)
    NGBBSE24_AUTH_RCV_INST_ID_NUM: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RCV-INST-ID-NUM", alq.BigInteger)
    NGBBSE24_AUTH_TERM_TYP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TERM-TYP", alq.String(2))
    NGBBSE24_AUTH_CLERK_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CLERK-ID", alq.String(6))
    NGBBSE24_AUTH_GRP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-GRP", alq.String(4))
    NGBBSE24_AUTH_USER_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-USER-ID", alq.String(8))
    NGBBSE24_AUTH_RETL_SIC_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RETL-SIC-CDE", alq.String(4))
    NGBBSE24_AUTH_ORIG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIG", alq.String(4))
    NGBBSE24_AUTH_DEST: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-DEST", alq.String(4))
    NGBBSE24_AUTH_TRAN_CDE_TC: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TRAN-CDE-TC", alq.String(2))
    NGBBSE24_AUTH_TRAN_CDE_T: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TRAN-CDE-T", alq.String(1))
    NGBBSE24_AUTH_TRAN_CDE_AA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TRAN-CDE-AA", alq.String(2))
    NGBBSE24_AUTH_TRAN_CDE_C: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TRAN-CDE-C", alq.String(1))
    NGBBSE24_AUTH_CRD_TYP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CRD-TYP", alq.String(2))
    NGBBSE24_AUTH_ACCT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ACCT", alq.String(19))
    NGBBSE24_AUTH_RESP_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RESP-CDE", alq.Integer)
    NGBBSE24_AUTH_AMT_1_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AMT-1-FILLER", alq.String(2))
    NGBBSE24_AUTH_AMT_1: orm.Mapped[Decimal|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AMT-1", alq.DECIMAL(17, 2))
    NGBBSE24_AUTH_AMT_2_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AMT-2-FILLER", alq.String(2))
    NGBBSE24_AUTH_AMT_2: orm.Mapped[Decimal|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AMT-2", alq.DECIMAL(17, 2))
    NGBBSE24_AUTH_EXP_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-EXP-DAT", alq.String(4))
    NGBBSE24_AUTH_TRACK2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TRACK2", alq.Unicode(40))
    NGBBSE24_AUTH_PIN_OFST: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PIN-OFST", alq.String(16))
    NGBBSE24_AUTH_PRE_AUTH_SEQ_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PRE-AUTH-SEQ-NUM", alq.String(12))
    NGBBSE24_AUTH_INVOICE_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-INVOICE-NUM", alq.String(10))
    NGBBSE24_AUTH_ORIG_INVOICE_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIG-INVOICE-NUM", alq.String(10))
    NGBBSE24_AUTH_AUTHORIZER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AUTHORIZER", alq.String(16))
    NGBBSE24_AUTH_AUTH_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AUTH-IND", alq.String(1))
    NGBBSE24_AUTH_SHIFT_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-SHIFT-NUM", alq.String(3))
    NGBBSE24_AUTH_BATCH_SEQ_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-BATCH-SEQ-NUM", alq.String(3))
    NGBBSE24_AUTH_APPRV_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-APPRV-CDE", alq.String(8))
    NGBBSE24_AUTH_APPRV_CDE_LGTH: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-APPRV-CDE-LGTH", alq.Integer)
    NGBBSE24_AUTH_ICHG_RESP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ICHG-RESP", alq.String(8))
    NGBBSE24_AUTH_PSEUDO_TERM_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PSEUDO-TERM-ID", alq.String(4))
    NGBBSE24_AUTH_RFRL_PHONE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RFRL-PHONE", alq.String(20))
    NGBBSE24_AUTH_DFT_CAPTURE_FLG: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-DFT-CAPTURE-FLG", alq.Integer)
    NGBBSE24_AUTH_SETL_FLAG: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-SETL-FLAG", alq.Integer)
    NGBBSE24_AUTH_RVRL_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-RVRL-CDE", alq.Integer)
    NGBBSE24_AUTH_REA_FOR_CHRGBCK: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-REA-FOR-CHRGBCK", alq.String(2))
    NGBBSE24_AUTH_NUM_OF_CHRGBCK: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-NUM-OF-CHRGBCK", alq.Integer)
    NGBBSE24_AUTH_PT_SRV_COND_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PT-SRV-COND-CDE", alq.Integer)
    NGBBSE24_AUTH_PT_SRV_ENTRY_MDE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PT-SRV-ENTRY-MDE", alq.Integer)
    NGBBSE24_AUTH_AUTH_IND2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AUTH-IND2", alq.String(1))
    NGBBSE24_AUTH_ORIG_CRNCY_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIG-CRNCY-CDE", alq.Integer)
    NGBBSE24_AUTH_AUTH_CRNCY_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AUTH-CRNCY-CDE", alq.Integer)
    NGBBSE24_AUTH_AUTH_CONV_RATE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AUTH-CONV-RATE", alq.Integer)
    NGBBSE24_AUTH_SETL_CRNCY_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-SETL-CRNCY-CDE", alq.Integer)
    NGBBSE24_AUTH_SETL_CONV_RATE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-SETL-CONV-RATE", alq.Integer)
    NGBBSE24_AUTH_CONV_DAT_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CONV-DAT-TIM", alq.String(19))
    NGBBSE24_AUTH_IMP_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-IMP-IND", alq.String(1))
    NGBBSE24_AUTH_AVAIL_CR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-AVAIL-CR", alq.String(1))
    NGBBSE24_AUTH_CR_LMT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CR-LMT", alq.String(1))
    NGBBSE24_AUTH_CR_BAL: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CR-BAL", alq.String(1))
    NGBBSE24_AUTH_TTL_FLOAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-TTL-FLOAT", alq.String(1))
    NGBBSE24_AUTH_CUR_FLOAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CUR-FLOAT", alq.String(1))
    NGBBSE24_AUTH_ADJ_SETL_IMP_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ADJ-SETL-IMP-FLG", alq.String(1))
    NGBBSE24_AUTH_PBF1: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PBF1", alq.String(1))
    NGBBSE24_AUTH_PBF2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PBF2", alq.String(1))
    NGBBSE24_AUTH_PBF3: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PBF3", alq.String(1))
    NGBBSE24_AUTH_PBF4: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PBF4", alq.String(1))
    NGBBSE24_AUTH_FRWD_INST_ID_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-FRWD-INST-ID-NUM", alq.String(11))
    NGBBSE24_AUTH_CRD_ACCPT_ID_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CRD-ACCPT-ID-NUM", alq.String(15))
    NGBBSE24_AUTH_CRD_ISS_ID_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-CRD-ISS-ID-NUM", alq.String(11))
    NGBBSE24_AUTH_ORIG_MSG_TYP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIG-MSG-TYP", alq.String(4))
    NGBBSE24_AUTH_ORIG_TRAN_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIG-TRAN-TIM", alq.String(8))
    NGBBSE24_AUTH_ORIG_TRAN_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIG-TRAN-DAT", alq.String(4))
    NGBBSE24_AUTH_ORIG_SEQ_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORIG-SEQ-NUM", alq.String(12))
    NGBBSE24_AUTH_ORG_B24_PST_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ORG-B24-PST-DAT", alq.String(4))
    NGBBSE24_AUTH_EXCP_RSN_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-EXCP-RSN-CDE", alq.String(3))
    NGBBSE24_AUTH_OVRRDE_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-OVRRDE-FLG", alq.String(1))
    NGBBSE24_AUTH_ADDR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ADDR", alq.String(20))
    NGBBSE24_AUTH_ZIP_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ZIP-CDE", alq.String(9))
    NGBBSE24_AUTH_ADDR_VRFY_STAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-ADDR-VRFY-STAT", alq.String(1))
    NGBBSE24_AUTH_PIN_IND: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PIN-IND", alq.Integer)
    NGBBSE24_AUTH_PIN_TRIES: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PIN-TRIES", alq.String(1))
    NGBBSE24_AUTH_PRE_AUTH_TS_DAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PRE-AUTH-TS-DAT", alq.String(6))
    NGBBSE24_AUTH_PRE_AUTH_TS_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PRE-AUTH-TS-TIM", alq.String(8))
    NGBBSE24_AUTH_PRE_AUTH_HLDS_LV: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-PRE-AUTH-HLDS-LV", alq.String(1))
    NGBBSE24_AUTH_USER_FLD5: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-AUTH-USER-FLD5", alq.String(29))
    NGBBSE24_HEAD_TOK_EYE_CATCHER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TOK-EYE-CATCHER", alq.String(2))
    NGBBSE24_HEAD_TOK_COUNT: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TOK-COUNT", alq.Integer)
    NGBBSE24_HEAD_TOK_LGTH: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-HEAD-TOK-LGTH", alq.Integer)
    NGBBSE24_04_ERR_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-04-ERR-FLG", alq.String(1))
    NGBBSE24_04_RTE_GRP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-04-RTE-GRP", alq.String(11))
    NGBBSE24_04_CRD_VRFY_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-04-CRD-VRFY-FLG", alq.String(1))
    NGBBSE24_04_CITY_EXT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-04-CITY-EXT", alq.String(5))
    NGBBSE24_04_CMPLT_TRACK2_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-04-CMPLT-TRACK2-DATA", alq.String(1))
    NGBBSE24_04_UAF_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-04-UAF-FLG", alq.String(1))
    NGBBSE24_BM_TXN_SUBTYPE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BM-TXN-SUBTYPE", alq.String(4))
    NGBBSE24_BM_ACQ_PROC_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BM-ACQ-PROC-CDE", alq.String(6))
    NGBBSE24_BM_ISS_PROC_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BM-ISS-PROC-CDE", alq.String(6))
    NGBBSE24_BM_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BM-FILLER", alq.String(20))
    NGBBSE24_C0_CVD_FLD: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-CVD-FLD", alq.String(4))
    NGBBSE24_C0_RESUB_STAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-RESUB-STAT", alq.String(1))
    NGBBSE24_RESUB_CNTR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RESUB-CNTR", alq.String(3))
    NGBBSE24_C0_TERM_POSTAL_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-TERM-POSTAL-CDE", alq.Unicode(10))
    NGBBSE24_C0_E_COM_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-E-COM-FLG", alq.String(1))
    NGBBSE24_C0_CMRCL_CRD_TYP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-CMRCL-CRD-TYP", alq.String(1))
    NGBBSE24_C0_ADNL_DATA_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-ADNL-DATA-IND", alq.String(1))
    NGBBSE24_C0_CVD_FLD_PRESENT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-CVD-FLD-PRESENT", alq.String(1))
    NGBBSE24_C0_SAF_OR_FORCE_POST: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-SAF-OR-FORCE-POST", alq.String(1))
    NGBBSE24_C0_AUTHN_COLL_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-AUTHN-COLL-IND", alq.String(1))
    NGBBSE24_C0_FRD_PRN_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-FRD-PRN-FLG", alq.String(1))
    NGBBSE24_C0_CAVV_AAV_RSLT_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C0-CAVV-AAV-RSLT-CDE", alq.String(1))
    NGBBSE24_C4_TERM_ATTEND_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-TERM-ATTEND-IND", alq.String(1))
    NGBBSE24_C4_TERM_OPER_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-TERM-OPER-IND", alq.String(1))
    NGBBSE24_C4_TERM_LOC_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-TERM-LOC-IND", alq.String(1))
    NGBBSE24_C4_CHLDR_PRES_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-CHLDR-PRES-IND", alq.String(1))
    NGBBSE24_C4_CRD_PRESENT_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-CRD-PRESENT-IND", alq.String(1))
    NGBBSE24_C4_CRD_CAPTR_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-CRD-CAPTR-IND", alq.String(1))
    NGBBSE24_C4_TXN_STAT_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-TXN-STAT-IND", alq.String(1))
    NGBBSE24_C4_TXN_SEC_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-TXN-SEC-IND", alq.String(1))
    NGBBSE24_C4_TXN_RTN_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-TXN-RTN-IND", alq.String(1))
    NGBBSE24_C4_CHLDR_ACT_TRM_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-C4-CHLDR-ACT-TRM-IND", alq.String(1))
    NGBBSE24_TERM_INPUT_CAP_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TERM-INPUT-CAP-IND", alq.String(1))
    NGBBSE24_CRDHLDR_ID_METHOD: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CRDHLDR-ID-METHOD", alq.String(1))
    NGBBSE24_P0_MISC_IMPACT_SETTLE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-MISC-IMPACT-SETTLE", alq.String(2))
    NGBBSE24_P0_MISC_CHECK_SETTLE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-MISC-CHECK-SETTLE", alq.String(2))
    NGBBSE24_P0_QUANT_QUOTAS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-QUANT-QUOTAS", alq.String(2))
    NGBBSE24_P0_USER_FLD0: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-USER-FLD0", alq.String(1))
    NGBBSE24_P0_CAP_FLAG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-CAP-FLAG", alq.String(1))
    NGBBSE24_P0_TYPE_FINANCING: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-TYPE-FINANCING", alq.String(2))
    NGBBSE24_P0_IND_CONTING: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-IND-CONTING", alq.String(1))
    NGBBSE24_P0_IMPACT_SETTLE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-IMPACT-SETTLE", alq.String(1))
    NGBBSE24_P0_SITUATION_TAX_BUS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-SITUATION-TAX-BUS", alq.String(2))
    NGBBSE24_P0_RUBRO: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-RUBRO", alq.String(5))
    NGBBSE24_P0_FIID_ACQ: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-FIID-ACQ", alq.String(4))
    NGBBSE24_P0_CNTRY_ISO: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-CNTRY-ISO", alq.String(3))
    NGBBSE24_P0_ORIG_APPRV_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-ORIG-APPRV-CDE", alq.String(6))
    NGBBSE24_P0_USER_FLD1: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P0-USER-FLD1", alq.String(6))
    NGBBSE24_P1_NRO_REFERENCE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P1-NRO-REFERENCE", alq.String(12))
    NGBBSE24_P1_PERIOD_BILLING: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P1-PERIOD-BILLING", alq.String(5))
    NGBBSE24_P1_STATUS_DA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P1-STATUS-DA", alq.String(2))
    NGBBSE24_P1_USER_FLD: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P1-USER-FLD", alq.String(1))
    NGBBSE24_P4_ITEM_BUSINESS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P4-ITEM-BUSINESS", alq.String(6))
    NGBBSE24_P4_CODE_PRODUCT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P4-CODE-PRODUCT", alq.String(12))
    NGBBSE24_P4_NRO_BILLING: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P4-NRO-BILLING", alq.String(12))
    NGBBSE24_P4_POINTS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P4-POINTS", alq.String(10))
    NGBBSE24_P5_TYPE_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P5-TYPE-ID", alq.String(1))
    NGBBSE24_P5_NRO_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P5-NRO-ID", alq.String(11))
    NGBBSE24_P5_SEX: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P5-SEX", alq.String(1))
    NGBBSE24_P5_NAME: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P5-NAME", alq.String(25))
    NGBBSE24_P5_TOTAL: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P5-TOTAL", alq.String(4))
    NGBBSE24_P5_OBSERVATION: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P5-OBSERVATION", alq.String(16))
    NGBBSE24_P6_TYPE_DIF: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P6-TYPE-DIF", alq.String(1))
    NGBBSE24_P6_DIA_DIF: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P6-DIA-DIF", alq.String(2))
    NGBBSE24_P6_DIA_INITIAL_DIF: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P6-DIA-INITIAL-DIF", alq.String(2))
    NGBBSE24_P6_DIA_PRESENTATION: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P6-DIA-PRESENTATION", alq.String(6))
    NGBBSE24_P6_USER_FLD: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-P6-USER-FLD", alq.String(1))
    NGBBSE24_RO_IMP_QUOTA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-IMP-QUOTA", alq.String(10))
    NGBBSE24_RO_COSTO_FIN_TOT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-COSTO-FIN-TOT", alq.String(5))
    NGBBSE24_RO_IMP_CHARGE_OTHER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-IMP-CHARGE-OTHER", alq.String(7))
    NGBBSE24_RO_TASA_CHARGE_SECURE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-TASA-CHARGE-SECURE", alq.String(7))
    NGBBSE24_RO_TNA: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-RO-TNA", alq.Integer)
    NGBBSE24_RO_TEA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-TEA", alq.String(5))
    NGBBSE24_RO_PLAN_CRED: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-PLAN-CRED", alq.String(1))
    NGBBSE24_RO_SUB_PLAN_CRED: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-SUB-PLAN-CRED", alq.String(2))
    NGBBSE24_RO_FLAG_TYPE_SEG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-FLAG-TYPE-SEG", alq.String(1))
    NGBBSE24_RO_FLAG_TYPE_EMI: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-FLAG-TYPE-EMI", alq.String(1))
    NGBBSE24_RO_QUANT_QUOTAS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-QUANT-QUOTAS", alq.String(2))
    NGBBSE24_RO_MAX_QUANT_QUOTAS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-MAX-QUANT-QUOTAS", alq.String(2))
    NGBBSE24_RO_COD_AUT_ORIG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-RO-COD-AUT-ORIG", alq.String(8))
    NGBBSE24_R2_QTY_QUOTAS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-QTY-QUOTAS", alq.String(2))
    NGBBSE24_R2_ENTITY_SENDER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-ENTITY-SENDER", alq.String(4))
    NGBBSE24_R2_PLAN: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-PLAN", alq.String(1))
    NGBBSE24_R2_SITUATION_TAX: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-SITUATION-TAX", alq.String(1))
    NGBBSE24_R2_PHOTO_FLAG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-PHOTO-FLAG", alq.String(1))
    NGBBSE24_R2_NRO_BILLING: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-NRO-BILLING", alq.String(12))
    NGBBSE24_R2_TYPE_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-TYPE-ID", alq.String(1))
    NGBBSE24_R2_NRO_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-NRO-ID", alq.String(11))
    NGBBSE24_R2_TCC: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-TCC", alq.String(1))
    NGBBSE24_R2_REASON: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-R2-REASON", alq.Integer)
    NGBBSE24_R2_REV_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-R2-REV-FILLER", alq.String(10))
    NGBBSE24_PC_CATEGORY_BUSINESS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PC-CATEGORY-BUSINESS", alq.String(2))
    NGBBSE24_PC_PRODUCT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PC-PRODUCT", alq.String(1))
    NGBBSE24_PC_IMPORT_DISCOUNT: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-PC-IMPORT-DISCOUNT", alq.BigInteger)
    NGBBSE24_PC_DISCOUNT: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-PC-DISCOUNT", alq.Integer)
    NGBBSE24_PC_PGM_GUARANTEE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-PC-PGM-GUARANTEE", alq.Integer)
    NGBBSE24_PC_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PC-FILLER", alq.String(9))
    NGBBSE24_PD_MODE_PAYMENT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-MODE-PAYMENT", alq.String(2))
    NGBBSE24_PD_NUMBER_MOBILE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-NUMBER-MOBILE", alq.String(4))
    NGBBSE24_PD_TYPE_CHARGE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-TYPE-CHARGE", alq.String(2))
    NGBBSE24_PD_CARD: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-CARD", alq.String(19))
    NGBBSE24_PD_TRACENO: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-TRACENO", alq.String(12))
    NGBBSE24_PD_COUPON: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-COUPON", alq.String(4))
    NGBBSE24_PD_APPROVAL_CODE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-APPROVAL-CODE", alq.String(6))
    NGBBSE24_PD_BUSINESS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-BUSINESS", alq.String(15))
    NGBBSE24_PD_ACCOUNT_CBU: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-ACCOUNT-CBU", alq.String(25))
    NGBBSE24_PD_IMP_COMISSION: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-PD-IMP-COMISSION", alq.BigInteger)
    NGBBSE24_PD_IMP_CHARGED: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-PD-IMP-CHARGED", alq.BigInteger)
    NGBBSE24_PD_SDO_TELEPHONE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-PD-SDO-TELEPHONE", alq.BigInteger)
    NGBBSE24_PD_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-PD-FILLER", alq.String(5))
    NGBBSE24_TKN_H_EYE_CATCHER_Q9: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-Q9", alq.String(2))
    NGBBSE24_Q9: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q9", alq.String(2))
    NGBBSE24_Q9_LEN: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q9-LEN", alq.Integer)
    NGBBSE24_Q9_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q9-FILLER", alq.String(1))
    NGBBSE24_Q9_TAX_AMT: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q9-TAX-AMT", alq.BigInteger)
    NGBBSE24_TAG_Q9_TIP_AMT: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TAG-Q9-TIP-AMT", alq.BigInteger)
    NGBBSE24_Q9_CBK_AMT: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q9-CBK-AMT", alq.BigInteger)
    NGBBSE24_Q9_REF_NBR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q9-REF-NBR", alq.String(6))
    NGBBSE24_Q9_USR_FLD: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q9-USR-FLD", alq.String(18))
    NGBBSE24_TKN_H_EYE_CATCHER_QA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-QA", alq.String(2))
    NGBBSE24_TKN_H_ID_QA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-QA", alq.String(2))
    NGBBSE24_TKN_H_LGTH_QA: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-QA", alq.Integer)
    NGBBSE24_FILLER_1: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_1", alq.String(1))
    NGBBSE24_QA_BATCH_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-QA-BATCH-ID", alq.String(6))
    NGBBSE24_QA_TRAN_CODE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-QA-TRAN-CODE", alq.String(2))
    NGBBSE24_QA_TERM_CODE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-QA-TERM-CODE", alq.String(3))
    NGBBSE24_QA_PREFLA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-QA-PREFLA", alq.String(1))
    NGBBSE24_QA_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-QA-FILLER", alq.String(28))
    NGBBSE24_TKN_H_EYE_CATCHER_CH: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-CH", alq.String(2))
    NGBBSE24_TKN_H_ID_CH: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-CH", alq.String(2))
    NGBBSE24_TKN_H_LGTH_CH: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-CH", alq.Integer)
    NGBBSE24_FILLER_2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_2", alq.String(1))
    NGBBSE24_CH_RESP_SRC_RSN_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-RESP-SRC-RSN-CDE", alq.String(1))
    NGBBSE24_CH_CRD_VRFY_FLG2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-CRD-VRFY-FLG2", alq.String(1))
    NGBBSE24_CH_ONLINE_LMT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-ONLINE-LMT", alq.String(12))
    NGBBSE24_CH_RETL_CLASS_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-RETL-CLASS-CDE", alq.String(4))
    NGBBSE24_CH_EMV_CAPABLE_OUTLET: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-EMV-CAPABLE-OUTLET", alq.String(1))
    NGBBSE24_CH_RECUR_PMNT_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-RECUR-PMNT-IND", alq.String(1))
    NGBBSE24_CH_NUM_INSTL: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-NUM-INSTL", alq.String(2))
    NGBBSE24_CH_NUM_MM_GRATUITY: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-NUM-MM-GRATUITY", alq.String(2))
    NGBBSE24_CH_PMNT_PLAN: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-PMNT-PLAN", alq.String(3))
    NGBBSE24_CH_TERM_OTPT_CAP_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-TERM-OTPT-CAP-IND", alq.String(1))
    NGBBSE24_CH_CRHDR_AUTH_CP_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-CRHDR-AUTH-CP-IND", alq.String(1))
    NGBBSE24_CH_PARTIAL_AUTH_OPT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-PARTIAL-AUTH-OPT", alq.String(1))
    NGBBSE24_CH_INSTL_PLAN_TYP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-INSTL-PLAN-TYP", alq.String(2))
    NGBBSE24_CH_INSTL_GRATUITY_PRD: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-INSTL-GRATUITY-PRD", alq.String(1))
    NGBBSE24_CH_RVSL_RSN_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-RVSL-RSN-IND", alq.String(1))
    NGBBSE24_CH_USER_FLD1: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-CH-USER-FLD1", alq.String(6))
    NGBBSE24_TKN_H_EYE_CATCHER_B2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-B2", alq.String(2))
    NGBBSE24_TKN_H_ID_B2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-B2", alq.String(2))
    NGBBSE24_TKN_H_LGTH_B2: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-B2", alq.Integer)
    NGBBSE24_FILLER_3: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_3", alq.String(1))
    NGBBSE24_B2_BIT_MAP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-BIT-MAP", alq.String(4))
    NGBBSE24_B2_USER_FLD1: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-USER-FLD1", alq.String(4))
    NGBBSE24_B2_CRYPTO_INFO_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-CRYPTO-INFO-DATA", alq.String(2))
    NGBBSE24_B2_TVR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-TVR", alq.String(10))
    NGBBSE24_B2_ARQC: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-ARQC", alq.String(16))
    NGBBSE24_B2_AMT_AUTH: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-AMT-AUTH", alq.String(12))
    NGBBSE24_B2_AMT_OTHER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-AMT-OTHER", alq.String(12))
    NGBBSE24_B2_AIP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-AIP", alq.String(4))
    NGBBSE24_B2_ATC: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-ATC", alq.String(4))
    NGBBSE24_B2_TERM_CNTRY_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-TERM-CNTRY-CDE", alq.String(3))
    NGBBSE24_B2_TRAN_CRNCY_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-TRAN-CRNCY-CDE", alq.String(3))
    NGBBSE24_B2_TRAN_DATE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-TRAN-DATE", alq.String(6))
    NGBBSE24_B2_TRAN_TYPE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-TRAN-TYPE", alq.String(2))
    NGBBSE24_B2_UNPREDICT_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-UNPREDICT-NUM", alq.String(8))
    NGBBSE24_B2_ISS_APPL_DATA_LGTH: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-ISS-APPL-DATA-LGTH", alq.String(4))
    NGBBSE24_B2_C_LGTH: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-C-LGTH", alq.String(2))
    NGBBSE24_B2_C_COMMON_CORE_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-C-COMMON-CORE-ID", alq.String(2))
    NGBBSE24_B2_C_DERIV_KEY_INDEX: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-C-DERIV-KEY-INDEX", alq.String(2))
    NGBBSE24_B2_C_CRD_VRFY_RSLTS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-C-CRD-VRFY-RSLTS", alq.String(10))
    NGBBSE24_B2_C_COUNTERS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-C-COUNTERS", alq.String(16))
    NGBBSE24_B2_C_ISS_DIS_DATA_LG: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-C-ISS-DIS-DATA-LG", alq.String(2))
    NGBBSE24_B2_C_ISS_DISCR_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B2-C-ISS-DISCR-DATA", alq.String(30))
    NGBBSE24_TKN_H_EYE_CATCHER_B3: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-B3", alq.String(2))
    NGBBSE24_TKN_H_ID_B3: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-B3", alq.String(2))
    NGBBSE24_TKN_H_LGTH_B3: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-B3", alq.Integer)
    NGBBSE24_FILLER_4: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_4", alq.String(1))
    NGBBSE24_B3_BIT_MAP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-BIT-MAP", alq.String(4))
    NGBBSE24_B3_TERM_SER_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-TERM-SER-NUM", alq.String(8))
    NGBBSE24_B3_EMV_TERM_CAP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-EMV-TERM-CAP", alq.String(8))
    NGBBSE24_B3_USER_FLD1: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-USER-FLD1", alq.String(4))
    NGBBSE24_B3_USER_FLD2: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-USER-FLD2", alq.String(8))
    NGBBSE24_B3_EMV_TERM_TYPE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-EMV-TERM-TYPE", alq.String(2))
    NGBBSE24_B3_APPL_VER_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-APPL-VER-NUM", alq.String(4))
    NGBBSE24_B3_CVM_RSLTS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-CVM-RSLTS", alq.String(6))
    NGBBSE24_B3_DF_NAME_LGTH: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-DF-NAME-LGTH", alq.String(4))
    NGBBSE24_B3_DF_NAME: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B3-DF-NAME", alq.String(32))
    NGBBSE24_TKN_H_EYE_CATCHER_B4: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-B4", alq.String(2))
    NGBBSE24_TKN_H_ID_B4: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-B4", alq.String(2))
    NGBBSE24_TKN_H_LGTH_B4: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-B4", alq.Integer)
    NGBBSE24_FILLER_5: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_5", alq.String(1))
    NGBBSE24_B4_PT_SRV_ENTRY_MDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-PT-SRV-ENTRY-MDE", alq.String(3))
    NGBBSE24_B4_TERM_ENTRY_CAP: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-TERM-ENTRY-CAP", alq.String(1))
    NGBBSE24_B4_LAST_EMV_STAT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-LAST-EMV-STAT", alq.String(1))
    NGBBSE24_B4_DATA_SUSPECT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-DATA-SUSPECT", alq.String(1))
    NGBBSE24_B4_APPL_PAN_SEQ_NUM: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-APPL-PAN-SEQ-NUM", alq.String(2))
    NGBBSE24_B4_CVM_RSLTS: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-CVM-RSLTS", alq.String(6))
    NGBBSE24_B4_RSN_ONL_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-RSN-ONL-CDE", alq.String(4))
    NGBBSE24_B4_ARQC_VRFY: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-ARQC-VRFY", alq.String(1))
    NGBBSE24_B4_ISO_RC_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B4-ISO-RC-IND", alq.String(1))
    NGBBSE24_EYE_CATCHER_B5: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-EYE-CATCHER-B5", alq.String(2))
    NGBBSE24_ID_B5: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-ID-B5", alq.String(2))
    NGBBSE24_LGTH_B5: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-LGTH-B5", alq.Integer)
    NGBBSE24_FILLER_6: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_6", alq.String(1))
    NGBBSE24_B5_ISS_AUTH_DATA_LGTH: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B5-ISS-AUTH-DATA-LGTH", alq.String(4))
    NGBBSE24_B5_ISS_AUTH_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-B5-ISS-AUTH-DATA", alq.String(34))
    NGBBSE24_EYE_BJ: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-EYE-BJ", alq.String(2))
    NGBBSE24_ID_BJ: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-ID-BJ", alq.String(2))
    NGBBSE24_LGTH_BJ: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-LGTH-BJ", alq.Integer)
    NGBBSE24_FILLER_7: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_7", alq.String(1))
    NGBBSE24_BJ_NUM_ISS_SCRIPT_RT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BJ-NUM-ISS-SCRIPT-RT", alq.String(1))
    NGBBSE24_BJ_USER_FLD1: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BJ-USER-FLD1", alq.String(1))
    NGBBSE24_BJ_ISS_SCRPT_RSLT: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BJ-ISS-SCRPT-RSLT", alq.String(1))
    NGBBSE24_BJ_ISS_SCRPT_SEQ: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BJ-ISS-SCRPT-SEQ", alq.String(1))
    NGBBSE24_BJ_ISS_SCRPT_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-BJ-ISS-SCRPT-ID", alq.String(8))
    NGBBSE24_TKN_H_EYE_CATCHER_Q4: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-Q4", alq.String(2))
    NGBBSE24_TKN_H_ID_Q4: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-Q4", alq.String(2))
    NGBBSE24_TKN_H_LGTH_Q4: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-Q4", alq.Integer)
    NGBBSE24_FILLER_8: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_8", alq.String(1))
    NGBBSE24_Q4_NBR_INST: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q4-NBR-INST", alq.String(2))
    NGBBSE24_Q4_TIPS: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q4-TIPS", alq.BigInteger)
    NGBBSE24_Q4_IVA_BASE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q4-IVA-BASE", alq.BigInteger)
    NGBBSE24_Q4_IVA_VALUE: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q4-IVA-VALUE", alq.BigInteger)
    NGBBSE24_Q4_IVA_BASE_DEV: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q4-IVA-BASE-DEV", alq.BigInteger)
    NGBBSE24_Q4_RECEIPT_NBR: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-Q4-RECEIPT-NBR", alq.BigInteger)
    NGBBSE24_Q4_BANK_CODE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q4-BANK-CODE", alq.String(4))
    NGBBSE24_Q4_TXN_REF: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q4-TXN-REF", alq.String(16))
    NGBBSE24_Q4_DB_CURR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q4-DB-CURR", alq.String(3))
    NGBBSE24_Q4_PIN_SYNC_FL: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q4-PIN-SYNC-FL", alq.String(1))
    NGBBSE24_Q4_PIN_FORCE_FL: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q4-PIN-FORCE-FL", alq.String(1))
    NGBBSE24_Q4_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q4-FILLER", alq.String(30))
    NGBBSE24_TKN_H_EYE_CATCHER_Q7: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-Q7", alq.String(2))
    NGBBSE24_TKN_H_ID_Q7: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-Q7", alq.String(2))
    NGBBSE24_TKN_H_LGTH_Q7: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-Q7", alq.Integer)
    NGBBSE24_FILLER_9: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_9", alq.String(1))
    NGBBSE24_Q7_CARD_NBR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q7-CARD-NBR", alq.String(19))
    NGBBSE24_Q7_ACCT_NBR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q7-ACCT-NBR", alq.String(28))
    NGBBSE24_Q7_FILLER: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-Q7-FILLER", alq.String(31))
    NGBBSE24_TKN_H_EYE_CATCHER_17: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-EYE-CATCHER-17", alq.String(2))
    NGBBSE24_TKN_H_ID_17: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-ID-17", alq.String(2))
    NGBBSE24_TKN_H_LGTH_17: orm.Mapped[int|None] = orm.mapped_column(
        "NGBBSE24-TKN-H-LGTH-17", alq.Integer)
    NGBBSE24_FILLER_10: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_10", alq.String(1))
    NGBBSE24_17_SRV_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-17-SRV-IND", alq.String(1))
    NGBBSE24_17_TRAN_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-17-TRAN-ID", alq.String(15))
    NGBBSE24_17_VALID_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-17-VALID-CDE", alq.String(4))
    NGBBSE24_17_MKT_SPC_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-17-MKT-SPC-DATA", alq.String(1))
    NGBBSE24_17_DUR: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-17-DUR", alq.String(1))
    NGBBSE24_17_PROP_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-17-PROP-IND", alq.String(1))
    NGBBSE24_FILLER_11: orm.Mapped[str|None] = orm.mapped_column(
        "NGBBSE24-FILLER_11", alq.String(24))
    NZBBSE24_TKN_H_EYE_CATCHER_B1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-EYE-CATCHER-B1", alq.String(2))
    NZBBSE24_TKN_H_ID_B1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-ID-B1", alq.String(2))
    NZBBSE24_TKN_H_LGTH_B1: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-LGTH-B1", alq.Integer)
    NZBBSE24_FILLER_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_1", alq.String(1))
    NZBBSE24_B1_LEN: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B1-LEN", alq.String(3))
    NZBBSE24_B1_USER_FLD1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B1-USER-FLD1", alq.String(1))
    NZBBSE24_B1_FIID: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B1-FIID", alq.String(4))
    NZBBSE24_B1_VER_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B1-VER-ID", alq.String(2))
    NZBBSE24_B1_NTWK_ID_CODE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-NTWK-ID-CODE", alq.Integer)
    NZBBSE24_B1_REF_NBR: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-REF-NBR", alq.BigInteger)
    NZBBSE24_B1_RESP_CODE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-RESP-CODE", alq.Integer)
    NZBBSE24_B1_POS_ENTRY_MDE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-POS-ENTRY-MDE", alq.Integer)
    NZBBSE24_B1_TERM_LOC: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-TERM-LOC", alq.Integer)
    NZBBSE24_B1_SWI_REF_NBR: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-SWI-REF-NBR", alq.Integer)
    NZBBSE24_B1_AIR_TKT_NBR: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-AIR-TKT-NBR", alq.BigInteger)
    NZBBSE24_B1_PROC_CODE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B1-PROC-CODE", alq.Integer)
    NZBBSE24_TKN_H_EYE_CATCHER_20: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-EYE-CATCHER-20", alq.String(2))
    NZBBSE24_TKN_H_ID_20: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-ID-20", alq.String(2))
    NZBBSE24_TKN_H_LGTH_20: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-LGTH-20", alq.Integer)
    NZBBSE24_FILLER_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_2", alq.String(1))
    NZBBSE24_20_LIFE_CYCL_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-20-LIFE-CYCL-IND", alq.String(1))
    NZBBSE24_20_TRACE_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-20-TRACE-ID", alq.String(15))
    NZBBSE24_20_VALID_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-20-VALID-CDE", alq.String(4))
    NZBBSE24_20_MONITOR_STAT: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-20-MONITOR-STAT", alq.String(1))
    NZBBSE24_20_ERR_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-20-ERR-IND", alq.String(1))
    NZBBSE24_TKN_H_EYE_CATCHER_B6: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-EYE-CATCHER-B6", alq.String(2))
    NZBBSE24_TKN_H_ID_B6: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-ID-B6", alq.String(2))
    NZBBSE24_TKN_H_LGTH_B6: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-LGTH-B6", alq.Integer)
    NZBBSE24_FILLER_3: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_3", alq.String(1))
    NZBBSE24_B6_ISS_SCRPT_DATA_LEN: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B6-ISS-SCRPT-DATA-LEN", alq.String(4))
    NZBBSE24_B6_SCRPT_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B6-SCRPT-DATA", alq.String(256))
    NZBBSE24_TKN_H_EYE_CATCHER_25: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-EYE-CATCHER-25", alq.String(2))
    NZBBSE24_TKN_H_ID_25: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-ID-25", alq.String(2))
    NZBBSE24_TKN_H_LGTH_25: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-LGTH-25", alq.Integer)
    NZBBSE24_FILLER_4: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_4", alq.String(1))
    NZBBSE24_25_TRAN_FEE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-TRAN-FEE", alq.String(19))
    NZBBSE24_25_ORIG_FEE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-ORIG-FEE", alq.String(19))
    NZBBSE24_25_TERM_SUR_PROF: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-TERM-SUR-PROF", alq.String(4))
    NZBBSE24_25_RVSL_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-RVSL-CDE", alq.String(1))
    NZBBSE24_25_FLAT_FEE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-FLAT-FEE", alq.String(19))
    NZBBSE24_25_PCNT_FEE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-PCNT-FEE", alq.String(1))
    NZBBSE24_25_MIN_MAX: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-MIN-MAX", alq.String(5))
    NZBBSE24_25_AUTH_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-AUTH-IND", alq.String(1))
    NZBBSE24_25_USER_FIELD1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-25-USER-FIELD1", alq.String(1))
    NZBBSE24_TKN_HEADER_SX: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-HEADER-SX", alq.String(10))
    NZBBSE24_TKN_H_EYE_CATCHER_SX: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-EYE-CATCHER-SX", alq.String(2))
    NZBBSE24_TKN_H_ID_SX: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-ID-SX", alq.String(2))
    NZBBSE24_TKN_H_LGTH_SX: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-LGTH-SX", alq.Integer)
    NZBBSE24_FILLER_5: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_5", alq.String(1))
    NZBBSE24_SX_FRMT_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-SX-FRMT-CDE", alq.String(2))
    NZBBSE24_SX_LGTH: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-SX-LGTH", alq.String(2))
    NZBBSE24_SX_RSTL_CDE_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-SX-RSTL-CDE-1", alq.String(1))
    NZBBSE24_SX_RSTL_CDE_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-SX-RSTL-CDE-2", alq.String(1))
    NZBBSE24_SX_EST_AMT: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-SX-EST-AMT", alq.String(12))
    NZBBSE24_SX_USER_FLD_MC: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-SX-USER-FLD-MC", alq.String(46))
    NZBBSE24_FILLER_6: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_6", alq.String(501))
    NZBBSE24_TKN_H_EYE_CATCHER_SE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-EYE-CATCHER-SE", alq.String(2))
    NZBBSE24_TKN_H_ID_SE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-ID-SE", alq.String(2))
    NZBBSE24_TKN_H_LGTH_CE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-LGTH-CE", alq.Integer)
    NZBBSE24_FILLER_7: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_7", alq.String(1))
    NZBBSE24_CE_AUTHN_IND_FLG_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-AUTHN-IND-FLG_1", alq.String(2))
    NZBBSE24_CE_CAP_TKN_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-CAP-TKN-DATA", alq.String(48))
    NZBBSE24_CE_CAP_TKN_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-CAP-TKN_1", alq.String(18))
    NZBBSE24_CE_UNPREDICT_NUM_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-UNPREDICT-NUM_1", alq.String(8))
    NZBBSE24_CE_CRNCY_CDE_1: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-CE-CRNCY-CDE_1", alq.Integer)
    NZBBSE24_CE_AMT_AUTH_1: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-CE-AMT-AUTH_1", alq.BigInteger)
    NZBBSE24_CE_APSN_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-APSN_1", alq.String(2))
    NZBBSE24_CE_RESP_ATC_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-RESP-ATC_1", alq.String(4))
    NZBBSE24_TKN_H_EYE_CATCHER_FB: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-EYE-CATCHER-FB", alq.String(2))
    NZBBSE24_TKN_H_ID_FB: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-ID-FB", alq.String(2))
    NZBBSE24_TKN_H_LGTH_FB: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-TKN-H-LGTH-FB", alq.Integer)
    NZBBSE24_FILLER_8: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_8", alq.String(1))
    NZBBSE24_FB_DATA_IND_FLG: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FB-DATA-IND-FLG", alq.String(2))
    NZBBSE24_FB_INFO_DATA_LEN: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FB-INFO-DATA-LEN", alq.String(4))
    NZBBSE24_FB_MC_PGM_PROTO: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FB-MC-PGM-PROTO", alq.String(1))
    NZBBSE24_FB_MC_DS_TXN_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FB-MC-DS-TXN-ID", alq.String(36))
    NZBBSE24_FB_USER_FLD: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FB-USER-FLD", alq.String(219))
    NZBBSE24_FILLER_9: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-FILLER_9", alq.String(1517))
    NZBBSE24_B0_LEN: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-LEN", alq.String(3))
    NZBBSE24_B0_USER_FLD1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-USER-FLD1", alq.String(1))
    NZBBSE24_B0_FIID: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-FIID", alq.String(4))
    NZBBSE24_B0_VER_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-VER-ID", alq.String(2))
    NZBBSE24_B0_LCL_TXN_TIME: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-LCL-TXN-TIME", alq.Integer)
    NZBBSE24_B0_LCL_TXN_DATE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-LCL-TXN-DATE", alq.Integer)
    NZBBSE24_B0_ADVCE_RSN_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-ADVCE-RSN-CDE", alq.Integer)
    NZBBSE24_B0_POS_ENTRY_MDE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-POS-ENTRY-MDE", alq.Integer)
    NZBBSE24_B0_RESP_CODE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-RESP-CODE", alq.Integer)
    NZBBSE24_B0_CRD_VRFY_RESULT: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-CRD-VRFY-RESULT", alq.String(1))
    NZBBSE24_B0_DBT_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-DBT-IND", alq.String(1))
    NZBBSE24_B0_DVLPMT_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-DVLPMT-IND", alq.String(1))
    NZBBSE24_B0_DEF_BILL_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-DEF-BILL-IND", alq.String(1))
    NZBBSE24_B0_PROC_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-PROC-CDE", alq.String(6))
    NZBBSE24_B0_ON_BEHALF: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-ON-BEHALF", alq.String(30))
    NZBBSE24_B0_MCHIP_PRO_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-MCHIP-PRO-IND", alq.String(2))
    NZBBSE24_B0_MCHIP_PROC_INFO: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-MCHIP-PROC-INFO", alq.String(1))
    NZBBSE24_B0_TRAN_FEE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-TRAN-FEE", alq.String(9))
    NZBBSE24_B0_ECOM_SEC_IND: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-ECOM-SEC-IND", alq.Integer)
    NZBBSE24_B0_AVS_RESULT: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-AVS-RESULT", alq.String(1))
    NZBBSE24_B0_ACCT_NUM_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-ACCT-NUM-IND", alq.String(1))
    NZBBSE24_B0_ADVC_DETL_CDE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-ADVC-DETL-CDE", alq.Integer)
    NZBBSE24_B0_AGENT_ID_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-AGENT-ID-CDE", alq.String(6))
    NZBBSE24_B0_PYMT_TXN_TYP: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-PYMT-TXN-TYP", alq.String(3))
    NZBBSE24_B0_CHIP_BIT_ERR: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-CHIP-BIT-ERR", alq.String(50))
    NZBBSE24_B0_CRD_LVL_RSLT: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-CRD-LVL-RSLT", alq.String(2))
    NZBBSE24_B0_MC_GTWY_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-MC-GTWY-IND", alq.String(8))
    NZBBSE24_B0_MC_ASSGN_ID: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-MC-ASSGN-ID", alq.String(6))
    NZBBSE24_B0_VPAN: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-VPAN", alq.String(19))
    NZBBSE24_B0_RTE_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-RTE-IND", alq.String(1))
    NZBBSE24_B0_VISA_MKT_DATA: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-VISA-MKT-DATA", alq.String(1))
    NZBBSE24_B0_POS_COND_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-POS-COND-CDE", alq.String(11))
    NZBBSE24_B0_PIN_SRV_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-PIN-SRV-CDE", alq.String(2))
    NZBBSE24_B0_PIN_CAP_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-PIN-CAP-CDE", alq.String(2))
    NZBBSE24_B0_AUTH_SA_DAT_TIM: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-AUTH-SA-DAT-TIM", alq.String(10))
    NZBBSE24_B0_FRAUD_SCORE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-FRAUD-SCORE", alq.String(3))
    NZBBSE24_B0_FRAUD_RSN_CDE: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-FRAUD-RSN-CDE", alq.String(2))
    NZBBSE24_B0_FRULE_ADJ_SCORE: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-FRULE-ADJ-SCORE", alq.Integer)
    NZBBSE24_B0_FRULE_RSN_CDE_1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-FRULE-RSN-CDE-1", alq.String(2))
    NZBBSE24_B0_FRULE_RSN_CDE_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-FRULE-RSN-CDE-2", alq.String(2))
    NZBBSE24_B0_PMT_INIT_CHAN: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-PMT-INIT-CHAN", alq.String(2))
    NZBBSE24_B0_TLE_CMPLNT_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-TLE-CMPLNT-IND", alq.String(1))
    NZBBSE24_B0_UKPT_CMPLT_IND: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-UKPT-CMPLT-IND", alq.String(1))
    NZBBSE24_B0_SANCTN_SCRN_SCR: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-B0-SANCTN-SCRN-SCR", alq.Integer)
    NZBBSE24_B0_FLD_ACI: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-B0-FLD-ACI", alq.String(1))
    NZBBSE24_S8_SF1: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-S8-SF1", alq.String(1))
    NZBBSE24_S8_SF2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-S8-SF2", alq.String(19))
    NZBBSE24_S8_SF3: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-S8-SF3", alq.String(4))
    NZBBSE24_CE_AUTHN_IND_FLG_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-AUTHN-IND-FLG_2", alq.String(2))
    NZBBSE24_CE_CAP_TKN_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-CAP-TKN_2", alq.String(18))
    NZBBSE24_CE_UNPREDICT_NUM_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-UNPREDICT-NUM_2", alq.String(8))
    NZBBSE24_CE_CRNCY_CDE_2: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-CE-CRNCY-CDE_2", alq.Integer)
    NZBBSE24_CE_AMT_AUTH_2: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-CE-AMT-AUTH_2", alq.BigInteger)
    NZBBSE24_CE_APSN_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-APSN_2", alq.String(2))
    NZBBSE24_CE_RESP_ATC_2: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-CE-RESP-ATC_2", alq.String(4))
    NZBBSE24_F3_TXN_TYP_IND: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-F3-TXN-TYP-IND", alq.Integer)
    NZBBSE24_F3_TRNSPRT_MDE_IND: orm.Mapped[int|None] = orm.mapped_column(
        "NZBBSE24-F3-TRNSPRT-MDE-IND", alq.Integer)
    NZBBSE24_F3_USER_FLD_ACI: orm.Mapped[str|None] = orm.mapped_column(
        "NZBBSE24-F3-USER-FLD-ACI", alq.String(4))
    
    member_prefix: orm.Mapped[str|None] = orm.mapped_column(alq.String(6),      # OK 
        alq.Computed("(left([NGBBSE24-HEAD-MBR-NUM],(6)))", persisted=True))    
    member_bucket: orm.Mapped[int|None] = orm.mapped_column(alq.Integer,        # OK
        alq.Computed("(abs(checksum([NGBBSE24-HEAD-MBR-NUM]))%(256))", persisted=True))

    PTLF_track: orm.Mapped[typ.Optional["PTLFTrack"]] = orm.relationship("PTLFTrack",
        back_populates="PTLF_raw")
