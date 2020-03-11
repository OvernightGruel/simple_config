import os

from simple_config import Config, ConfigAttribute, converter
from simple_config import exceptions

file_dir = os.path.dirname(os.path.abspath(__file__))


class ProjectConfig(Config):
    ETCD_HOST = ConfigAttribute('ETCD_HOST')
    ETCD_PORT = ConfigAttribute('ETCD_PORT', get_converter=int)
    ETCD_USER = ConfigAttribute('ETCD_USER')
    ETCD_PASSWD = ConfigAttribute('ETCD_PASSWD')

    HTTP_SERVER = ConfigAttribute(
        'HTTP_SERVER', get_converter=converter.server)

    DEBUG = ConfigAttribute('DEBUG', get_converter=converter.boolean)
    ALIAS_DEBUG = ConfigAttribute('DEBUG', get_converter=converter.boolean)

    ALLOWED_HOSTS = ConfigAttribute(
        'ALLOWED_HOSTS', get_converter=converter.Csv())


def test_defaults():
    config = ProjectConfig(defaults={'DEBUG': False, 'ETCD_HOST': 'test'})
    assert config.DEBUG is False
    assert config.ALIAS_DEBUG is False
    assert config.ETCD_HOST == 'test'
    try:
        config.ETCD_PORT
    except exceptions.NotConfigured:
        pass
    else:
        raise Exception('exception is expected')


def test_env_file():
    config = ProjectConfig(defaults={'DEBUG': False})
    assert config.DEBUG is False
    config.from_env_file(os.path.join(file_dir, 'test_env'))
    assert config.DEBUG is True
    assert config.ETCD_PORT == 80
    assert config.get_namespace('ETCD_') == {
        'host': '1.1.1.1',
        'passwd': '0hyxdryq_CZ',
        'port': 80,
        'user': 'test'
    }
    assert config.ALLOWED_HOSTS == ['*.test.com', 'api.test.com', '*']
    assert config.ALIAS_DEBUG is True
    assert config.USER_NAME == 'root'


def test_ini():
    config = ProjectConfig(defaults={'DEBUG': False})
    assert config.DEBUG is False
    config.from_ini(os.path.join(file_dir, 'test.ini'))
    assert config.DEBUG is True
    assert config.ETCD_PORT == 80
    assert config.get_namespace('ETCD_') == {
        'host': '1.1.1.1',
        'passwd': '0hyxdryq_CZ',
        'port': 80,
        'user': 'test'
    }
    assert config.ALLOWED_HOSTS == ['*.test.com', 'api.test.com', '*']
    assert config.ALIAS_DEBUG is True
    assert config.USER_NAME == 'root\nroot\nroot\nroot'
