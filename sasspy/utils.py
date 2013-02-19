import platform
import collections
import inspect

def is_windows():
	return platform.system().lower() == 'windows'

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def abstract(obj):
	raise NotImplementedError("%s must implement %s"%(obj.__class__.__name__, inspect.stack()[1][3]))

def destructure(val):
	return val if val else []