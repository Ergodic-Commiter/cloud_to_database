Los archivos .txt están en proceso de mejoramiento. 

- Al leer los datos `PTLF_YYYY-MM-DD` y usando las especificaciones del Excel, 
cada columna se asigna un `TypeConverter` y se procesa de acuerdo a las reglas. 
- Estos _type converters_ forzan la conversión para no detener el proceso, pero
escriben el reporte en estos archivos.  