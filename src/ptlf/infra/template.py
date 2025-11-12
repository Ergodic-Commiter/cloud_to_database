from jinja2 import Environment, PackageLoader


def nulls(seq, val='NULL', sep=', '): 
    return sep.join(val for _ in seq)

def join_values(view, keys):
    join_on = """
      AND """.join(f"t.{kk} = k.{kk}" for kk in keys)
    join_query = f""";
    SELECT t.*
    FROM {view} AS t
    JOIN ("& ValuesClause &"
      ) AS k{tuple(keys)} 
      ON  {join_on}"""
    return join_query

def setup_template_env(**kwargs):
    env = Environment(loader=PackageLoader('ptlf', 'data/templates'), **kwargs)
    env.filters['nulls'] = nulls
    env.filters['join_values'] = join_values
    return env
