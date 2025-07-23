
# Recursos de Azure
- `data-fiserv`:      _Resource group_
- `fiserv-reports`:   _SQL server_      
- `fiserv-db`:        _SQL database_    ($5.25 USD)

El servidor SQL tiene muchas configuraciones truculentas: 
- Se revisan permisos para el usuario que crea las tablas.  
- Incluso si tiene un service principal, se tiene que agregar por aparte.  
- Y para esto, la identidad del servidor tiene que estar activada y tener permisos
  de leer Entra ID. 
  

# Otros recursos
- Se requiere instalar `unixodbc` aparte del pip. 
- Y actualizar mssql con pyodbc: 
```
$ brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
$ brew update
```

# Otras notas
- modificamos los formatos `S9(15)V99` por `S9(15)V(2)` de acuerdo a la longitud de 17.

# Instalación de Python
- Una forma recomendada de manejar ambientes de Python es mediante `pyenv`.  
- Revisar el (sitio de Pyenv)[pyenv] para la instalación.  
```
$ pyenv install 3.12.2
$ pyenv virtualenv 3.12.2 fiserv312
$ pyenv activate fiserv312
$ pyenv local
$ pip install -r requirements.txt
```  

pyenv: [https://github.com/pyenv/pyenv]


