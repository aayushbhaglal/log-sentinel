import sys
import os
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from paths import CONFIG_PATH
from paths import PROJECT_ROOT
from config_loader import load_config
import json


class HealthRegistry:
    def __init__(self):
        config = load_config(CONFIG_PATH)
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
            if component_name=="log_processor":
                entry = self._registry.get(component_name)
                if entry and (time.time() - entry["timestamp"] > self.timeout):
                    return {"status": "stale", "message": "timeout expired", "timestamp": None}            

            return self._registry.get(component_name, {"status": "UNKNOWN", "message": "Not reported", "timestamp": None})

    def all(self):
        with self._lock:
            return dict(self._registry)
    
    def _save_loop(self):
        while True:
            try:
                with self._lock:
                    with open(self.output_path, "w") as f:
                        json.dump(self._registry, f, indent=2)
            except Exception as e:
                print(f"[HealthRegistry] Failed to write health file: {e}")
            time.sleep(3)
        
registry = HealthRegistry()