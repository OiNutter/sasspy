import platform
import collections

def is_windows():
	return platform.system().lower() == 'windows'

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el