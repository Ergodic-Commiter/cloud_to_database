from collections import defaultdict
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime as dt
from operator import attrgetter as ɑ
import re
from typing import (Any, ClassVar, DefaultDict, Dict, 
    List, NamedTuple, Optional, Tuple, Type)
from warnings import warn

import pandas as pd
import sqlalchemy as alq
from sqlalchemy.dialects import mssql
from toolz import functoolz as fz

from src import errors as ee
from src.db import utils
# pylint:disable=abstract-method
# pylint:disable=invalid-name
# pylint:disable=no-member
# pylint:disable=no-self-argument
# pylint:disable=protected-access

@dataclass
class FieldSpecs: 
    Name1 : str
    From : int
    Length : int
    Format : str
    
    @property
    def slice(self): 
        ff, ll = ɑ('From', 'Length')(self)
        return slice(ff, ff+ll)



class Typer: 
    """A factory and mixin class of converters for different types. 
    Each converter reads a Pandas (specs) tuple representing a column of a wider table. 
    """
    # Atributos para el "usuario"
    pytype: ClassVar[Optional[Type[Any]]] = None
    _pandas_dtype: ClassVar[Optional[object]] = None
    
    # Registro de Converter's como subclases. 
    registry = {}
    typeid: ClassVar[Optional[str]] = None
    def __init_subclass__(cls):
        """Registers subclass based on typeid."""
        super().__init_subclass__()
        if not hasattr(cls, 'typeid') or cls.typeid is None:
            raise TypeError(f"{cls.__name__} must define 'typeid'.")
        Typer.registry[cls.typeid] = cls

    # Inicialización (de subclases). 
    def __init__(self, raw_row:NamedTuple):
        """All subclasses start with RAW-ROW (from dataframe)"""
        self._specs = raw_row

    @classmethod
    def from_specs(cls, raw_row:tuple, stage='raw'):
        """Validates and chooses."""
        if len(valids := cls.get_valid_converters(raw_row, stage)) != 1: 
            raise ee.UniqueConverterError(raw_row.Name1)
        converter = cls.registry[valids[0]]
        return converter(raw_row)

    @classmethod
    def get_valid_converters(cls, raw_row:tuple, stage=None):
        stage = stage or 'raw'
        χ_valid = lambda typeid: cls.registry[typeid](raw_row).validate(stage)
        return list(filter(χ_valid, cls.registry))    
    
    def validate(self, stage):
        raise NotImplementedError

    # Conjunción de muchos Converter's en diccionario
    @classmethod
    def dataframe_to_dict(cls, types_df: pd.DataFrame) -> Dict[str, 'Typer']: 
        λ_prepare = dict(
            Name0 = lambda df: df['Field_Name'].str.replace(' ', ''), 
            Name1 = lambda df: utils.index_duplicates(df['Name0']), 
            Format = lambda df: df['Format'].str.replace(' ', ''))
        λ_dicter = fz.juxt(ɑ('Name1'), cls.from_specs)
        iter_df = types_df.assign(**λ_prepare)
        return dict(map(λ_dicter, iter_df.itertuples()))    
    
    # Propiedades ayudadoras. 
    @utils.classproperty
    def pandas_dtype(cls):  
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
        """Typer subclasses use format_groups to choose their type."""
        # COBOL: (S?9|X)\((\d+)\)(V9(9|\(\d\)))?
        # S9(n), 9(n), X(n), S9(n)V9(k), 9(n)V99...
        fmt_str = self.specs.Format
        reg_fmt = r"^(?P<base>S?9|X)(?:\((?P<len>\d{1,4})\))?(?:V9(?P<v9>\d))?"      
        if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
            raise ee.COBOL_FormatError(fmt_str)
        base, len_, v9 = reg_match.groups()
        return base, int(len_ or 1), utils.noner(int)(v9)

    # Usos y procesamiento de cada convertidor
    # (NotImplemented) se implementan a nivel subclase Converter. 
    # VALIDATE, MSSQL_COL, PD_SERIES
    def alq_mssql(self):  
        """Genera columna para SQLALCHEMY al crear la table en SQL"""
        name = self.specs.Name1
        sql_col = self.mssql_col()
        return alq.Column(name, sql_col)
    
    def mssql_col(self):
        raise NotImplementedError

    def pd_fromrow(self, row_name='value', *, 
        report:DefaultDict[str, List[Tuple]]=None):
        """Procesa con Pandas la fila completa del Fixed Width"""
        def mutate(df): 
            a_slice = self.slice_df(df, row_name)
            novalid = ~self._is_valid(a_slice)
            if ((nosum := novalid.sum()) > 0) and (report is not None): 
                report[self.typeid].append((self.specs.Name1, int(nosum)))
            parsed = self._coerce(a_slice).where(~novalid)
            return self._finalize(parsed)
        return mutate

    def slice_df(self, df, row_name='value'): 
        return df[row_name].str[self.specs.slice]

    def _coerce(self, str_srs):
        raise NotImplementedError
    
    def _valid_srs(self, str_srs): 
        return pd.Series(True, index=str_srs.index)
    
    def _finalize(self, prs_srs): 
        return prs_srs

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.typeid}: {self.specs})>"


