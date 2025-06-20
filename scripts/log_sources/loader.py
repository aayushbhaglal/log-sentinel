import sys
import os
from .file_source import FileLogSource
from .base import LogSource

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.paths import PROJECT_ROOT

def get_log_source(config: dict) -> LogSource:
    source_config = config.get("log_source", {})
    source_type = source_config.get("type")

    if source_type == "file":
        return FileLogSource(str(PROJECT_ROOT / source_config["path"]))
    
    raise ValueError(f"Unsupported log source type: {source_type}") # only file logs support for now