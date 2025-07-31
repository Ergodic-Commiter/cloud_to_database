# TypeConverter class does two things: 
#   - Factory Class for different types:  str, numeric, etc. 
#   - SuperClass of all the different types:  str, numeric, etc. 
from collections import namedtuple
import re

import sqlalchemy as alq
from sqlalchemy.dialects import mssql

FieldSpecs = namedtuple('FieldSpecs', "Name1,From,Length,Format")

class TypeManager: 
    _registry = {}
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        if not hasattr(cls, 'pytype') or cls.pytype is None:
            raise TypeError(f"{cls.__name__} must define 'pytype'.")
        TypeManager._registry[cls.pytype] = cls

    def __init__(self, df_specs): 
        self._specs = df_specs
    
    @property
    def specs(self):
        specs_dict = self._specs._asdict()
        return FieldSpecs(*map(specs_dict.get, FieldSpecs._fields))

    def __repr__(self):
        return f"<{self.__class__.__name__}; pytype={self.pytype}; specs={self.specs}>"

    @property
    def format_groups(self): 
        """TypeManager subclasses use format_groups to choose their type."""
        # COBOL: (S?9|X)\((\d+)\)(V9(9|\(\d\)))?
        # S9(n), 9(n), X(n), S9(n)V9(k), 9(n)V99... 
        fmt_str = self.specs.Format
        reg_fmt = r"^(S?9|X)(?:\((\d{1,4})\))?(?:V9(\d))?"
        if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
            err_msg = f"Format string cannot be parsed for typer:\n{self}"
            raise ValueError(err_msg)        
        return reg_match.groups()
    
    def validate(self):
        raise NotImplementedError
    
    @classmethod
    def get_valid_types(cls, specs_srs):
        χ_valid = lambda pytype: cls._registry[pytype](specs_srs).validate()
        return list(filter(χ_valid, cls._registry))

    @classmethod
    def from_specs(cls, specs_srs): 
        if len(valid_types := cls.get_valid_types(specs_srs)) != 1: 
            err_msg = (f"Can't find unique validated type from: [{maybes}]"
                "\nCheck validation functions for {s_row}")
            raise ValidationError(err_msg)
        converter = cls._registry[valid_types[0]]
        return converter(specs_srs)

    def mssql_col(self): 
        raise NotImplementedError

    def alq_mssql(self): 
        name = self.specs.Name1
        sql_col = self.mssql_col()
        return alq.Column(name, sql_col)

    def pandas_lambda(self, with_name): 
        raise NotImplementedError
    

class StrConverter(TypeManager):
    pytype = str
    def validate(self): 
        base0, _l0, v9 = self.format_groups
        return base0 == 'X'

    def mssql_col(self):
        _b0, len0, _v9 = self.format_groups
        return mssql.VARCHAR(int(len0 or 1))
    
    def pandas_lambda(self, with_name): 
        from_, to, name, _ = self.specs
        b0, l0, _ = self.format_groups
        λ_slice = lambda df: df['value'].str.slice(from_, to).str.split()
        return (name, λ_slice) if with_name else λ_slice

    
class IntConverter(TypeManager): 
    pytype = int
    def validate(self): 
        base0, _l0, v9 = self.format_groups
        return (base0 == '9') and (v9 is None)
    
    def mssql_col(self): 
        _b0, len0, _v9 = self.format_groups
        return mssql.INTEGER(int(len0 or 1))
    
    def pandas_lambda(self, with_name): 
        from_, to, name, _fmt = self.specs
        λ_slice = (lambda df: df['value'].str.slice(from_, to)
            .str.split().astype(int))
        return (name, λ_slice) if with_name else λ_slice

class DecConverter(TypeManager): 
    pytype = float
    def validate(self): 
        base0, len0, v9 = self.format_groups
        return (base0 in ('9', 'S9')) and (v9 is not None)
    
    def mssql_col(self): 
        _b0, len0, v9 = self.format_groups
        len1 = int(len0 or 1)
        dec1 = int(v9 or 0)
        prec = len1 + dec1
        scale = dec1 
        return mssql.DECIMAL(prec, scale)
            
    def pandas_lambda(self, with_name): 
        from_, to, name, _fmt = self.specs
        _base, _len, v9 = self.format_groups
        λ_slice = (lambda df: df['value'].str.slice(from_, to)
            .str.split().astype(float).div(10**int(v9)))
        return (name, λ_slice) if with_name else λ_slice
        

    