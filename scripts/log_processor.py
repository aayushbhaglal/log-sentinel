import csv
import os
from tqdm import tqdm
import numpy as np
from utils import cosine_distance

class LogProcessor:
    def __init__(self, model, config, pbar):
        self.model = model
        self.config = config
        self.pbar = pbar
        self.buffer = []
        self.last_centroid = None
        self.line_counter = 0

        self.stride = int(config["window_size"] * (1 - config["overlap"])) or 1
        self.output_file = config["drift_history_file_path"]

        if not os.path.exists(self.output_file):
            with open(self.output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["start_line", "end_line", "drift_score", "alert"])

    def process_line(self, line):
        embedding = self.model.encode(line)
        self.buffer.append(embedding)
        self.line_counter += 1

        if len(self.buffer) >= self.config["window_size"]:
            start_line = self.line_counter - len(self.buffer)
            end_line = start_line + self.config["window_size"] - 1
            current_window = self.buffer[:self.config["window_size"]]
            current_centroid = np.mean(current_window, axis=0)

            drift = None
            alert = False
            if self.last_centroid is not None:
                drift = cosine_distance(self.last_centroid, current_centroid)
                alert = drift > self.config["drift_threshold"]
                tqdm.write(f"[DRIFT] {start_line}-{end_line} | Score: {drift:.4f}{' 🚨' if alert else ''}")
                with open(self.output_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([start_line, end_line, round(drift, 4), alert])

            self.last_centroid = current_centroid
            self.buffer = self.buffer[self.stride:]
        self.pbar.update(1)