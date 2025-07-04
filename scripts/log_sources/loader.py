from scripts.log_sources.file_source import FileLogSource
from scripts.log_sources.kafka_source import KafkaLogSource
from scripts.log_sources.base import LogSource

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