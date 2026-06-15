from abc import ABC, abstractmethod
import typing as typ

import pandas as pd
from .base import FieldSpec


Mutate = typ.Callable[[pd.Series], pd.Series]

class PandasIntake(ABC):
    # Definition
    registry: typ.ClassVar[dict[str, type[typ.Self]]] = {}

    def __init_subclass__(cls, kind:str, **kw): 
        super().__init_subclass__(**kw)
        PandasIntake.registry[kind] = cls

    # Instantiation
    @classmethod
    def from_spec(cls, spec:FieldSpec) -> typ.Self: 
        intake = PandasIntake.registry[spec.kind]
        return intake(spec)

    def __init__(self, spec:FieldSpec): 
        self.spec = spec 

    # Operation
    def make_lambda(self) -> Mutate:
        slice_  = self.slice_df()
        valid_  = self.is_valid()
        coerce_ = self.coerce()
        finish_ = self.finalize()
        def mutate(srs:pd.Series) -> pd.Series: 
            a_slice = slice_(srs)
            novalid = ~valid_(a_slice)
            parsed = coerce_(a_slice).where(~novalid)
            return finish_(parsed)
        return mutate

    def slice_df(self) -> Mutate:
        return lambda srs: srs.str[self.spec.slice]

    def is_valid(self) -> Mutate: 
        return lambda srs: pd.Series(True, index=srs.index)

    @abstractmethod
    def coerce(self) -> Mutate: ...

    def finalize(self) -> Mutate: 
        return lambda srs: srs


class StrIntake(PandasIntake, kind='str'): 
    def coerce(self) -> Mutate:
        return lambda srs: srs.str.strip().replace('', pd.NA)
    

class IntIntake(PandasIntake, kind='int'):
    def coerce(self) -> Mutate:
        def λ_coerce(srs:pd.Series) -> pd.Series: 
            pre = srs.str.strip().replace("", pd.NA, regex=False)
            return pd.to_numeric(pre, errors="coerce")
        return λ_coerce


class DecimalIntake(IntIntake, kind='decimal'): 
    def is_valid(self) -> Mutate:
        return lambda srs: srs.str.fullmatch(r'\s*[\-\+]?\d*', na=False)

    def finalize(self) -> Mutate: 
        v9 = self.spec.cobol.v9
        return lambda srs: srs.astype('Float64').div(10**v9).round(v9)


class DatetimeIntake(PandasIntake, kind='datetime'): 
    def coerce(self) -> Mutate: 
        dt_args = dict(errors="coerce", unit="D", origin="julian")
        return lambda srs: pd.to_datetime(srs, **dt_args)

    def is_valid(self) -> Mutate: 
        return lambda srs: srs.str.fullmatch(r'\d{19}')


class DateIntake(PandasIntake, kind='date'):     
    def coerce(self) -> Mutate: 
        return lambda srs: pd.to_datetime(srs, "%y%m%d").dt.date

    def is_valid(self) -> Mutate: 
        return lambda srs: srs.str.fullmatch(r'\d{6}')


class FractimeIntake(PandasIntake, kind='fractime'):
    def coerce(self) -> Mutate: 
        pass 

    def is_valid(self) -> Mutate: 
        pass


