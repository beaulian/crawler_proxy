# coding=utf-8
from datetime import datetime

from .utils import reachable
from .constants import PROXY_EXPIRE_TIME


class Proxy(object):
    def __init__(self, address=None, schemes=(), expire=PROXY_EXPIRE_TIME):
        if address.startswith('http://'):
            address = address.lstrip('http://')
        elif address.startswith('https://'):
            address = address.lstrip('https://')

        self._address = address
        self._schemes = schemes
        self._create_time = datetime.now()
        self._expire = expire

    def try_connect(self):
        result = reachable(self._address)
        return result

    def is_expired(self):
        return (datetime.now() - self._create_time).seconds >= self._expire

    @property
    def urls(self):
        return ['%s://%s' % (scheme, self._address) for scheme in self._schemes]

    @urls.setter
    def urls(self, value):
        raise ValueError('forbidden to set the field!')

    def __str__(self):
        return '<Proxy address=%s schemes=%s>' % (self._address, str(self._schemes))

    def __repr__(self):
        return self.__str__()