import yaml
from utils.paths import CONFIG_PATH

_config = None

def get_config():
    global _config
    if _config is None:
        with open(CONFIG_PATH, "r") as f:
            _config = yaml.safe_load(f)
    return _config