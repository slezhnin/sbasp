# coding=utf-8
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def _load_config():
    """
    Загрузка конфигурации
    """
    config_file = open('config.yml')
    cfg = load(config_file, Loader=Loader)
    config_file.close()
    return cfg


# Загруженная конфигурация
CONFIG = _load_config()
