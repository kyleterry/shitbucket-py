import json
import os


CONFIG_PATHS = ['/etc/shitbucket/config.json',
                os.environ['HOME'] + '/.config/shitbucket/config.json']
_settings = {}


def find_config():
    for config_path in CONFIG_PATHS:
        if os.path.exists(config_path):
            return config_path
    return None


def load_config_from_file(config_path):
    """
    Loads json config from file. It will memoize too.
    returns dict
    """
    global _settings
    if not _settings:
        with open(config_path) as f:
            _settings = json.load(f)
    print(_settings)
    return _settings


def get_settings(config_file=None):
    if not config_file:
        config_file = find_config()
    if not config_file: # still no config file?!
        raise Exception("No config file found.")

    return load_config_from_file(config_file)
