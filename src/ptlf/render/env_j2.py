from itertools import starmap
from pathlib import Path
from jinja2 import Environment, FileSystemLoader 
# pylint: disable=format-string-without-interpolation

TEMPLATES = Path(__file__).parent/'templates'


def setup_j2(**kwargs):
    kwargs = dict(trim_blocks=True, lstrip_blocks=True) | kwargs
    # kwargs sólo aplican para los bloques de jinja2 {% for kk in keys %} 
    env = Environment(loader=FileSystemLoader(TEMPLATES), **kwargs)
    env.filters['mapper'] = mapper
    return env

def mapper(f_name, *args):
    funcs = dict(
        query = _query, 
        nulls = _nulls,
        records = _records, 
        transforms = _transforms, 
        params = _params, 
        filters = _filters)
    return funcs[f_name](*args)   


def _query(view, keys): 
    k_temp = ", ".join(kk.name for kk in keys)
    join_on = """
      AND """.join(f"t.{kk.name} = k.{kk.name}" for kk in keys)
    q_template = f""";
    SELECT t.*
    FROM {view} AS t
    JOIN ("& ValuesClause &"
      ) AS k({k_temp})
      ON  {join_on}"""
    return q_template

def _nulls(keys):
    λ_key = lambda k: 'NULL'
    return ', '.join(λ_key(kk) for kk in keys)

def _records(keys): 
    λ_key = lambda k: f'{k.pq_lit}(Record.Field(row, "{k.name}"))'
    return ' & "," &\n\t\t'.join(λ_key(kk) for kk in keys)

def _transforms(keys): 
    λ_key = lambda k: f'{{ "{k.name}", type {k.pq_type} }}'
    return ',\n\t\t'.join(λ_key(kk) for kk in keys)

def _params(keys): 
    λ_key = lambda k: f'{k.excel} = Opt_{k.pq_type}(ReadName("par_{k.name}"))'
    return ',\n\t\t'.join(λ_key(kk) for kk in keys)

def _filters(keys): 
    λ_enumkey = (lambda i,k: 
    f"""Filter{i+1} = if Params[{k.excel}] <> null 
    then Table.SelectRows(Filter{i}, each [{k.excel}] = Params[{k.excel}]) 
    else Filter{i},""")
    return '\n\t'.join(starmap(λ_enumkey, enumerate(keys)))