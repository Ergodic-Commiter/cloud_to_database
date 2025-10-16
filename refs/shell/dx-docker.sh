python - <<'PY'
import os, sys
from azure.storage.blob import BlobServiceClient
conn = os.getenv("BlobConn")
bsc = BlobServiceClient.from_connection_string(conn)
gcc = bsc.get_container_client("mediospago")
for c in gcc.list_blobs(name_starts_with="fiserv/2025/8"):
    print("Blob:", c.name)
PY