# coding=utf-8
import sys

'''
This module ensure compatibility between Python 2 and 
Python 3.
'''

_ver = sys.version_info

#: Python 2.x?
is_PY2 = (_ver[0] == 2)

#: Python 3.x?
is_PY3 = (_ver[0] == 3)


if is_PY2:
    from urlparse import urlparse

    builtin_str = str
    bytes = str
    str = unicode

elif is_PY3:
    from urllib.parse import urlparse

    builtin_str = str
    bytes = str
    str = unicode




