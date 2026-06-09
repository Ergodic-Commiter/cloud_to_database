import sqlalchemy as alq
from sqlalchemy.dialects import mssql

# from .base import Merger
# pylint: disable=no-member


class MSSQLMixin: 
    def alq_mssql(self):  
        """Genera columna para SQLALCHEMY al crear la table en SQL"""
        name = self.specs.Name1
        sql_col = self.mssql_col()
        return alq.Column(name, sql_col)
    
    def mssql_col(self):
        raise NotImplementedError


class StrMSSQL(MSSQLMerger):
    typeid = 'str'
    def mssql_col(self):
        _b, len_, _v9 = self.format_groups
        return mssql.VARCHAR(len_)

class IntMSSQL(MSSQLMerger): 
    typeid = 'int'
    def mssql_col(self): 
        return mssql.INTEGER()
  
class BigIntMSSQL(IntMSSQL): 
    typeid = 'bigint'
    def mssql_col(self): 
        return mssql.BIGINT()
    
class DecimalMSSQL(MSSQLMerger): 
    typeid = 'decimal'
    def mssql_col(self): 
        _b, len_, v9 = self.format_groups
        dec1 = v9 or 0
        prec = len_ + dec1
        scale = dec1 
        return mssql.DECIMAL(prec, scale)

class DatetimeMSSQL(MSSQLMerger): 
    typeid = 'datetime'
    def mssql_col(self): 
        return mssql.DATETIME2()

class DateMSSQL(MSSQLMerger): 
    typeid = 'date'
    def mssql_col(self): 
        return mssql.DATE


class FracTimeMSSQL(MSSQLMerger): 
    typeid = 'fractime'
    def mssql_col(self): 
        return mssql.TIMESTAMP


