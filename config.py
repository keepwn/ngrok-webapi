import configparser


def get_config(section, key):
    config = configparser.ConfigParser()
    path = 'data/app.conf'
    config.read(path)
    return config.get(section, key)
