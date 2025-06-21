# scripts/log_sources/kafka_source.py
from .base import LogSource
from kafka import KafkaConsumer

class KafkaLogSource(LogSource):
    def __init__(self, topic, bootstrap_servers="localhost:9092", group_id="log-sentinel"):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="latest",  # start from the latest messages
            enable_auto_commit=True
        )

    def stream(self):
        for message in self.consumer:
            yield message.value.decode("utf-8")