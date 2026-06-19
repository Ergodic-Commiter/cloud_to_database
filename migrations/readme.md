# Resumen
La herramienta *Alembic* sirve para gestionar la base de datos sobre la que opera 
el proyecto.  
En un inicio usamos scripts de SQL cuyos comandos guardamos en la carpeta `refs/sql/...`.  
Estos comandos se copian manualmente, y eso ya representa un problema.  

El objetivo de Alembic es quitar el mantenimiento manual y hacerlo programático.  
El nombre de `migrations` viene de la similitud con la herramienta correspondiente
de Django.  
