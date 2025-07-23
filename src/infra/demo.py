import pyodbc
import os

# Variables desde entorno
tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
server = os.getenv("SERVER")
database = os.getenv("DATABASE")


# Conexión con ODBC Driver 17
conn_str = (
    "Driver=/opt/homebrew/lib/libmsodbcsql.17.dylib;"
    f"Server={server};"
    f"Database={database};"
    "Authentication=ActiveDirectoryServicePrincipal;"
    f"UID={client_id};"
    f"PWD={client_secret};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

# Atributo 1256 = SQL_COPT_SS_ACCESS_TOKEN
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT SUSER_SNAME(), DB_NAME()")
user, db = cursor.fetchone()

print(f"✅ Conectado como: {user}")
print(f"📂 Base de datos activa: {db}")
