from dataclasses import astuple, dataclass, field
from operator import attrgetter as ɑ
import re
import typing as typ

from pydantic import BaseModel, ConfigDict, field_validator


@dataclass
class Cobol: 
    base : str
    length : int
    decimals : int | None 
    raw : str = field(default='', init=False, repr=False)

    _PATTERN = re.compile(r"^(P<base>S?9|X)(?:\((?P<len>\d{1,4})\))?(?:V9(?P<v9>\d))")

    @classmethod
    def parse(cls, raw:str) -> typ.Self: 
        raw = raw.strip()
        if not (m := cls._PATTERN.match(raw)): 
            raise Exception
        bb, ll, v9 = m.groups()
        instance = cls(bb.upper(), int(ll or 1), int(v9) if v9 else None)
        instance.raw = raw
        return instance
    
    def kind(self): 
        bb, _ll, v9 = astuple(self)
        if bb == 'X': 
            return 'str'
        if re.match(r'S?9', bb) and v9 is None: 
            return 'int'
        if re.match(r'S?9', bb) and v9 is not None: 
            return 'decimal'
        raise Exception


class FieldSpec(BaseModel): 
    model_config = ConfigDict(frozen=True)
    
    name : str
    start : int
    length : int
    cobol : Cobol 

    @field_validator('start', mode='before')
    def zero_index(self, v:int) -> int: 
        return v-1
    
    @field_validator('cobol', mode='before')
    def parse_cobol(self, v:str|Cobol) -> Cobol: 
        return Cobol.parse(v) if isinstance(v, str) else v
    
    @property
    def slice(self) -> slice: 
        ss, ll = ɑ('start', 'length')(self)
        return slice(ss, ss+ll)
    
    @property
    def kind(self) -> str: 
        match (self.cobol.kind, self.cobol.length, self.name.upper()):
            case ('str', 6,  nn) if 'DAT' in nn: return 'date'
            case ('str', 8,  nn) if 'TIM' in nn: return 'fractime'
            case ('str', 19, nn) if 'TIM' in nn: return 'datetime'
            case ('int', nn, _ ) if nn >= 9 :    return 'bigint'
            case (kind , _ , _ )            :    return kind

