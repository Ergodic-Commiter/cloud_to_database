az login
AZURE_CONTAINER="<the container>"
az acr build --registry $AZURE_CONTAINER\
    --image funcs/ptlf:latest --file dockerfile.ci .