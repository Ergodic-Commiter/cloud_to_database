Uno desarrolla y después regresa a sus proyectos.  
En el inter, uno aprende y al regresar quisiera mejorar cosas.  

A nivel estratégico funcional, el proyecto requiere una implementación técnica robusta: 
- Correr en algún contenedor institucional.  
- Crecer a PRD.   
- Cargar archivos automáticamente y no manual.  

A nivel técnico personal:  
- Los logs imprimen mucha basura, y en general se implementaron con conciencia media.  
- La clase convertidora de tipos Converter puede empaquetarse aún mejor:  
  - Registros los tipos individuales automáticamente.  
  - Utilizar los Mixin para funcionalidades adicionales.  
- Estructura de conexión, infraestructura, servicios se puede revisar mejor.  

Ajustes de Versión 2. 
- PTLF_TRACK.data_date <=> PTLF_raw["NGBBSE24-AUTH-POST-DAT"] pero una es fecha y 
  la otra string.  Quién sabe cómo pasó eso. 
- 