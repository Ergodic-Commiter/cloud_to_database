from functools import partial, reduce 
from pathlib import Path
from typing import Union

from toolz import functoolz as fz

from .helpers import shortcut_target, str_camel_to_snake, OpenTable


class partial2(partial):   
    """An improved version of partial that uses Ellipsis (...) as a placeholder."""
    def __init__(self, func, *args, kwargs_first=None, **kwargs): 
        if ((kwargs_first is None)
            and (any(x is ... for x in args))
            and (any(v is ... for x in kwargs.values()))): 
            warn("Positional arguments with ... are evaluated before keyword ones."
                "\nUse kwargs_first=True to control behavior.")
            kwargs_first = False
        self.kwargs_first = kwargs_first

    def __call__(self, *args, **keywords):
        # notation is tricky: 
        # η for iterator, λ for lambdas, 0 intermediate vars, 1 final vars.  
        η_args = iter(args)
        λ_ellipsis = lambda x: next(η_args) if x is ... else x
        if self.kwargs_first: 
            keywords_0 = {k: λ_ellipsis(v) for k, v in self.keywords.items()}
            args_1 = tuple(λ_ellipsis(arg) for arg in self.args) + tuple(η_args)
        else: 
            args_0 = (λ_ellipsis(arg) for arg in self.args)
            keywords_0 = {k: λ_ellipsis(v) for k, v in self.keywords.items()}
            args_1 = tuple(args_0) + tuple(η_args)
        keywords_1 = {**keywords_0, **keywords}        
        return self.func(*args_1, **keywords_1)


def star(func):
    # Unpacks star operator:  star(func)(args) := func(*args) 
    return lambda args: func(*args)


def thread(val, *forms):
    # Unify pytoolz.thread_(first|last) with Ellipsis ...
    eval_ff = (lambda vv, ff: 
        partial2(*ff)(vv) if isinstance(ff, tuple) else ff(vv))
    return reduce(eval_ff, forms, val)
    
