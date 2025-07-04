import csv
import os
import numpy as np

from utils.utils import cosine_distance
from utils.parser import parse_log_line  
from utils.paths import PROJECT_ROOT
from utils.logger import setup_logger

from monitoring.health_registry import registry as health_registry
from monitoring.alerts import console_alert
from monitoring.metrics_server import update_drift_score, increment_alerts, increment_centroid_updates

class LogProcessor:
    def __init__(self, model, config):
        self.logger = setup_logger("log-processor", str(PROJECT_ROOT / config["log_file_path"]))
        self.model = model
        self.config = config
        self.buffer = []
        self.timestamps = []  #Track timestamps for each embedding
        self.last_centroid = None
        self.line_counter = 0
        self.drift_streak = 0
        self.drift_patience = config.get("drift_patience", 3)

        self.stride = int(config["window_size"] * (1 - config["overlap"])) or 1
        self.output_file = str(PROJECT_ROOT / config["drift_history_file_path"])

        if not os.path.exists(self.output_file):
            with open(self.output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "start_line", "end_line", "start_timestamp", "end_timestamp", "drift_score", "alert", "centroid_updated"
                ])

    def process_line(self, line):
        try:
            timestamp, message = parse_log_line(line)
            if not message:
                return

            embedding = self.model.encode(message)
            self.buffer.append(embedding)
            self.timestamps.append(timestamp)
            self.line_counter += 1

            if len(self.buffer) >= self.config["window_size"]:
                start_line = self.line_counter - len(self.buffer)
                end_line = start_line + self.config["window_size"] - 1

                start_timestamp = self.timestamps[0] if self.timestamps else ""
                end_timestamp = self.timestamps[self.config["window_size"] - 1] if len(self.timestamps) >= self.config["window_size"] else ""

                current_window = self.buffer[:self.config["window_size"]]
                current_centroid = np.mean(current_window, axis=0)

                drift = None
                alert = False
                updated = False

                if self.last_centroid is not None:
                    drift = cosine_distance(self.last_centroid, current_centroid)
                    alert = drift > self.config["drift_threshold"] 

                    update_drift_score(drift)

                    if alert:
                        increment_alerts()
                        console_alert(f"Drift detected with score {drift:.4f}")
                        self.drift_streak += 1
                        if self.drift_streak >= self.drift_patience:
                            increment_centroid_updates()
                            self.last_centroid = current_centroid
                            updated = True
                            self.drift_streak = 0
                            console_alert(f"Drift patience exceeded. Updating centroid.")
                    else:
                        self.drift_streak = 0
                    self.logger.info(
                        f"[DRIFT] {start_line}-{end_line} | Score: {drift:.4f} | Alert: {alert} | Updated: {updated}"
                    )

                    with open(self.output_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            start_line, end_line, start_timestamp, end_timestamp, round(drift, 4), alert, updated
                        ])
                else:
                    self.last_centroid = current_centroid

                # Slide window
                self.buffer = self.buffer[self.stride:]
                self.timestamps = self.timestamps[self.stride:]

            health_registry.update("log_processor", "healthy")
        
        except Exception as e:
            self.logger.error(f"Error processing line {self.line_counter}: {e}")
            health_registry.update("log_processor", "unhealthy")