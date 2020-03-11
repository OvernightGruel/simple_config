import sys

from simple_config import Const


A = 1
A = 2
# b = 1


sys.modules[__name__] = Const.from_current_module(__name__)
