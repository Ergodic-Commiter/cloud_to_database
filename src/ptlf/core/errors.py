
# pylint:disable=invalid-name

class ErrorControversias(Exception):
    """Base de errores en flujo de PTLF."""

class COBOL_FormatError(ErrorControversias): 
    def __init__(self, *args): 
        super().__init__(f"Error de formato COBOL: {args}")

class UniqueConverterError(ErrorControversias): 
    def __init__(self, *args): 
        super().__init__(f"Error de convertidor: {args}")

class PTLFConnError(ErrorControversias):
    def __init__(self, process): 
        super().__init__(f"Error de conexión en {process}.")

class KeyCredentialsError(ErrorControversias, KeyError):
    def __init__(self, key, process): 
        super().__init__(f"La llave {key} no es aceptada en proceso {process}.")

class ZipPTLF_Error(ErrorControversias): 
    def __init__(self, zfile): 
        super().__init__(f"El a-Zip {zfile} no tiene formato de PTLF.")

class SpecsPTLF_Error(ErrorControversias): 
    def __init__(self, col): 
        super().__init__(f"La columna {col} no existe en especificaciones.")

class FormatCOBOL_Error(ErrorControversias): 
    def __init__(self, cformat): 
        super().__init__(f"El formato {cformat} no se puede procesar.")
    
class UniqueValidatorError(ErrorControversias): 
    def __init__(self, col): 
        super().__init__(f"La especificación {col} no tiene validación única.")

class PandasConversionError(ErrorControversias):
    def __init__(self, col, typeid): 
        super().__init__(f"Columna {col} de tipo {typeid} no puede convertirse en pandas.")

class PTLF_FlowError(ErrorControversias): 
    def __init__(self, dfile, event):
        self.event = event 
        super().__init__(f"Fallo en flujo: '{dfile}'-'{event}'")

class PTLFReadError(ErrorControversias):
    def __init__(self, dfile, reason):
        super().__init__(f"Fallo de lectura: '{dfile}' debido a '{reason}'.")
        self.reason = reason

class PTLFUploadError(ErrorControversias): 
    def __init__(self, dfile, reason):
        super().__init__(f"Fallo de carga: '{dfile}' debido a '{reason}'.")
        self.reason = reason