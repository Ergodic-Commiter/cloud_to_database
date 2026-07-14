from functools import partial, reduce #, Placeholder as __
from typing import Callable, Iterator, TypeVar
from warnings import warn  

from toolz import dicttoolz as dz
# pylint:disable=invalid-name
# pylint:disable=too-few-public-methods

T = TypeVar('T')


class partial2(partial):   
    """
    partial2(func, *args, **kwargs) with `...` as placeholder to be filled at call time. 
    Rules (deterministic): 
    - Placeholders are filled from left to right.
    - Call-time keywords override stored keywords (like functools.partial).
    - To pass a literal Ellipsis (not placeholder)... it will break, dont use it like that.
    """
    def __init__(self, func:Callable[..., T], *args, 
    kwargs_first:bool=None, **kwargs): 
        super().__init__(self, func, *args, **kwargs)
        if kwargs_first is None:
            kwargs_first=False
            ell_in_args = any(x is ... for x in args)
            ell_in_kargs = any(v is ... for v in kwargs.values())
            ell_msg = (
                "partial2: placeholder `...` appears in both args and kwargs.\n"
                "Defaulting to positional args first (kwargs_first=False)\n"
                "Pass kwargs_first=True to flip behavior")
            if ell_in_args and ell_in_kargs:
                warn(ell_msg)
        self.kwargs_first = kwargs_first

    @staticmethod
    def iter_filler(call_args) -> tuple[Iterator, Callable]:
        args_iter = iter(call_args)
        def its_filler(when): 
            err_msg = f"Not enough arguments to fill {when} placeholder"
            def apply(x): 
                if x is not ...:
                    return x
                try:
                    return next(args_iter)
                except StopIteration as err:
                    raise TypeError(err_msg) from err
            return apply
        return args_iter, its_filler 


    def __call__(self, *args, **keywords) -> T:
        η_args, λ_ellipsis = self.iter_filler(args)
        if self.kwargs_first: 
            keywords_0 = dz.valmap(λ_ellipsis('keyword'), self.keywords)
            args_0 = map(λ_ellipsis('positional'), self.args)
        else: 
            args_0 = map(λ_ellipsis('positional'), self.args)
            keywords_0 = dz.valmap(λ_ellipsis('keyword'), self.keywords) 
        args_1 = tuple(args_0) + tuple(η_args)
        keywords_1 = {**keywords_0, **keywords}        
        return self.func(*args_1, **keywords_1)


def thread(val, *forms):
    """Unify pytoolz.thread_(first|last) with Ellipsis ..."""
    eval_ff = (lambda vv, ff: 
        partial2(*ff)(vv) if isinstance(ff, tuple) else ff(vv))
    return reduce(eval_ff, forms, val)

  
def noner(func:Callable) -> Callable: 
    """Para funciones que se quiebran con None."""
    return lambda x: func(x) if x is not None else None


class classproperty(property):
    def __get__(self, _, owner):
        return self.fget(owner)

