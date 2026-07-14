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
- Las fechas, datetimes, y times se guardan como strings.  Cambiarlos a fechas. 
- Cuando un day-data-flow no se sube completo, a veces se queda la entrada de track, 
  y crea problemas para comletarlo.  Hay que "ptlf data delete <el día>" y volver 
  a subirlo. 