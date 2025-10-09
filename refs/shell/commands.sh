
poetry export -f requirements.txt --without-hashes -o azurefunc/requirements.txt

poetry install --with dev
poetry run {pytest, ...}
poetry shell 

# Azure functions
poetry build -f wheel
pip install dist/ptlf-... 
