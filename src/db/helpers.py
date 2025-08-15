
from operator import attrgetter as ɑ

# pylint: disable=invalid-name


class classproperty(property):              
    def __get__(self, _, owner):
        return self.fget(owner)


def noner(func): 
    return lambda x: func(x) if x is not None else None


def dicter(keys): 
    return lambda obj: dict(zip(keys, ɑ(*keys)(obj)))


def specs_dicter(keys): 
    def matcher(raw): 
        match raw: 
            case dict() as dd:
                return dd 
            case obj if hasattr(obj, '_asdict'): 
                return obj._asdict()
            case obj: 
                return dicter(keys)(obj)
    return matcher