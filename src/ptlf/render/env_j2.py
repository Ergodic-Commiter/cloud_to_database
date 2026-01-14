from jinja2 import Environment, FileSystemLoader 
# pylint: disable=format-string-without-interpolation


def setup_j2(**kwargs):
    env = Environment(loader=FileSystemLoader('src/ptlf/render/templates'), **kwargs)
    env.filters['mapper'] = mapper
    return env

def mapper(f_name, *args):
    funcs = {
        'query': _query, 
        'nulls': _nulls,
        'records': _records, 
        'transforms': _transforms}
    return funcs[f_name](*args)   


def _query(view, keys): 
    q_template = f"""
    SELECT t.*
    FROM {view} AS t
    JOIN ("& ValuesClause &"
      ) AS k{tuple(keys)}
      ON  {{0}}"""
    join_on = "\n\t  AND ".join(f"t.{kk} = k.{kk}" for kk in keys)
    return q_template.format(join_on)

def _nulls(keys):
    λ_key = 'NULL'.format
    return ', '.join(λ_key(kk) for kk in keys)

def _records(keys): 
    λ_key = '{0.pqlit}(Record.Field(row "{0.name}"))'.format
    return ' & "," &\n\t'.join(λ_key(kk) for kk in keys)

def _transforms(keys): 
    λ_key = '{{ "{0.name}", type {0.pqtype} }}'.format
    return ',\n\t'.join(λ_key(kk) for kk in keys)

