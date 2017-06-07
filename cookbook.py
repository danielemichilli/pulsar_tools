'''A collection of recipies from the "python cookbook". '''

from copy import deepcopy
def resetdefaults(f):
    fdefaults = f.func_defaults
    def refresher(*args, **kwds):
        f.func_defaults = deepcopy(fdefaults)
        return f(*args, **kwds)
    return refresher

def curry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(a+more_a), **dict(kw, **more_kw))
    return curried

def rcurry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(more_a+a), **dict(kw, **more_kw))
    return curried
