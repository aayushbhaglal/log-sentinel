from scripts.log_sources.base import LogSource
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import time
import threading

from scripts.monitoring.health_registry import registry as health_registry

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
            
            # Start background heartbeat thread to monitor health
            thread = threading.Thread(target=self._health_heartbeat_loop, daemon=True)
            thread.start()
        except Exception as e:
            health_registry.update("kafka_consumer", "unhealthy")

    def stream(self):
        for message in self.consumer:
            yield message.value.decode("utf-8")

    def _health_heartbeat_loop(self):
        """Background thread that periodically checks Kafka connection health."""
        while True:
            try:
                _ = self.consumer.topics()
                health_registry.update("kafka_consumer", "healthy", "Connected to broker")
            except KafkaError as e:
                health_registry.update("kafka_consumer", "unhealthy", f"Broker error: {e}")
            except Exception as e:
                health_registry.update("kafka_consumer", "unhealthy", f"Unexpected error: {e}")
            time.sleep(5)