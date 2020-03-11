import sys

from .core import Config
from .core import Attribute as ConfigAttribute


class Const(object):
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't change const.{}".format(name))
        if not name.isupper():
            raise self.ConstCaseError(
                "const name {} is not all uppercase".format(name))
        self.__dict__[name] = value

    @classmethod
    def from_current_module(cls, name):
        current_module = sys.modules[name]
        _const = cls()
        for key in dir(current_module):
            if not key.isupper():
                continue
            setattr(_const, key, getattr(current_module, key))
        return _const


__name__ = "simple_config"
__all__ = ('Config', 'ConfigAttribute', 'const')
__version__ = '1.2'
