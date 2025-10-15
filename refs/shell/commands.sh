
poetry export -f requirements.txt --without-hashes -o azurefunc/requirements.txt

poetry install --with dev
poetry run {pytest, ...}
poetry shell 

# Azure functions
poetry build -f wheel
pip install dist/ptlf-... 

az storage blob upload \
  --account-name $STORAGE_ACCOUNT_NAME \
  --account-key $STORAGE_ACCOUNT_KEY \
  --container-name mediospago \
  --file data/temp/zips/OneDrive_1013/PRD_TRXS_PTLF_2025-10-12.ZIP \
  --name fiserv/2025/10/12/PRD_TRXS_PTLF_2025-10-12.ZIP \
  --overwrite true

az acr build --file dockerfile.ci --registry $AZURE_CONTAINER --image ptlf/blob-to-sql:1.0 .

# Para estos no tenemos permisos, asi que usamos `az acr build ...`
docker buildx --platofrm linux/amd64 build -f .\dockerfile.ci -t  "ptlf/blob-to-sql:1.0"
docker tag "ptlf/blob-to-sql:1.0" "dataappsregistry.azurecr.io:1.0"
docker push "dataappsregistry.azurecr.io:1.0"

