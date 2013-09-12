# coding=utf-8
from yaml import load


def _load_config():
    """
    Загрузка конфигурации
    """
    config_file = open('config.yml')
    cfg = load(config_file)
    config_file.close()
    return cfg


# Загруженная конфигурация
CONFIG = _load_config()
