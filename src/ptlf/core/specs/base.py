from dataclasses import astuple, dataclass, field
from operator import attrgetter as ɑ
import re
from typing import Self

import pandas as pd
import pydantic as pyd
# pylint: disable=unsubscriptable-object


@dataclass
class Cobol: 
    raw : str
    base : str = field(init=False, repr=False)
    length : int = field(init=False, repr=False)
    decimals : int|None = field(init=False, repr=False)

    _PATTERN = re.compile(r"^(?P<base>S?9|X)(?:\((?P<len>\d{1,4})\))?(?:V9(?P<v9>\d))?")

    def __post_init__(self):
        raw = self.raw = self.raw.strip() 
        if not (m := self._PATTERN.match(raw)): 
            raise ValueError(f"Raw string {raw} doesnt match Cobol regex")
        bb, ll, v9 = m.groups()
        self.base = bb.upper()
        self.length = int(ll or 1)
        self.decimals = int(v9) if v9 else None
    
    @property
    def kind(self) -> str: 
        _, bb, _ll, v9 = astuple(self)
        if bb == 'X': 
            return 'str'
        if re.match(r'S?9', bb) and v9 is None: 
            return 'int'
        if re.match(r'S?9', bb) and v9 is not None: 
            return 'decimal'
        raise ValueError(f"Cannot sort 'kind' for {self}")
    

class FieldSpec(pyd.BaseModel): 
    model_config = pyd.ConfigDict(frozen=True, extra='allow', 
        from_attributes=True, populate_by_name=True)
    
    name : str = pyd.Field(alias="Name1")
    start : int = pyd.Field(alias="From")
    length : int = pyd.Field(alias="Length")
    cobol : Cobol = pyd.Field(alias="Format")

    @classmethod
    def dataframe_dict(cls, df:pd.DataFrame) -> dict[str, Self]: 
        name_at = cls.model_fields['name'].alias     
        the_specs = {row[name_at]: cls.model_validate(row)
            for row in df.to_dict('records')}
        return the_specs

    @pyd.field_validator('start', mode='before')
    @classmethod
    def zero_index(cls, v:int) -> int: 
        return v-1
    
    @pyd.field_validator('cobol', mode='before')
    @classmethod
    def parse_cobol(cls, v:Cobol|str) -> Cobol: 
        return Cobol(v) if isinstance(v, str) else v
    
    @property
    def slice(self) -> slice: 
        ss, ll = ɑ('start', 'length')(self)
        return slice(ss, ss+ll)
    
    @property
    def kind(self) -> str: 
        match (self.cobol.kind, self.cobol.length, self.name.upper()):
            case ('str', 6,  nn) if 'DAT' in nn: return 'date'
            case ('str', 19, nn) if 'TIM' in nn: return 'datetime'
            case ('str', 8,  nn) if 'TIM' in nn: return 'fractime'
            case ('int', nn, _) if nn >= 9: return 'bigint'
            case (kk, _, _): return kk
            case _: raise ValueError(f"Unmatched kind for {self.name}")