class StrConverter(Typer):
    typeid = 'str'
    pytype = str
    _pandas_dtype = 'string'

    def validate(self, stage):
        b_, l_, _v9 = self.format_groups
        if stage == 'raw': 
            return b_ == 'X'
        if b_ != 'X': 
            return False
        name = self.specs.Name1
        is_dt   = ('TIM' in name) and (l_ == 19)
        is_date = ('DAT' in name) and (l_ == 6)
        is_time = ('TIM' in name) and (l_ == 8)
        return not is_dt and not is_date and not is_time
    
    def mssql_col(self):
        _b, len_, _v9 = self.format_groups
        return mssql.VARCHAR(len_)

    def _coerce(self, str_srs):
        return str_srs.str.strip()

    def _is_valid(self, str_srs):
        return pd.Series(True, index=str_srs.index)

    def _finalize(self, prs_srs):
        return prs_srs.astype(self.pandas_dtype)
 
    
class IntConverter(Typer): 
    typeid = 'int'
    pytype = int
    _pandas_dtype = 'Int64'
    
    def validate(self, stage): 
        base, len_, v9 = self.format_groups
        return (base == '9') and (len_ <= 9) and (v9 is None)
    
    def mssql_col(self): 
        return mssql.INTEGER()
  
    def _coerce(self, str_srs):
        pre = str_srs.str.strip().replace("", pd.NA, regex=False)
        return pd.to_numeric(pre, errors="coerce")

    def _is_valid(self, str_srs):
        return str_srs.str.fullmatch(r"\s*\d+\s*", na=False)

    def _finalize(self, prs_srs):
        return prs_srs.astype(self.pandas_dtype)
 
    
class BigIntConverter(IntConverter): 
    typeid = 'bigint'
    def validate(self, stage): 
        if stage == 'raw': 
            base, len_, v9 = self.format_groups
            return (base == '9') and (len_ > 9) and (v9 is None)
        raise TypeError

    def mssql_col(self): 
        return mssql.BIGINT()
    

