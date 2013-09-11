# coding=utf-8


_cfg = None


def load_config():
    """
    Загрузка конфигурации
    """
    global _cfg
    if _cfg:
        return _cfg
    cfg_file = {}
    execfile('app.config.py', cfg_file)
    _cfg = cfg_file['config']
    print 'config', '=', _cfg
    return _cfg


# Загруженная конфигурация
CONFIG = load_config()
