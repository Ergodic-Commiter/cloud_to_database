
ALTER VIEW dbo.v_PTLF_Fraudes AS
SELECT 
	dbo.[PTLF_raw].[NGBBSE24-HEAD-CRD-CARD-NUM] AS [Tarjeta],  --VARCHAR 
	dbo.[PTLF_raw].[NGBBSE24-AUTH-APPRV-CDE] AS [Codigo_Aprov],  --varchar
	CAST(dbo.[PTLF_raw].[NGBBSE24-AUTH-POST-DAT] AS DATE) AS [Fecha_Trans],  --DATE
	dbo.[PTLF_raw].[NGBBSE24-AUTH-TYP] AS [Tipo_Auth],  --integer
	dbo.[PTLF_raw].[NGBBSE24-HEAD-CRD-FIID] AS [FID],  
	CAST(dbo.[PTLF_raw].[NGBBSE24-AUTH-TRAN-DAT] AS DATE) AS [Fecha_Posteo],
	dbo.[PTLF_raw].[NGBBSE24-HEAD-RETL-ID] AS [Afiliacion],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-TERM-OWNER-NAME] AS [Comercio],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-TERM-CITY] AS [Ciudad],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-TERM-ST] AS [Estado],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-TERM-CNTRY-CDE] AS [Pais],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-RETL-SIC-CDE] AS [SIC_CDE],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-AMT-1] AS [Monto],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-PT-SRV-ENTRY-MDE] AS [Entry_Mode],
	dbo.[PTLF_raw].[NGBBSE24-AUTH-ORIG-CRNCY-CDE] AS [Moneda_Impot_Origen],
	dbo.[PTLF_raw].[NGBBSE24-C0-CVD-FLD-PRESENT] AS [CVV],
	dbo.[PTLF_raw].[NGBBSE24-CRDHLDR-ID-METHOD] AS [QPS],
	dbo.[PTLF_raw].[NGBBSE24-CH-CRD-VRFY-FLG2] AS [V_Flag],
	dbo.[PTLF_raw].[NGBBSE24-B3-CVM-RSLTS] AS [PIN] 
FROM dbo.[PTLF_raw]
GO


select g.*, f.*
from (select Tarjeta, Codigo_Aprov, Fecha_Trans, Tipo_Auth,
	count(*) as n_txns
	from v_PTLF_Fraudes
	group by Tarjeta, Codigo_Aprov, Fecha_Trans, Tipo_Auth
	) g
join dbo.v_PTLF_Fraudes f
on g.Tarjeta = f.Tarjeta AND g.Codigo_Aprov = f.Codigo_Aprov and 
	g.Fecha_Trans = f.Fecha_Trans and g.Tipo_Auth = f.Tipo_auth
where n_txns > 1 
order by n_txns desc, Codigo_Aprov
GO


CREATE UNIQUE NONCLUSTERED INDEX UX_PTLF_Fraudes
ON dbo.PTLF_raw ([NGBBSE24-AUTH-TYP], [NGBBSE24-AUTH-POST-DAT], 
	[NGBBSE24-HEAD-CRD-CARD-NUM], [NGBBSE24-AUTH-APPRV-CDE])
INCLUDE (
	[NGBBSE24-HEAD-CRD-FIID], [NGBBSE24-AUTH-TRAN-DAT], 
	[NGBBSE24-HEAD-RETL-ID], [NGBBSE24-AUTH-TERM-OWNER-NAME], 
	[NGBBSE24-AUTH-TERM-CITY], [NGBBSE24-AUTH-TERM-ST], 
	[NGBBSE24-AUTH-TERM-CNTRY-CDE], [NGBBSE24-AUTH-RETL-SIC-CDE], 
	[NGBBSE24-AUTH-AMT-1], [NGBBSE24-AUTH-PT-SRV-ENTRY-MDE], 
	[NGBBSE24-AUTH-ORIG-CRNCY-CDE], [NGBBSE24-C0-CVD-FLD-PRESENT], 
	[NGBBSE24-CRDHLDR-ID-METHOD], [NGBBSE24-CH-CRD-VRFY-FLG2], 
	[NGBBSE24-B3-CVM-RSLTS] )
WHERE [NGBBSE24-AUTH-APPRV-CDE] != '00000000'; 	
GO
DROP INDEX UX_Card_PostDate_Auth_Amount ON dbo.PTLF_raw; 