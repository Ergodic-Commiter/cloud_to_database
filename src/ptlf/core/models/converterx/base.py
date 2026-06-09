from collections import defaultdict, namedtuple
from decimal import Decimal
from datetime import datetime as dt
from operator import attrgetter as ɑ
import re
from typing import Any, ClassVar, Dict, Literal, Optional, Type
from warnings import warn

import pandas as pd
from pydantic import BaseModel
from toolz import functoolz as fz

from ptlf import tools
from ptlf.core import errors as ee
# pylint: disable=invalid-name
# pylint: disable=no-self-argument
# pylint: disable=too-few-public-methods


class FieldSpecs(BaseModel): 
    Name : str
    From : int
    Length : int
    Format : str    
    @property
    def slice(self): 
        ff, ll = ɑ('From', 'Length')(self)
        return slice(ff, ff+ll)



class Converter: 
    registry: Dict[str, type('Converter')] = {}
    typeid: ClassVar[Optional[str]] = None
    pytype: ClassVar[Optional[Type[Any]]] = None

    def __init_subclass__(cls):
        """Registers subclass based on typeid."""
        super().__init_subclass__()
        if (type_id := getattr(cls, 'typeid', None)) is None: 
            return 
        Converter.registry[type_id] = cls
        
    def __init__(self, raw_row:FieldSpecs):
        """Subclasses usually start with RAW-ROW (from dataframe)"""
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
    
    def validate(self, stage:Literal['raw','ops']):
        # stage 
        raise NotImplementedError

    @classmethod
    def dataframe_to_dict(cls, types_df: pd.DataFrame) -> Dict[str, 'Converter']: 
        λ_prepare = dict(
            Name0 = lambda df: df['Field_Name'].str.replace(' ', ''), 
            Name1 = lambda df: tools.index_duplicates(df['Name0']), 
            Format = lambda df: df['Format'].str.replace(' ', ''))
        λ_dicter = fz.juxt(ɑ('Name1'), cls.from_specs)
        iter_df = types_df.assign(**λ_prepare)
        return dict(map(λ_dicter, iter_df.itertuples()))    
    
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
        """Converter subclasses use format_groups to choose their type."""
        # COBOL: (S?9|X)\((\d+)\)(V9(9|\(\d\)))?
        # S9(n), 9(n), X(n), S9(n)V9(k), 9(n)V99...
        fmt_str = self.specs.Format
        reg_fmt = r"^(?P<base>S?9|X)(?:\((?P<len>\d{1,4})\))?(?:V9(?P<v9>\d))?"      
        if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
            raise ee.COBOL_FormatError(fmt_str)
        base, len_, v9 = reg_match.groups()
        return base, int(len_ or 1), tools.noner(int)(v9)
  
    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.typeid}: {self.specs})>"


class StrConverter(Converter, typeid='str'):
    pytype = str
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
    
class IntConverter(Converter, typeid='int'): 
    pytype = int
    def validate(self, stage): 
        base, len_, v9 = self.format_groups
        return (base == '9') and (len_ <= 9) and (v9 is None)
    
class BigIntConverter(IntConverter, typeid='bigint'): 
    def validate(self, stage): 
        if stage == 'raw': 
            base, len_, v9 = self.format_groups
            return (base == '9') and (len_ > 9) and (v9 is None)
        raise TypeError

class DecimalConverter(Converter, typeid='decimal'): 
    pytype = Decimal
    warn_v9 = defaultdict(int)
    @property
    def format_groups(self): 
        """Converter subclasses use format_groups to choose their type."""
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
        return tools.noner(int)(v9)
    def validate(self, stage):
        base, _l, v9 = self.format_groups
        return re.match(r'S?9', base) and (v9 is not None)

class DatetimeConverter(Converter, typeid='datetime'): 
    pytype = dt
    def validate(self, stage): 
        if stage == 'raw': 
            return False
        if stage == 'ops': 
            name = self.specs.Name1
            b_, l_, _ = self.format_groups
            return (b_ == 'X') and (l_ == 19) and ('TIM' in name)
        raise ValueError(f"stage validator {stage} must be [raw, ops]")

class DateConverter(Converter, typeid='date'): 
    pytype = dt.date
    def validate(self, stage): 
        if stage == 'raw': 
            return False 
        if stage == 'ops': 
            name = self.specs.Name1 
            b_, l_, _ = self.format_groups
            return (b_ == 'X') and (l_ == 6) and ('DAT' in name)
        raise ValueError(f"stage validator {stage} must be [raw, ops]")

class FracTimeConverter(Converter, typeid='fractime'): 
    pytype = dt 
    def validate(self, stage): 
        if stage == 'raw': 
            return False 
        if stage == 'ops': 
            name = self.specs.Name1 
            b_, l_, _ = self.format_groups
            return (b_ == 'X') and (l_ == 8) and ('TIM' in name)
        raise ValueError(f"stage validator {stage} must be [raw, ops]")



def resolve_cobol(fields:FieldSpecs, stage:str=None): 
    stage = stage or 'raw'
    if stage == 'raw': 
        return _raw_resolve(fields.Format)
    if stage == 'ops': 
        return _ops_resolve(fields)
    raise ValueError("Can only resolve_type in stages [raw, ops]")

     
def _raw_resolve(formatter): 
    b_, l_, v_ = ɑ('base', 'len', 'v9')(_cobolize(formatter))
    if (b_ == 'X'): 
        return 'str'
    if (v_ is not None): 
        return 'decimal'
    if (l_ <= 9):  
        return 'int'
    if (l_ > 9): 
        return 'bigint'
    raise ValueError(f"Formatter {formatter} couldnt be resolved.")
    
CobolGroups = namedtuple('CobolGroups', 'base,len,v9')

def _cobolize(formatter:str): 
    reg_fmt = r"^(?P<base>S?9|X)(?:\((?P<len>\d{1,4})\))?(?:V9(?P<v9>\d))?"      
    if not (reg_match := re.match(reg_fmt, formatter.strip().upper())):
        raise ee.COBOL_FormatError(formatter)
    base, len_, v9 = reg_match.groups()
    return CobolGroups(base, len_ or 1, tools.noner(int)(v9))
    
    
def _ops_resolve(specs:FieldSpecs): 
    _format, name = ɑ('Format', 'Name')(specs)
    b_, l_, _ = ɑ('base', 'len', 'v9')(_cobolize(_format))
    if b_ != 'X':
        return _raw_resolve(_format)
    if ('TIM' in name) and (l_ == 19): 
        return 'datetime'
    if ('DAT' in name) and (l_ == 6): 
        return 'date'
    if ('TIM' in name) and (l_ == 8): 
        return 'fractime'
    return 'str'


class ConverterFactory:
    @staticmethod
    def from_specs(row, stage:str="raw") -> Converter:
        spec = FieldSpecs(
            Name=row.Name,
            From=int(row.From) - 1,
            Length=int(row.Length),
            Format=row.Format)

        typeid = resolve_cobol(spec, stage)  # <- central logic
        conv_cls = Converter.registry[typeid]
        return conv_cls(spec) 


