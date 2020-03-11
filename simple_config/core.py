from configparser import ConfigParser
import os
import re
import warnings

from .exceptions import (FileDoesNotExist, VariableNotExist, NotConfigured,
                         InvalidConfig)


class Attribute(object):
    """

    >>> from .converter import boolean
    >>> class TestConfig(Config):
    ...     DEBUG = Attribute('DEBUG', boolean)
    ...
    >>> config = TestConfig()
    >>> config.DEBUG
    Traceback (most recent call last):
        ....
    simple_config.exceptions.NotConfigured: value of 'DEBUG' has not been set
    >>> config = TestConfig(defaults={'debug':False})
    >>> config.DEBUG
    False
    >>> config.DEBUG = False
    >>> config._raw_config['debug']
    Traceback (most recent call last):
        ....
    KeyError: 'debug'
    >>> config._raw_config['DEBUG']
    False
    """

    def __init__(self, name, get_converter=None):
        if name.upper() != name:
            warnings.warn('upper case name is expected')
        self.__name__ = name.upper()
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        try:
            rv = obj._raw_config[self.__name__]
        except KeyError:
            raise NotConfigured(
                "value of '%s' has not been set" % self.__name__)
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        obj._raw_config[self.__name__] = value


class Environment(dict):
    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)

    @classmethod
    def from_env_file(cls, filename, load_env=False):
        """从文件中加载环境变量
        """
        if not os.path.exists(filename):
            raise FileDoesNotExist('cannot find file: %s' % filename)
        with open(filename, 'r', encoding='utf8') as f:
            lines = f.readlines()
        dct = dict(os.environ) if load_env else {}

        for line in lines:
            if line.startswith('#'):
                continue
            if '=' not in line:
                if re.match(r'^\s*$', line):
                    continue
                raise InvalidConfig("config line should contain '='")
            key, value = line.strip().split('=', 1)
            if value[0] == value[-1] and value[0] in ('\'', '"'):
                warnings.warn('There is no need to quote string')
            dct[key] = value
        return cls(dct)

    @classmethod
    def from_env(cls):
        return cls(dict(os.environ))


class Config(object):
    INI_SECTION_NAME = 'settings'

    def __init__(self, defaults=None):
        self._raw_config = {}
        defaults and self._update_config(**defaults)

    def from_ini(self, filename):
        """

        >>> config = Config(defaults={'DBEUG': True})
        >>> from tempfile import TemporaryFile
        >>> filename = TemporaryFile().name
        >>> with open(filename, 'w', encoding='utf8') as f:
        ...     f.write('[settings]\\ndebug=false\\n')
        23
        >>> config.from_ini(filename)
        >>> config._raw_config['DEBUG']
        'false'
        >>> with open(filename, 'w', encoding='utf8') as f:
        ...     f.write('[settings]\\ndebug=True\\n')
        22
        >>> config.from_ini(filename)
        >>> config._raw_config['DEBUG']
        'True'
        >>> os.remove(filename)
        """
        config = ConfigParser()
        with open(filename, 'r', encoding='utf8') as f:
            config.read_file(f)
        self._update_config(**config[self.INI_SECTION_NAME])

    def from_env_file(self, filename, load_env=False):
        """

        >>> config = Config(defaults={'DBEUG': True})
        >>> from tempfile import TemporaryFile
        >>> filename = TemporaryFile().name
        >>> with open(filename, 'w', encoding='utf8') as f:
        ...     f.write('debug=false')
        11
        >>> config.from_env_file(filename)
        >>> config._raw_config['DEBUG']
        'false'
        >>> with open(filename, 'w', encoding='utf8') as f:
        ...     f.write('debug=True')
        10
        >>> config.from_env_file(filename)
        >>> config._raw_config['DEBUG']
        'True'
        >>> os.remove(filename)
        """
        self._update_config(**Environment.from_env_file(
            filename, load_env=load_env))

    def from_env_var(self, variable, errors='strict'):
        environ = Environment.from_env()
        value = environ.get(variable)
        if value is None and errors == 'strict':
            raise VariableNotExist('cannot get %s from env' % variable)
        self._update_config(**{variable: value})

    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self._update_config(**{key: getattr(obj, key)})

    def from_dict(self, dct):
        """
        >>> from .converter import boolean
        >>> class NewConfig(Config):
        ...     DEBUG = Attribute('DEBUG', get_converter=boolean)
        ...
        >>> config = NewConfig()
        >>> config.DEBUG
        Traceback (most recent call last):
            ....
        simple_config.exceptions.NotConfigured: \
value of 'DEBUG' has not been set
        >>> config.from_dict({'debug': 'true'})
        >>> config.DEBUG
        True
        >>> config.from_dict({'Debug': ''})
        >>> config.DEBUG
        False

        """
        self._update_config(**dct)

    def _update_config(self, **kwargs):
        for key, value in kwargs.items():
            self._raw_config[key.upper()] = value

    def __setattr__(self, key, value):
        """
        >>> config = Config()
        >>> config._raw_config['DEBUG']
        Traceback (most recent call last):
            ....
        KeyError: 'DEBUG'
        >>> config.DEBUG = False
        >>> config._raw_config
        {'DEBUG': False}
        """
        pre_fields = ('_raw_config', )
        if key in pre_fields:
            super().__setattr__(key, value)
        else:
            if key.upper() != key:
                warnings.warn('upper case attribute is expected')
            key = key.upper()
            self._update_config(**{key: value})

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """
        >>> config = Config(
        ...     defaults={'A_ID': 1, 'A_NAME': 2, 'A_CITY': 3, 'B_ID': 2})
        >>> config.get_namespace('A') == {'_id': 1, '_name': 2, '_city': 3}
        True
        >>> config.get_namespace('A_') == {'id': 1, 'name': 2, 'city': 3}
        True
        >>> config.get_namespace('A_', lowercase=False) \\
        ...     == {'ID': 1, 'NAME': 2, 'CITY': 3}
        True
        >>> config.get_namespace(
        ...        'A_', lowercase=False, trim_namespace=False) \\
        ...     == {'A_ID': 1, 'A_NAME': 2, 'A_CITY': 3}
        True
        """
        dct = {}
        for key in self._raw_config.keys():
            origin_key = key
            if not key.startswith(namespace):
                continue
            if trim_namespace:
                key = key[len(namespace):]
            # if lowercase:
            #     key = key.lower()
            dct[key] = getattr(self, origin_key)
        return dct

    def __getattr__(self, key):
        try:
            return self._raw_config[key]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__, key))
