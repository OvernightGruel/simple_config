# simple_config

Python项目的配置信息工具，可以从解析配置文件、环境变量。

## Getting Started


### Installing


```
$: git clone git@gitlab.situdata.com:zhouweiqi/simple_config.git
$: pip install -e simple_config
```


### QuickStart


**配置文件**

创建配置文件`test.ini`, 内容如下：

```
ETCD_HOST=1.1.1.1
ETCD_PORT=80
ETCD_PASSWD=0hyxdryq_CZ
ETCD_USER=test
HTTP_SERVER=http://test.com
DEBUG=true
ALLOWED_HOSTS=*.test.com, api.test.com,  *
USER_NAME=root
```

解析配置文件

```python
In [2]: from simple_config import Config, ConfigAttribute, converter
In [3]: class ProjectConfig(Config):
   ...:     ETCD_HOST = ConfigAttribute('ETCD_HOST')
   ...:     ETCD_PORT = ConfigAttribute('ETCD_PORT', get_converter=int)
   ...:     ETCD_USER = ConfigAttribute('ETCD_USER')
   ...:     ETCD_PASSWD = ConfigAttribute('ETCD_PASSWD')
   ...: 
   ...:     HTTP_SERVER = ConfigAttribute(
   ...:         'HTTP_SERVER', get_converter=converter.server)
   ...: 
   ...:     DEBUG = ConfigAttribute('DEBUG', get_converter=converter.boolean)
   ...:     ALIAS_DEBUG = ConfigAttribute('DEBUG', get_converter=converter.boolean)
   ...: 
   ...:     ALLOWED_HOSTS = ConfigAttribute(
   ...:         'ALLOWED_HOSTS', get_converter=converter.Csv())
   ...: 
   ...: 
   ...: config = ProjectConfig(defaults={'DEBUG': False})

In [4]: config.DEBUG
Out[4]: False

In [5]: config.from_env_file('test.ini')

In [6]: config.DEBUG
Out[6]: True

In [7]: config.ETCD_PORT
Out[7]: 80

In [8]: config.get_namespace('ETCD_')
Out[8]: {'host': '1.1.1.1', 'passwd': '0hyxdryq_CZ', 'port': 80, 'user': 'test'}

In [9]: config.ALLOWED_HOSTS
Out[9]: ['*.test.com', 'api.test.com', '*']

In [10]: config.ALIAS_DEBUG
Out[10]: True

In [11]: config.USER_NAME  # 获取配置文件中有，但是Config没有声明的配置
Out[11]: 'root'

In [12]: config.HTTP_SERVER
Out[12]: Server(scheme='http', host='test.com', port=80)

```


**常量**

创建文件`const.py`, 内容如下

```python
import sys
from simple_config import Const

A = 1
B = 2


sys.modules[__name__] = Const.from_current_module(__name__)
```

加载常量

```python
In [1]: import const
In [2]: const
Out[2]: <simple_config.Const at 0x7fc59c9475c0>
In [3]: const?
Type:        Const
String form: <simple_config.Const object at 0x7fc59c9475c0>
Docstring:   <no docstring>
In [4]: const.A
Out[4]: 1
In [5]: const.B
Out[5]: 2
In [6]: const.A = 3  # 不能修改已有变量值
---------------------------------------------------------------------------
ConstError                                Traceback (most recent call last)
<ipython-input-6-d1e1d5d0fa5a> in <module>
----> 1 const.A = 3

~/code/simple_config/simple_config/__init__.py in __setattr__(self, name, value)
     14     def __setattr__(self, name, value):
     15         if name in self.__dict__:
---> 16             raise self.ConstError("Can't change const.{}".format(name))
     17         if not name.isupper():
     18             raise self.ConstCaseError(

ConstError: Can't change const.A
```



## Test

1. 安装依赖

    ```bash
    $ pip install nose coverage
    ```

2. 运行测试

    ```
    nosetests -c .setup.cfg
    ```
