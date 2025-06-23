import sys
import os
import threading
import time
import tempfile
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from paths import PROJECT_ROOT
from config import get_config
import json


class HealthRegistry:
    def __init__(self):
        config = get_config()
        self._lock = threading.Lock()
        self._registry = {}
        self.timeout = 15
        self.output_path = str(PROJECT_ROOT / config["health_logs_path"])
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Start the background thread to save health data periodically
        thread = threading.Thread(target=self._save_loop, daemon=True)
        thread.start()

    def update(self, component_name, status, message="OK"):
        with self._lock:
            self._registry[component_name] = {
                "status": status,
                "message": message,
                "timestamp": time.time()
            }

    def get(self, component_name):
        with self._lock:
            entry = self._registry.get(component_name)
            if self.is_stale(entry, self.timeout):
                return {"status": "stale", "message": "timeout expired", "timestamp": None}            

            return self._registry.get(component_name, {"status": "UNKNOWN", "message": "Not reported", "timestamp": None})

    def all(self):
        with self._lock:
            return dict(self._registry)
    
    def _save_loop(self):
        while True:
            try:
                with self._lock:
                    temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(self.output_path))
                    with os.fdopen(temp_fd, "w") as tmp_file:
                        json.dump(self._registry, tmp_file, indent=2)
                    shutil.move(temp_path, self.output_path)
            except Exception as e:
                print(f"[HealthRegistry] Failed to write health file: {e}")
            time.sleep(3)

    def is_stale(self, entry, timeout):
        return time.time() - entry["timestamp"] > timeout
    
    def heartbeat(self, component_name):
        self.update(component_name, "healthy", "heartbeat")
        
registry = HealthRegistry()

def start_heartbeat(component_name: str, interval: int = 5):
        def heartbeat_loop():
            while True:
                registry.heartbeat(component_name)
                time.sleep(interval)
        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()