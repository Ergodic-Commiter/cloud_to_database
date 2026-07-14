from abc import ABC, abstractmethod
import typing as typ

import pandas as pd
from .base import FieldSpec


Mutate = typ.Callable[[pd.Series], pd.Series]

class PandasIntake(ABC):
    registry: typ.ClassVar[dict[str, type[typ.Self]]] = {}

    def __init_subclass__(cls, key:str=None, **kwargs): 
        super().__init_subclass__(**kwargs)
        if key is not None: 
            PandasIntake.registry[key] = cls

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
            valid = valid_(a_slice)
            parsed = coerce_(a_slice).where(valid)
            return finish_(parsed)
        return mutate

    def slice_df(self) -> Mutate:
        return lambda srs: srs.str[self.spec.slice].str.strip()

    def is_valid(self) -> Mutate: 
        return lambda srs: pd.Series(True, index=srs.index)

    @abstractmethod
    def coerce(self) -> Mutate: ...

    def finalize(self) -> Mutate: 
        return lambda srs: srs


class StrIntake(PandasIntake, key='str'): 
    def coerce(self) -> Mutate:
        return lambda srs: srs.replace('', pd.NA)
    
class IntIntake(PandasIntake, key='int'):
    def coerce(self) -> Mutate:
        def λ_coerce(srs:pd.Series) -> pd.Series: 
            pre = srs.replace("", pd.NA, regex=False)
            return pd.to_numeric(pre, errors="coerce")
        return λ_coerce

class BigintIntake(IntIntake, key='bigint'): 
    pass 

class DecimalIntake(IntIntake, key='decimal'): 
    def is_valid(self) -> Mutate:
        return lambda srs: srs.str.fullmatch(r'\s*[\-\+]?\d*', na=False)
    def finalize(self) -> Mutate: 
        v9 = self.spec.cobol.decimals
        return lambda srs: srs.astype('Float64').div(10**v9).round(v9)

class DatetimeIntake(StrIntake, key='datetime'): 
    pass
    # def coerce(self) -> Mutate: 
    #     dt_args = dict(errors="coerce", unit="D", origin="julian")
    #     def λ_coerce(srs: pd.Series) -> pd.Series: 
    #         srs_1 = pd.to_numeric(srs, errors='coerce')
    #         return pd.to_datetime(pd.to_numeric(srs_1), **dt_args)
    #     return λ_coerce
    # def is_valid(self) -> Mutate: 
    #     return lambda srs: srs.str.fullmatch(r'\d{19}')

class DateIntake(StrIntake, key='date'): 
    pass 
    # def coerce(self) -> Mutate: 
    #     def λ_coerce(srs: pd.Series) -> pd.Series:
    #         return pd.to_datetime(srs, format="%y%m%d", errors='coerce').dt.date
    #     return λ_coerce
    # def is_valid(self) -> Mutate: 
    #     return lambda srs: srs.str.fullmatch(r'\d{6}')

class FractimeIntake(StrIntake, key='fractime'):
    pass