class DecimalConverter(Typer): 
    typeid = 'decimal'
    pytype = Decimal
    _pandas_dtype = 'Float64'
    
    warn_v9 = defaultdict(int)

    @property
    def format_groups(self): 
        """Typer subclasses use format_groups to choose their type."""
        # COBOL: (S?9|X)\((\d+)\)(V9(9|\(\d\)))?
        # S9(n), 9(n), X(n), S9(n)V9(k), 9(n)V99...
        fmt_str = self.specs.Format
        reg_fmt = r"^(?P<base>S?9|X)(?:\((?P<len>\d{1,4})\))?(?:V9(?P<v9>\d))?"      
        if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
            raise ee.FormatCOBOL_Error(fmt_str.strip())
        base, len_, v9 = reg_match.groups()
        return base, int(len_ or 1), self.about_v9(v9)
  
    def about_v9(self, v9):
        cls = self.__class__         
        this_fmt = self._specs.Format 
        if v9 not in (None, '2'):
            v9 = '2'
            if this_fmt not in cls.warn_v9: 
                warn(f"Unusual V9 spec in ({this_fmt}) in {cls.__name__}; defaulting to 2")
                cls.warn_v9[this_fmt] += 1
        return utils.noner(int)(v9)
    
    def validate(self, stage):
        base, _l, v9 = self.format_groups
        return re.match(r'S?9', base) and (v9 is not None)

    def mssql_col(self): 
        _b, len_, v9 = self.format_groups
        dec1 = v9 or 0
        prec = len_ + dec1
        scale = dec1 
        return mssql.DECIMAL(prec, scale)

    def _coerce(self, str_srs): 
        return str_srs.str.strip().replace('', pd.NA)

    def _is_valid(self, str_srs): 
        return str_srs.str.fullmatch(r'\s*\d+\s*', na=False)

    def _finalize(self, prs_srs): 
        _b, _l, v9 = self.format_groups
        return prs_srs.astype(self.pandas_dtype).div(10**v9).round(v9)


class DatetimeConverter(Typer): 
    typeid = 'datetime'
    pytype = dt

    def validate(self, stage): 
        if stage == 'raw': 
            return False
        if stage == 'ops': 
            name = self.specs.Name1
            b_, l_, _ = self.format_groups
            return (b_ == 'X') and (l_ == 19) and ('TIM' in name)
        raise ValueError(f"stage validator {stage} must be [raw, ops]")

    def mssql_col(self): 
        return mssql.DATETIME2()

    def _coerce(self, str_srs): 
        return str_srs

    def _is_valid(self, str_srs): 
        return str_srs.str.fullmatch(r'\d{19}')

    def _finalize(self, prs_srs): 
        return pd.to_datetime(prs_srs, unit='D', origin='julian')



class DateConverter(Typer): 
    typeid = 'date'
    pytype = dt.date

    def validate(self, stage): 
        if stage == 'raw': 
            return False 
        if stage == 'ops': 
            name = self.specs.Name1 
            b_, l_, _ = self.format_groups
            return (b_ == 'X') and (l_ == 6) and ('DAT' in name)
        raise ValueError(f"stage validator {stage} must be [raw, ops]")

    def mssql_col(self): 
        return mssql.DATE

    def _coerce(self, str_srs): 
        return pd.to_datetime(str_srs, "%y%m%d").dt.date

    def _is_valid(self, str_srs): 
        return str_srs.str.fullmatch(r'\d{6}')

    def _finalize(self, prs_srs): 
        return pd.to_datetime(prs_srs, "%y%m%d").dt.date



class FracTimeConverter(Typer): 
    typeid = 'fractime'
    pytype = dt 

    def validate(self, stage): 
        if stage == 'raw': 
            return False 
        if stage == 'ops': 
            name = self.specs.Name1 
            b_, l_, _ = self.format_groups
            return (b_ == 'X') and (l_ == 8) and ('TIM' in name)
        raise ValueError(f"stage validator {stage} must be [raw, ops]")

    def mssql_col(self): 
        return mssql.TIMESTAMP

    def _coerce(self, str_srs): 
        pass 

    def _is_valid(self, str_srs): 
        pass

    def _finalize(self, prs_srs): 
        pass 

    def pd_series(self, str_srs, errors=False): 
        if not errors:
            return pd.to_datetime(str_srs, '%H%M%S%T')
        raise ee.PandasConversionError(self.cfg.Name1, self.typeid)
