# Fiserv FPSL, Controversias  

Este repositorio es el componente de programación correspondiente al proyecto de Controversias.  
La documentación se encuentra en el [_sharepoint_ de Medios de Pago II][medios].  
El _sharepoint_ anterior contiene vinculación a documentos de _OneDrive_, pero aún
se pudiera beneficiar de una presentación en el portal.  Para conocer tus comentarios, 
te agradeceré que me escribas por [Teams][teams]. 

- [Fiserv FPSL, Controversias](#fiserv-fpsl-controversias)
  - [Runbook de Azure](#runbook-de-azure)
    - [Instalación del repositorio](#instalación-del-repositorio)
  - [Reproducibilidad](#reproducibilidad)
  - [Pruebas de respaldo](#pruebas-de-respaldo)
    - [Recomendaciones de Github](#recomendaciones-de-github)


## Runbook de Azure
- `data-fiserv`:      _Resource group_
- `fiserv-reports`:   _SQL server_      
- `fiserv-db`:        _SQL database_    ($5.25 USD)
- `medios-pago-data-dev`: _Service Principal_  
- `mediospago`:       _Azure Container_ (ya existe)

El servidor SQL tiene muchas configuraciones truculentas: 
- Se revisan permisos para el usuario que crea las tablas.  
- Incluso si tiene un _service principal_, se tiene que agregar por aparte.  
- Y para esto, la identidad del servidor tiene que estar activada y tener permisos
  de leer Entra ID. 
- El _service principal_ tiene que tener permisos de lectura en el contenedor de Azure.  
  👀 `Contributor` no es suficiente para leer, se necesita `Blob Data Contributor`.  
  

### Instalación del repositorio
- La preparación de ambientes de Python se recomienda con `pyenv`. 
  En el [sitio de Pyenv][pyenv] se puede seguir la instalación.  
  Para la creación del ambiente:  
  ```
  $ pyenv install 3.12.2
  $ pyenv virtualenv 3.12.2 fiserv312
  ```  

- Se requiere instalar `unixodbc` aparte del pip.  

  Tenemos discrepancia en la versión de `unixodbc` para Infra (Juan José), y x-Datos (Diego).  
  Infra usó 17 y x-Datos, 18.  
  En la ejecución global se especifica en `src/db/__init__.py`.  
  Si necesita cambiar, favor de no "empujarlo" a la rama `main`.  

- Utilizamso  `mssql` con `pyodbc`.  Para Mac:  
  ```
  $ brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
  $ brew update
  ```

- El repositorio se clonar con `git`: 
  ```
  $ git clone https://github.com/diego-v_bineo/data-fiserv-ptlf.git <NOMBRE-LOCAL>
  $ pyenv activate fiserv312
  $ pyenv local
  $ pip install -r requirements.txt
  ```
  El nombre `fiserv312` no es a fuerzas, pero sí conviente.  
  En realidad nada de esto es a fuerzas, pero si nos ponemos filosóficos no avanzaremos
  en nuestro proyecto.  

- Se utiliza el Excel del Sharepoint: `Documents > Referencias > Columnas-PTLF.xlsx`.  
  La herramienta programática de _One Drive_ no está disponible, entonces se requiere lo siguiente:   
  - Hacer una copia en `./data/PTLF-cols.xlsx` 
  - Para cambios, actualizar en el _onedrive_ mencionado
  - Para facilitarlo, se puede crear un atajo: `./data/PTLF-cols-2.xlsx` 
  - Verificar que estén ignorados en `.gitignore`

- Las variables de ambiente se guardan en el archivo `.env`, favor de solicitar una copia con las 
variables relevantes.  
  También solicitar copias de los archivos de prueba `PTLF_2024-12-30.txt`


## Reproducibilidad  
- Modificamos los formatos `S9(15)V99` por `S9(15)V(2)` de acuerdo a la longitud de 17.
- También ajustamos los nombres de `Field Name` para que no hubiera repetidos y alguno que otro _typo_ 
  que se veía desajustado, se guarda en el Excel correspondiente.    


## Pruebas de respaldo  
- Se manejan dos carpetas paralelas:  `src` y  `tests`.   
- La teoría de pruebas unitarias indica que el código de `src` está respaldado por 
  pruebas de `tests`.  
  Las fallas de `src` se simplifican en `tests`, y al resolverse en `tests` deben 
  resolverse también en `src`.  
  A su vez, unas pruebas exitosas de `tests` deben garantizar una ejecución exitosa en `src`.  
- `pytest` está incluido en los requisitos, para ejecutar las pruebas:  
  `$ pytest test/test_{module}.py`  


### Recomendaciones de Github  
- Archivos de datos:  `NO`  
  Para pruebas los guardamos en `/data`, y aseguramos que se ignoren con `.gitignore`.  
  Para ejecución del día a día, se extraen de otros repositorios.  
- Variables de ambiente:  `NO`  
  Para desarrollo se leen del archivo `/.env` (incluído en `.gitignore`)  
  Para la ejecución se manejan identidades gestionadas por Azure, o en casos específicos  
  se alamacenan en un _keyvault_.  



[medios]: https://bineomex.sharepoint.com/sites/medios-pago-2/SitePages/ProjectHome.aspx
[teams]: https://teams.microsoft.com/l/chat/0/0?users=diego.v@bineo.com
[pyenv]: https://github.com/pyenv/pyenv
