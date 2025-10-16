## Build & Push
az login
RG="<rg>" ; LOC="eastus" ; APP="ptlf-func-app" ; PLAN="ptlf-func-plan"
ACR="ptlfacr$RANDOM" ; IMG="fiserv-ptlf-func:1.0.0"

az acr create -g "$RG" -n "$ACR" --sku Basic
az acr login -n "$ACR"
ACR_LOGIN="$ACR.azurecr.io"
az login

docker buildx build --platform linux/amd64 -t "$ACR_LOGIN/$IMG" .
docker push "$ACR_LOGIN/$IMG"
# A veces no funciona docker, y usamos az acr build. 

AZURE_CONTAINER="<the container>"
az acr build --registry $AZURE_CONTAINER\
    --image funcs/ptlf:latest --file dockerfile.ci .

## Plan & App
az appservice plan create -g "$RG" -n "$PLAN" -l "$LOC" --sku EP1 --is-linux
az functionapp create -g "$RG" -p "$PLAN" -n "$APP" \
  --functions-version 4 \
  --deployment-container-image-name "$ACR_LOGIN/$IMG" \
  --assign-identity

# Let the app pull the image
PRINCIPAL_ID=$(az functionapp identity show -g "$RG" -n "$APP" --query principalId -o tsv)
ACR_ID=$(az acr show -g "$RG" -n "$ACR" --query id -o tsv)
az role assignment create --assignee "$PRINCIPAL_ID" --role AcrPull --scope "$ACR_ID"

jq -r '.Values | to_entries[] | select(.key!="IsEncrypted") | "\(.key)=\(.value)"' local.settings.json \
| xargs -I{} az functionapp config appsettings set -g <rg> -n "$APP" --settings {}