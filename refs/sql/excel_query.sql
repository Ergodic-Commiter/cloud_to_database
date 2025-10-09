
ALTER VIEW dbo.v_PTLF_Token AS
SELECT dbo.[PTLF_raw].[NGBBSE24-HEAD-CRD-CARD-NUM] AS [num_tarjeta],
	CAST(dbo.[PTLF_raw].[NGBBSE24-AUTH-POST-DAT] AS DATE) AS [f_posteo], 
	dbo.[PTLF_raw].[NGBBSE24-AUTH-APPRV-CDE] AS [num_autorizacion],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-AMT-1] AS [monto_txn],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-TYP] AS [tipo_auth],
	dbo.[PTLF_raw].[NGBBSE24-C0-E-COM-FLG] AS [etiq_e-commerce],
	dbo.[PTLF_raw].[NGBBSE24-C0-AUTHN-COLL-IND] AS [estatus_ucaf],
	dbo.[PTLF_raw].[NGBBSE24-C4-TERM-ATTEND-IND] AS [tipo_terminal],
	dbo.[PTLF_raw].[NGBBSE24-C4-TERM-LOC-IND] AS [ubic_terminal],
	dbo.[PTLF_raw].[NGBBSE24-C4-CHLDR-PRES-IND] AS [t-habiente_presente],
	dbo.[PTLF_raw].[NGBBSE24-C4-CHLDR-ACT-TRM-IND] AS [tipo_cat],
	dbo.[PTLF_raw].[NGBBSE24-TERM-INPUT-CAP-IND] AS [tipo_input-tarjeta],
	dbo.[PTLF_raw].[NGBBSE24-CRDHLDR-ID-METHOD] AS [t-habiente_auth],
	dbo.[PTLF_raw].[NGBBSE24-B2-CRYPTO-INFO-DATA] AS [cripto_data],
	dbo.[PTLF_raw].[NGBBSE24-B2-TVR] AS [verif_terminal],
	dbo.[PTLF_raw].[NGBBSE24-B2-C-CRD-VRFY-RSLTS] AS [verif_tarjeta],
	dbo.[PTLF_raw].[NGBBSE24-B3-CVM-RSLTS] AS [verif_t-habiente],
	dbo.[PTLF_raw].[NGBBSE24-B4-TERM-ENTRY-CAP] AS [capacidad_terminal],
	dbo.[PTLF_raw].[NGBBSE24-B4-ARQC-VRFY] AS [verif_arqc],
	dbo.[PTLF_raw].[NZBBSE24-CE-CAP-TKN_1] AS [cap_token],
	dbo.[PTLF_raw].[NZBBSE24-B0-PMT-INIT-CHAN] AS [dispositivo_sin-contacto],
	dbo.[PTLF_raw].[NZBBSE24-S8-SF2] AS [archivo_pan],
	dbo.[PTLF_raw].[NZBBSE24-CE-CAP-TKN_2] AS [cap_comercio-e] 
FROM dbo.[PTLF_raw]; 
GO

-- Make it an index
-- Error porque hay valores repetidos:  (000540208A6ZV6K4322, 250812, 158510, 0.00)
CREATE UNIQUE NONCLUSTERED INDEX UX_Card_PostDate_Auth_Amount
ON dbo.PTLF_raw ([NGBBSE24-HEAD-CRD-CARD-NUM], [NGBBSE24-AUTH-POST-DAT], 
	[NGBBSE24-AUTH-SEQ-NUM], [NGBBSE24-AUTH-AMT-1], [NGBBSE24-AUTH-TYP])
INCLUDE ([NGBBSE24-C0-E-COM-FLG], [NGBBSE24-C0-AUTHN-COLL-IND], [NGBBSE24-C4-TERM-ATTEND-IND],
	[NGBBSE24-C4-TERM-LOC-IND], [NGBBSE24-C4-CHLDR-PRES-IND], [NGBBSE24-C4-CHLDR-ACT-TRM-IND], 
	[NGBBSE24-TERM-INPUT-CAP-IND], [NGBBSE24-CRDHLDR-ID-METHOD], [NGBBSE24-B2-CRYPTO-INFO-DATA], 
	[NGBBSE24-B2-TVR], [NGBBSE24-B2-C-CRD-VRFY-RSLTS], [NGBBSE24-B3-CVM-RSLTS], 
	[NGBBSE24-B4-TERM-ENTRY-CAP], [NGBBSE24-B4-ARQC-VRFY], [NZBBSE24-CE-CAP-TKN_1], 
	[NZBBSE24-B0-PMT-INIT-CHAN], [NZBBSE24-S8-SF2], [NZBBSE24-CE-CAP-TKN_2]); 	

-- Query de repetidos: 

select v.* 
from [dbo].[PTLF_raw] v 
join (
	select count(*) as repetidos, 
		num_tarjeta, f_posteo, num_autorizacion, monto_txn
	from v_ptlf_token
	group by num_tarjeta, f_posteo, num_autorizacion, monto_txn) g
on v.[NGBBSE24-HEAD-CRD-CARD-NUM] = g.num_tarjeta 
	and v.[NGBBSE24-AUTH-POST-DAT] = g.f_posteo 
	and v.[NGBBSE24-AUTH-SEQ-NUM] = g.num_autorizacion 
	and v.[NGBBSE24-AUTH-AMT-1] = g.monto_txn
where g.repetidos > 1 
order by f_posteo, monto_txn, num_autorizacion
