import pyodbc
import pandas as pd

from config import (
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    SERVER,
    DATABASE,
)

# Leer solo las primeras 100 filas del CSV original
column_names = [
    "ID_OPERACION", "ID_VERSION", "SECUENCIA", "ID_OPERACION_BIS", "ID_OPERACION_HIS",
    "FECHA_REPORTE", "FECHA_VALOR", "FECHA_VENCIMIENTO", "FECHA_EMISION", "FECHA_PAGO_INTERES",
    "FECHA_PAGO_CAPITAL", "ID_CLIENTE", "ID_CONTRAPARTE", "ID_CONTRAPARTE_HIS", "ID_GARANTE",
    "ID_SECTOR_INST", "ID_SECTOR_CONTRAPARTE", "ID_TIPO_PERSONA", "ID_SUB_TIPO_PERSONA",
    "ID_ENTIDAD", "ID_TIPO_ENTIDAD", "ID_TIPO_OPERACION", "ID_SUB_TIPO_OPERACION", "ID_MONEDA",
    "ID_TIPO_CAMBIO", "TIPO_TASA", "TASA_INTERES", "MONTO_ORIGINAL", "SALDO_OPERACION",
    "TIPO_GARANTIA", "ESTADO_OPERACION", "OPERACION_RELEVANTE", "CLASIFICACION_RIESGO",
    "PROVISION_OPERACION", "VALOR_DESEMBOLSADO", "VALOR_RECUPERADO", "FECHA_DESEMBOLSO",
    "FECHA_RECUPERACION", "TIPO_CAMBIO_PACTADO", "FECHA_TASA_FIJA", "GARANTIA_REAL",
    "GARANTIA_PERSONAL", "TIPO_PRODUCTO", "ID_TIPO_CLIENTE", "CODIGO_SECTORIAL",
    "ID_TIPO_INSTITUCION", "ID_CATEGORIA_CARTERA", "ID_MODALIDAD", "CALIFICACION_CARTERA",
    "FECHA_ULTIMA_CLASIFICACION", "PORCENTAJE_COBERTURA", "ID_GARANTIA", "CLASIFICACION_INTERNA"
]

df = pd.read_csv(
    "PTLF_2024-12-30",
    encoding="latin1",
    header=None,
    names=column_names,
    nrows=100
)



# Configurar conexión
conn_str = (
    "Driver=/opt/homebrew/lib/libmsodbcsql.17.dylib;"
    f"Server={SERVER};"
    f"Database={DATABASE};"
    "Authentication=ActiveDirectoryServicePrincipal;"
    f"UID={AZURE_CLIENT_ID};"
    f"PWD={AZURE_CLIENT_SECRET};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

print("🧪 Columnas detectadas:")
print(df.columns.tolist())
exit()
# Generar el insert dinámicamente
column_names = df.columns.tolist()
placeholders = ", ".join(["?"] * len(column_names))
column_list = ", ".join(f"[{col}]" for col in column_names)
sql = f"INSERT INTO ptlf_lo ({column_list}) VALUES ({placeholders})"

print(f"⚙️ Ejecutando inserciones sobre la tabla: ptlf_lo...")
for index, row in df.iterrows():
    values = [str(x) if pd.notnull(x) else None for x in row]
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(f"⚠️ Error en la fila {index}: {e}")

conn.commit()
print("✅ Insert completado para 100 registros.")
conn.close()
