from collections import namedtuple
from decimal import Decimal
from operator import attrgetter as ɑ
import re
from typing import Any, ClassVar, Optional, Type

import pandas as pd
import sqlalchemy as alq
from sqlalchemy.dialects import mssql

from .helpers import classproperty, noner, specs_dicter
# pylint:disable=no-member


RawSpecs = namedtuple('RawSpecs', "From,Length,Field_Name,Format,Description,"
        "PCI_DSS,Token,Comentarios,Nombre_en_PBI")

def field_slice(self):
    ff, ll = ɑ('From', 'Length')(self)
    return slice(ff, ff+ll)
FieldSpecs = namedtuple('FieldSpecs', "Name1,From,Length,Format")
FieldSpecs.slice = property(field_slice)


class TypeManager: 
    """A factory and mixing class of converters for different types. 
    Each converter reads a RawSpecs tuple representing a column of a wider table.  
    """
    _registry = {}
    typeid: ClassVar[Optional[str]] = None
    pytype: ClassVar[Optional[Type[Any]]] = None
    _pandas_dtype: ClassVar[Optional[object]] = None

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not hasattr(cls, 'typeid') or cls.typeid is None:
            raise TypeError(f"{cls.__name__} must define 'typeid'.")
        TypeManager._registry[cls.typeid] = cls

    def __init__(self, raw_row:RawSpecs):
        specs_dict = specs_dicter(RawSpecs._fields)(raw_row)
        self._specs = RawSpecs(**specs_dict)

    def __repr__(self):
        return f"<{self.__class__.__name__}; typeid={self.typeid}; specs={self.specs}>"

    @classproperty
    def pandas_dtype(cls):                  # pylint:disable=no-self-argument
        return cls._pandas_dtype or cls.pytype
    
    @property
    def specs(self) -> FieldSpecs:
        raw = self._specs
        spec_map = dict(
            Name1 = raw.Name1, 
            From = int(raw.From)-1,     # adjust to python starting at 0.  
            Length = int(raw.Length), 
            Format = raw.Format)
        return FieldSpecs(**spec_map)

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
        base, len_, v9 = reg_match.groups()
        return base, int(len_ or 1), noner(int)(v9)

    def validate(self):
        raise NotImplementedError
    
    @classmethod
    def get_valid_types(cls, srs:RawSpecs):
        χ_valid = lambda typeid: cls._registry[typeid](srs).validate()
        return list(filter(χ_valid, cls._registry))

    @classmethod
    def from_specs(cls, raw_row:RawSpecs): 
        if len(valid_types := cls.get_valid_types(raw_row)) != 1: 
            err_msg = (f"Can't find unique validated type from: [{valid_types}]"
                "\nCheck validation functions for {raw_row}")
            raise ValueError(err_msg)
        converter = cls._registry[valid_types[0]]
        return converter(raw_row)

    def mssql_col(self): 
        raise NotImplementedError

    def alq_mssql(self):  
        name = self.specs.Name1
        sql_col = self.mssql_col()
        return alq.Column(name, sql_col)

    def pd_fromrow(self, row_name, with_name): 
        raise NotImplementedError

    def pd_fromstr(self, with_name): 
        raise NotImplementedError
    

class StrConverter(TypeManager):
    typeid = 'str'
    pytype = str
    _pandas_dtype = 'string'
    def validate(self): 
        base, _l, _v9 = self.format_groups
        return base == 'X'

    def mssql_col(self):
        _b, len_, _v9 = self.format_groups
        return mssql.VARCHAR(len_)
    
    def pd_fromrow(self, row_name=None, with_name=False): 
        name, slice_ = ɑ('Name1', 'slice')(self.specs)
        λ_slice = (lambda df: df['value'].str[slice_].str.strip()
            .replace('', pd.NA))
        return (name, λ_slice) if with_name else λ_slice

    def pd_fromstr(self, with_name=False): 
        name = self.specs.Name1 
        λ_mutate = lambda df: df[name].str.strip()
        return (name, λ_mutate) if with_name else λ_mutate
    

class IntConverter(TypeManager): 
    typeid = 'int'
    pytype = int
    _pandas_dtype = 'Int64'
    def validate(self): 
        base, len_, v9 = self.format_groups
        return (base == '9') and (len_ <= 9) and (v9 is None)
    
    def mssql_col(self): 
        return mssql.INTEGER()
    
    def pd_fromrow(self, row_name=None, with_name=False): 
        row_name = row_name or 'value'
        name, slice_ = ɑ('Name1', 'slice')(self.specs)
        def λ_slice(df): 
            try: 
                sliced = (df[row_name].str[slice_].str.strip()
                    .replace('', pd.NA).astype(self.pandas_dtype))
                return sliced
            except ValueError as ee: 
                err_msg = f"FromRow Error on Row {self}"
                raise ValueError(err_msg) from ee
        return (name, λ_slice) if with_name else λ_slice

    def pd_fromstr(self, with_name): 
        name = self.specs.Name1
        λ_mutate = (lambda df: df[name].str.strip()
            .replace('', pd.NA).astype(self.pandas_dtype))
        return (name, λ_mutate) if with_name else λ_mutate

class BigIntConverter(IntConverter): 
    typeid = 'bigint'
    def validate(self): 
        base, len_, v9 = self.format_groups
        return (base == '9') and (len_ > 9) and (v9 is None)
    
    def mssql_col(self): 
        return mssql.BIGINT()
    

class DecimalConverter(TypeManager): 
    typeid = 'decimal'
    pytype = Decimal
    _pandas_dtype = 'Float64'

    def validate(self): 
        base, _l, v9 = self.format_groups
        return re.match(r'S?9', base) and (v9 is not None)
    
    def mssql_col(self): 
        _b, len_, v9 = self.format_groups
        dec1 = v9 or 0
        prec = len_ + dec1
        scale = dec1 
        return mssql.DECIMAL(prec, scale)

    def pd_fromrow(self, row_name=None, with_name=False): 
        row_name = row_name or 'value'
        name, slice_ = ɑ('Name1', 'slice')(self.specs)
        _b, _l, v9 = self.format_groups
        λ_slice = lambda df: (df[row_name].str[slice_]
            .str.strip().replace('', pd.NA)
            .astype(self.pandas_dtype)
            .div(10**v9).round(v9 or 0))    
        return (name, λ_slice) if with_name else λ_slice
        
    def pd_fromstr(self, with_name): 
        name = self.specs.Name1
        _b, _l, v9 = self.format_groups
        λ_mutate = (lambda df: df[name].str.strip()
            .replace('', pd.NA).astype(self.pandas_dtype).div(10**v9).round(v9))
        return (name, λ_mutate) if with_name else λ_mutate


