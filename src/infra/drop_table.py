import pyodbc
from config import (
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    SERVER,
    DATABASE,
) 

server = SERVER
database = DATABASE
client_id = AZURE_CLIENT_ID
client_secret = AZURE_CLIENT_SECRET

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


print("🔍 Variables cargadas:")
print(f"SERVER={server}")
print(f"DATABASE={database}")
print(f"CLIENT_ID={client_id}")
print(f"SECRET is set: {client_secret is not None}")

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS ptlf_lo")
conn.commit()

print("🧨 Tabla 'ptlf_lo' eliminada.")
conn.close()
