
poetry export -f requirements.txt --without-hashes -o azurefunc/requirements.txt

poetry install --with dev
poetry run {pytest, ...}
poetry shell 

# Azure functions



az storage blob upload --account-name $STORAGE_ACCOUNT_NAME \
  --account-key $STORAGE_ACCOUNT_KEY \
  --container-name $STORAGE_CONTAINER \
  --file data/temp/zips/OneDrive_1013/PRD_TRXS_PTLF_2025-10-12.ZIP \
  --name fiserv/2025/10/12/PRD_TRXS_PTLF_2025-10-12.ZIP \
  --overwrite true

### Build Docker y Push ❌
# Dev Vars
RG=data-fiserv
IMG=$CONTAINER_IMAGE
TAG=v1.0
ACR=$AZURE_CONTAINER
FUNC=$AZURE_FUNCTION
FQ_IMG=$ACR.azurecr.io/$IMG:$TAG
RG2=rg-common-data-dev

docker buildx build --platform=linux/amd64 -f dockerfile.ci -t "$IMG:$TAG" . 
docker build -t $IMG:$TAG --file dockerfile.ci .

docker run --platform=linux/amd64 --rm -it --name myfunc -p 7071:80 \
  --env-file ./.env_docker \
  -e FUNCTIONS_WORKER_RUNTIME=python \
  -e AzureWebJobsStorage=$AZURE_JOB_STORAGE \
  -e BlobConn=$AZURE_BLOB_STORAGE \
  $IMG:$TAG

docker run --platform=linux/amd64 --rm -it --name myfunc -p 8080:80 \ 
  --env-file ./.env_docker \
  -e FUNCTIONS_WORKER_RUNTIME=python -e WEBSITES_INCLUDE_CLOUD_CERTS=true \
  -e AzureWebJobsStorage=$AZURE_JOB_STORAGE \
  -e BlobConn=$AZURE_BLOB_STORAGE \
  -e AzureWebJobsSecretStorageType=Files \
  -e AzureFunctionsJobHost__logging__logLevel__default=Debug \
  -e AzureFunctionsJobHost__logging__logLevel__Host.Results=Information \
  -e AzureFunctionsJobHost__extensions__blobs__logging__logLevel=Debug \
  $IMG:$TAG
# Before -p 7071:80, then tried 8080:80


# Los comandos Docker-ACR necesitan permisos raros.  ❓
docker tag "$IMG:$TAG" "$ACR.azurecr.io:1.0"

# ❌ push reference tag doesn't exist. 
az acr login -n $ACR
docker push $FQ_IMG

## Build ACR directo ✅
az acr build --file dockerfile.ci --registry $ACR --image $IMG:$TAG \
  --file dockerfile.ci .

### Ahora la función.
## Un principal ✅ 
az functionapp identity assign -g $RG -n $FUNC
ACR_ID=$(az acr show -n $ACR -g $RG2 --query id -o tsv)
PRINCIPAL_ID=$(az functionapp identity show -g $RG -n $FUNC --query principalId -o tsv)
#... and assign ❌ Authorization failed. 
az role assignment create --assignee $PRINCIPAL_ID --role AcrPull --scope $ACR_ID


# B) container image on the function ❓ no credential for ACR, lookup. 
az functionapp config container set \
  -g $RG -n $FUNC \
  --docker-custom-image-name $FQ_IMG \
  --registry-server https://$ACR.azurecr.io

# C) Application Settings
az functionapp config container set \
  -g $RG -n $FUNC \
  --image $FQ_IMG \
  --docker-registry-server-url https://$ACR.azurecr.io

az functionapp config appsettings set -g $RG -n $FUNC \
  --settings FUNCTIONS_WORKER_RUNTIME=custom WEBSITES_PORT=80

az functionapp config appsettings set -g $RG -n $FUNC --settings \
  SQL_SERVER=fiserv-reports.database.windows.net \
  SQL_DATABASE=fiserv-db \
  AZURE_TENANT_ID=$AZURE_TENANT_ID \
  AZURE_CLIENT_ID=$AZURE_CLIENT_ID \
  AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET \
  ODBC_DRIVER=ODBC\ Driver\ 18\ for\ SQL\ Server



# Publish funciona pero se hizo en otro contexto. ✅ 
func azure functionapp publish "$FUNC" --python --script-root azurefunc --build remote


#