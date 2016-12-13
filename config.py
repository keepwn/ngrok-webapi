import os
import configparser


def get_config(section, key):
    config = configparser.ConfigParser()
    path = 'data/app.conf'
    config.read(path)
    return os.environ.get(key.upper()) or config.get(section, key)
