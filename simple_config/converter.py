from collections import namedtuple
import re
import string
from shlex import shlex

from .exceptions import ConvertError

__all__ = ('host_port', 'server', 'Csv')

Server = namedtuple('Server', 'scheme host port')

host_port_pattern = re.compile(
    r'^(?P<host>[0-9a-zA-Z\-.]+)(?:\:(?P<port>\d{1,5}))?$')


def host_port(string):
    """
    解析"host:port"字符串

    >>> host_port('dev.some-host.org:60000')
    Server(scheme=None, host='dev.some-host.org', port=60000)
    >>> host_port('8.8.8.8:8080')
    Server(scheme=None, host='8.8.8.8', port=8080)
    >>> host_port('8.8.8.8')
    Server(scheme=None, host='8.8.8.8', port=None)
    >>> res = host_port('dev.some-host.org:600000')
    Traceback (most recent call last):
        ...
    simple_config.exceptions.ConvertError: invalid host_port \
string: dev.some-host.org:600000

    """
    match = host_port_pattern.match(string)
    if not match:
        raise ConvertError('invalid host_port string: %s' % string)
    port = match.group('port') and int(match.group('port'))
    return Server(None, match.group('host'), port)


http_server_pattern = re.compile(
    r'^(?P<schema>https?)://(?P<host>[0-9a-zA-Z\-.]+)(?:\:(?P<port>\d{1,5}))?$'
)


def server(string):
    """
    解析"http://host:port"字符串

    >>> server('http://dev.some-host.org:60000')
    Server(scheme='http', host='dev.some-host.org', port=60000)
    >>> server('https://8.8.8.8:8080')
    Server(scheme='https', host='8.8.8.8', port=8080)
    >>> server('http://8.8.8.8')
    Server(scheme='http', host='8.8.8.8', port=80)
    >>> res = server('dev.some-host.org:600000')
    Traceback (most recent call last):
        ...
    simple_config.exceptions.ConvertError: invalid http_server \
string: dev.some-host.org:600000


    """
    match = http_server_pattern.match(string)
    if not match:
        raise ConvertError('invalid http_server string: %s' % string)
    port = match.group('port') and int(match.group('port'))
    if not port:
        port = 80 if match.group('schema') == 'http' else 443
    return Server(match.group('schema'), match.group('host'), port)


def boolean(instance):
    """
    根据输入，返回是否为True

    >>> boolean(True)
    True
    >>> boolean('True')
    True
    >>> boolean('TRUE')
    True
    >>> boolean('false')
    False
    >>> boolean(None)
    Traceback (most recent call last):
        ...
    simple_config.exceptions.ConvertError: expected boolean or str, \
but get <class 'type'>

    """
    if isinstance(instance, bool):
        return instance
    elif isinstance(instance, str):
        if instance.upper() == 'TRUE':
            return True
        return False
    raise ConvertError('expected boolean or str, but get %s' % type(object))


class Csv(object):
    """
    Produces a csv parser that return a list of transformed elements.

    origin code is here
    https://github.com/henriquebastos/python-decouple/blob/master/decouple.py
    >>> csv = Csv()
    >>> hosts = "*,*.test.com, demo.test.com   ,test.org"
    >>> csv(hosts)
    ['*', '*.test.com', 'demo.test.com', 'test.org']
    >>> csv = Csv(delimiter=';；')
    >>> string = 'a;b; c；D'
    >>> csv(string)
    ['a', 'b', 'c', 'D']
    >>> hosts = "*,*.test.com, demo.test.com   ,test.org"
    >>> csv(hosts)
    ['*,*.test.com, demo.test.com   ,test.org']
    """

    def __init__(self,
                 cast=str,
                 delimiter=',',
                 strip=string.whitespace,
                 post_process=list):
        """
        Parameters:
        cast -- callable that transforms the item just before
                it's added to the list.
        delimiter -- string of delimiters chars passed to shlex.
        strip -- string of non-relevant characters to be passed to
                 str.strip after the split.
        """
        self.cast = cast
        self.delimiter = delimiter
        self.strip = strip
        self.post_process = post_process

    def __call__(self, value):
        """The actual transformation"""

        def transform(s):
            return self.cast(s.strip(self.strip))

        splitter = shlex(value, posix=True)
        splitter.whitespace = self.delimiter
        splitter.whitespace_split = True

        return self.post_process(transform(s) for s in splitter)
