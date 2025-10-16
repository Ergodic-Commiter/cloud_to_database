
poetry export -f requirements.txt --without-hashes -o azurefunc/requirements.txt

poetry install --with dev
poetry run {pytest, ...}
poetry shell 

# Azure functions

az storage blob upload --account-name $STORAGE_ACCOUNT_NAME \
  --account-key $STORAGE_ACCOUNT_KEY \
  --container-name mediospago \
  --file data/temp/zips/OneDrive_1013/PRD_TRXS_PTLF_2025-10-12.ZIP \
  --name fiserv/2025/10/12/PRD_TRXS_PTLF_2025-10-12.ZIP \
  --overwrite true

docker buildx --platofrm linux/amd64 build -f .\dockerfile.ci -t  "ptlf/blob-to-sql:1.0"
docker build -t ptlf/blob-to-sql:1.0 --file dockerfile.ci .
docker run --platform=linux/amd64 --rm -it --name myfunc -p 7071:80 \
  -e FUNCTIONS_WORKER_RUNTIME=python -e WEBSITES_INCLUDE_CLOUD_CERTS=true \
  -e AzureWebJobsStorage=$AZURE_JOB_STORAGE \
  -e BlobConn=$AZURE_BLOB_STORAGE ptlf/blob-to-sql:1.0

# Los comandos Docker-ACR necesitan permisos raros. 
docker tag "ptlf/blob-to-sql:1.0" "dataappsregistry.azurecr.io:1.0"
docker push "dataappsregistry.azurecr.io:1.0"

az acr build --file dockerfile.ci --registry $AZURE_CONTAINER --image ptlf/blob-to-sql:1.0 \
  --file dockerfile.ci .
  
# Para estos no tenemos permisos, asi que usamos `az acr build ...`
func azure functionapp publish "$APP" --python --script-root azurefunc --build remote
