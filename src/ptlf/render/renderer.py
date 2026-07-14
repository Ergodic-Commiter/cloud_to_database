from itertools import starmap
from pathlib import Path
from textwrap import dedent
import typing as typ

import jinja2 as j2

from ptlf.core.specs import PqmTemplate

TEMPLATES = Path(__file__).parent/'templates'


class Renderer: 
    template: str 
    
    _registry: typ.ClassVar[dict[str, 'Renderer']] = {}
    def __init_subclass__(cls, key:str, **kwargs): 
        super().__init_subclass__(**kwargs)
        Renderer._registry[key] = cls
        cls.key = key

    @classmethod
    def create(cls, key:str, *args): 
        return cls._registry[key](*args)
    
    def setup_env(self): 
        env = j2.Environment(loader=j2.FileSystemLoader(TEMPLATES))
        env.filters['mapper'] = lambda f_name: getattr(self, f_name)()
        return env

    def render(self): 
        return self.setup_env().get_template(self.template).render()
    
    def write(self, path:Path): 
        path.write_text(self.render(), encoding='utf-8')



class RendererExacto(Renderer, key='exacto'):
    template = 'PTLF_Exacto.j2.pqm'

    def __init__(self, view:str, keys:list[PqmTemplate]): 
        self.view = view
        self.keys = keys 

    def query(self): 
        k_temp = ", ".join(kk.name for kk in self.keys)
        join_on = dedent("""
        \t\t  AND """.join(f"t.{kk.name} = k.{kk.name}" for kk in self.keys))
        q_template = dedent(f"""\
        ;
        \t\tSELECT t.*
        \t\tFROM {self.view} AS t
        \t\tJOIN ("& ValuesClause &"
        \t\t  ) AS k({k_temp})
        \t\t  ON  {join_on}""")
        return q_template

    def nulls(self):
        return ', '.join('NULL' for _ in self.keys)

    def records(self):
        return ' & "," &\n\t\t'.join(kk.pq_2_sql() for kk in self.keys)

    def transforms(self): 
        return ',\n\t\t'.join(kk.xl_2_pq() for kk in self.keys)


class RendererExplora(Renderer, key='explora'):
    template = 'PTLF_Explora.j2.pqm'

    def __init__(self, keys): 
        self.keys = keys

    def params(self): 
        λ_key = lambda k: f'{k.excel} = Opt{k.pq_type.title()}(ReadName("par_{k.name}"))'
        return ',\n\t\t'.join(λ_key(kk) for kk in self.keys)

    def filters(self): 
        λ_enumkey = lambda i,k: dedent(f"""\
        \tFilter{i+1} = if Params[{k.excel}] <> null 
        \t\t\tthen Table.SelectRows(Filter{i}, each [{k.excel}] = Params[{k.excel}]) 
        \t\t\telse Filter{i},""")
        return '\n\t'.join(starmap(λ_enumkey, enumerate(self.keys)))