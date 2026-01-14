from typing import ClassVar, DefaultDict, List, Optional, Tuple

import pandas as pd

from ptlf import tools
from .base import Merger
# pylint: disable=no-self-argument
# pylint: disable=too-few-public-methods
# pylint: disable=no-member


class PandasMerger(Merger): 
    registry = {}
    _pandas_dtype: ClassVar[Optional[object]] = None

    @tools.classproperty
    def pandas_dtype(cls):  
        return cls._pandas_dtype or cls.pytype

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
    
    def _is_valid(self, str_srs): 
        return pd.Series(True, index=str_srs.index)
    
    def _finalize(self, prs_srs): 
        return prs_srs


class StrPandas(PandasMerger):
    typeid = 'str'
    _pandas_dtype = 'string'
    def _coerce(self, str_srs):
        return str_srs.str.strip().replace('', pd.NA)
    
class IntPandas(PandasMerger): 
    typeid = 'int'
    _pandas_dtype = 'Int64'
    def _coerce(self, str_srs):
        pre = str_srs.str.strip().replace("", pd.NA, regex=False)
        return pd.to_numeric(pre, errors="coerce")
    def _is_valid(self, str_srs):
        return str_srs.str.fullmatch(r"\s*\d*", na=False)
    def _finalize(self, prs_srs):
        return prs_srs.astype(self.pandas_dtype)
 
class DecimalPandas(PandasMerger): 
    typeid = 'decimal'
    _pandas_dtype = 'Float64'
    def _coerce(self, str_srs): 
        pre = str_srs.str.strip().replace('', pd.NA)
        return pd.to_numeric(pre, errors='coerce')
    def _is_valid(self, str_srs): 
        return str_srs.str.fullmatch(r'\s*[\-\+]?\d*', na=False)
    def _finalize(self, prs_srs): 
        _b, _l, v9 = self.format_groups
        return prs_srs.astype(self.pandas_dtype).div(10**v9).round(v9)

class DatetimePandas(PandasMerger): 
    typeid = 'datetime'
    def _coerce(self, str_srs: pd.Series) -> pd.Series:
        return pd.to_datetime(str_srs, errors="coerce", unit="D", origin="julian")
    def _is_valid(self, str_srs): 
        return str_srs.str.fullmatch(r'\d{19}')
    def _finalize(self, prs_srs): 
        return prs_srs

class DatePandas(PandasMerger): 
    typeid = 'date'
    def _coerce(self, str_srs): 
        return pd.to_datetime(str_srs, "%y%m%d").dt.date
    def _is_valid(self, str_srs): 
        return str_srs.str.fullmatch(r'\d{6}')
    def _finalize(self, prs_srs): 
        return prs_srs 

class FracTimePandas(PandasMerger): 
    typeid = 'fractime'
    def _coerce(self, str_srs): 
        raise NotImplementedError
    def _is_valid(self, str_srs): 
        pass
    def _finalize(self, prs_srs): 
        pass 



