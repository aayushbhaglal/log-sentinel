import sys
import os
from .file_source import FileLogSource
from .kafka_source import KafkaLogSource
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
    elif source_type == "kafka":
        return KafkaLogSource(
            topic=source_config.get("topic"),
            bootstrap_servers=source_config.get("bootstrap_servers"),
            group_id=source_config.get("group_id")
        )
    
    raise ValueError(f"Unsupported log source type: {source_type}")