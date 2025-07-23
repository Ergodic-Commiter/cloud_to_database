#!/bin/bash

# Ruta a Python 3.11 instalado vía Homebrew
PYTHON_PATH="/opt/homebrew/bin/python3.11"

# Validar si Python 3.11 está disponible
if [ ! -f "$PYTHON_PATH" ]; then
  echo "❌ Python 3.11 no está instalado. Ejecuta: brew install python@3.11"
  exit 1
fi

# Crear entorno virtual solo si no existe
if [ ! -d "venv-sqlsp" ]; then
  echo "🔧 Creando entorno virtual con Python 3.11..."
  $PYTHON_PATH -m venv venv-sqlsp
fi

# Activar entorno virtual
echo "🚀 Activando entorno virtual..."
source venv-sqlsp/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Exportar variables de entorno para Azure Identity
# Borrar secretos de variables.

export AZURE_TENANT_ID=""
export AZURE_CLIENT_ID=""
export AZURE_CLIENT_SECRET=""
export SERVER=""
export DATABASE="demo-adm-dev"
export ODBCINSTINI=/opt/homebrew/etc/odbcinst.ini
export ODBCINI=/opt/homebrew/etc/odbc.ini
export ODBCTRACE=1
export ODBCTRACEFILE=odbc.log


# Opcional: permitir bypass SSL en entornos con proxy corporativo
export DISABLE_SSL_VERIFY=1

# Ejecutar el script principal
echo "▶️ Ejecutando demo.py"
python3 demo.py
