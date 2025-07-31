
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

Tenemos discrepancia en la versión de `unixodbc` para Infra (Juan José), y x-Datos (Diego).  
Infra usó 17 y x-Datos, 18.  
En la ejecución global se especifica en `src/db/__init__.py`.  
Si necesitan cambiarlo, procuren no "empujarlo" a la rama `main`.  

# Otras notas
- Modificamos los formatos `S9(15)V99` por `S9(15)V(2)` de acuerdo a la longitud de 17.
- También ajustamos los nombres de `Field Name` para que no hubiera repetidos y alguno que otro typo 
  que se veía desajustado, se guarda en el Excel correspondiente.    

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

# Pruebas de respaldo  
- Se manejan dos carpetas paralelas:  `src` y  `tests`.   
- La teoría de pruebas unitarias sugiere que el código de `src` está respaldado por 
  pruebas de `tests`.  
  Las fallas de `src` se simplifican en `tests`, y al resolverse en `tests` deben 
  resolverse también en `src`.  
  A su vez, unas pruebas exitosas de `tests` deben garantizar una ejecución exitosa en `src`.  
- Para ejecutar las pruebas:  
  `$ pytest test/test_{module}.py`  


# Recomendaciones de Github  
- Archivos de datos:  NO.  
  Para pruebas los guardamos en `/data`, y aseguramos que se ignoren con `.gitignore`.  
  Para ejecución del día a día, se extraen de otros repositorios.  
- Variables de ambiente:  NO. 
  Para desarrollo se leen del archivo `/.env` (incluído en `.gitignore`)  
  Para la ejecución se manejan identidades gestionadas por Azure, o en casos específicos  
  se alamacenan en un _keyvault_.  




pyenv: [https://github.com/pyenv/pyenv]
