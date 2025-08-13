# TypeConverter class does two things: 
#   - Factory Class for different types:  str, numeric, etc. 
#   - SuperClass of all the different types:  str, numeric, etc. 
from collections import namedtuple
from decimal import Decimal
import re
from typing import Any, ClassVar, Optional, Type

import sqlalchemy as alq
from sqlalchemy.dialects import mssql

RawSpecs = namedtuple('RawSpecs', "From,Length,Field Name,Format,Description"
        ",PCI DSS,Token,Comentarios, Nombre en PBI")
FieldSpecs = namedtuple('FieldSpecs', "Name1,From,Length,Format")


class TypeManager: 
    _registry = {}
    pytype: ClassVar[Optional[Type[Any]]] = None
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        if not hasattr(cls, 'pytype') or cls.pytype is None:
            raise TypeError(f"{cls.__name__} must define 'pytype'.")
        TypeManager._registry[cls.pytype] = cls

    def __init__(self, specs_row:RawSpecs): 
        self._specs = specs_row
    
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
        reg_fmt = r"^(?P<base>S?9|X)(?:\((?P<len>\d{1,4})\))?(?:V9(?P<v9>\d))?"      
        if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
            err_msg = f"Format string cannot be parsed for typer:\n{self}"
            raise ValueError(err_msg)        
        return reg_match.groups()
    
    def validate(self):
        raise NotImplementedError
    
    @classmethod
    def get_valid_types(cls, srs:RawSpecs):
        χ_valid = lambda pytype: cls._registry[pytype](srs).validate()
        return list(filter(χ_valid, cls._registry))

    @classmethod
    def from_specs(cls, srs:RawSpecs): 
        if len(valid_types := cls.get_valid_types(srs)) != 1: 
            err_msg = (f"Can't find unique validated type from: [{valid_types}]"
                "\nCheck validation functions for {s_row}")
            raise ValueError(err_msg)
        converter = cls._registry[valid_types[0]]
        return converter(srs)

    def mssql_col(self): 
        raise NotImplementedError

    def alq_mssql(self):  
        name = self.specs.Name1
        sql_col = self.mssql_col()
        return alq.Column(name, sql_col)

    def pd_lambda(self, with_name): 
        raise NotImplementedError
    

class StrConverter(TypeManager):
    pytype = str
    def validate(self): 
        base, _l, _v9 = self.format_groups
        return base == 'X'

    def mssql_col(self):
        _b, len0, _v9 = self.format_groups
        return mssql.VARCHAR(int(len0 or 1))
    
    def pd_lambda(self, with_name): 
        from_, to, name, _ = self.specs
        _b, _l, _v9 = self.format_groups
        λ_slice = lambda df: df['value'].str.slice(from_, to).str.split()
        return (name, λ_slice) if with_name else λ_slice

    
class IntConverter(TypeManager): 
    pytype = int
    def validate(self): 
        base, _l, v9 = self.format_groups
        return (base == '9') and (v9 is None)
    
    def mssql_col(self): 
        return mssql.INTEGER()
    
    def pd_lambda(self, with_name): 
        from_, len_, name, _fmt = self.specs
        λ_slice = (lambda df: df['value'].str.slice(from_, from_+len_)
            .str.split().astype(int))
        return (name, λ_slice) if with_name else λ_slice

class DecConverter(TypeManager): 
    pytype = Decimal
    def validate(self): 
        base, _l, v9 = self.format_groups
        return (base in ('9', 'S9')) and (v9 is not None)
    
    def mssql_col(self): 
        _b, len_, v9 = self.format_groups
        len1 = int(len_ or 1)
        dec1 = int(v9 or 0)
        prec = len1 + dec1
        scale = dec1 
        return mssql.DECIMAL(prec, scale)
            
    def pd_lambda(self, with_name): 
        from_, len_, name, _fmt = self.specs
        _b, _l, v9 = self.format_groups
        λ_slice = (lambda df: df['value'].str.slice(from_, from_+len_)
            .str.split().astype(float).div(10**int(v9)))
        return (name, λ_slice) if with_name else λ_slice
        

    