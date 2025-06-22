import sys
import os
from .base import LogSource
from kafka import KafkaConsumer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from monitoring.health_registry import registry as health_registry

class KafkaLogSource(LogSource):
    def __init__(self, topic, bootstrap_servers="localhost:9092", group_id="log-sentinel"):
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset="latest",  # start from the latest messages
                enable_auto_commit=True
            )
            health_registry.update("kafka_consumer", "healthy")
        except Exception as e:
            health_registry.update("kafka_consumer", "unhealthy")

    def stream(self):
        for message in self.consumer:
            yield message.value.decode("utf-8")