
# Recursos de Azure
- `data-fiserv`:      _Resource group_
- `fiserv-reports`:   _SQL server_      
- `fiserv-db`:        _SQL database_    ($5.25 USD)

# Otros recursos
- Se requiere instalar `unixodbc` aparte del pip. 
- Y actualizar mssql con pyodbc: 
```
$ brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
$ brew update
```

# Otras notas
- modificamos los formatos `S9(15)V99` por `S9(15)V(2)` de acuerdo a la longitud de 17. 


