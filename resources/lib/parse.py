# -*- coding: utf-8 -*-

import sys, copy

if sys.version_info.major >= 3:
    from . import content
else:
    import content
#from operator import itemgetter

def pyStr(ostr, doNothing=False):
    if sys.version_info.major >= 3:
        return str(ostr)
    else:
        if doNothing:
            return ostr
        else:
            return u(ostr)

def u(data):
    return data.encode("utf-8")