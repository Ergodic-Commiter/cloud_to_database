from operator import attrgetter as ɑ

import sqlalchemy as alq
from sqlalchemy.dialects import mssql

from .base import FieldSpec
# pylint: disable=too-many-return-statements


class MssqlUpload:
    def __init__(self, spec:FieldSpec): 
        self.spec = spec 

    def alq_type(self) -> alq.types.TypeEngine:
        ll, v9 = ɑ('length', 'decimals')(self.spec.cobol)
        v9 = v9 or 0
        match self.spec.kind:
            case 'str'      : return mssql.VARCHAR(ll)
            case 'int'      : return mssql.INTEGER()
            case 'bigint'   : return mssql.BIGINT()
            case 'decimal'  : return mssql.DECIMAL(ll + v9, v9)
            case 'datetime' : return mssql.DATETIME2()
            case 'date'     : return mssql.DATE()
            case 'fractime' : return mssql.TIME()

    def alq_column(self) -> alq.Column:
        return alq.Column(self.spec.name, self.alq_type())

