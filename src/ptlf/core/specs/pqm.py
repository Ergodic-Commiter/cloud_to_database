from functools import cached_property
import re
from toolz import curried as cz

from ptlf.tools import thread
from .base import FieldSpec



class PqmTemplate:
    def __init__(self, spec:FieldSpec): 
        self.spec = spec 

    TYPE_2_PQM = dict(
        str = ('text', 'TextLit'), 
        int = ('number', 'IntLit'), 
        decimal = ('number', 'NumberLit'), 
        date = ('date', 'DateLit'))

    @cached_property
    def name(self) -> str:
        return getattr(self.spec, 'new_name')

    @cached_property
    def excel(self) -> str:
        camel = thread(self.name, 
            (re.split, r"[-_]", ...), 
            cz.map(str.title), 
            ''.join)
        return camel

    @cached_property
    def pq_type(self) -> str:
        return self.TYPE_2_PQM[self.spec.kind][0]

    @cached_property
    def pq_lit(self) -> str:
        return self.TYPE_2_PQM[self.spec.kind][1]

    def xl_2_pq(self) -> str: 
        return f'{{ "{self.name}", type {self.pq_type} }}'

    def pq_2_sql(self) -> str: 
        return f'{self.pq_lit}(Record.Field(row, "{self.name}"))'