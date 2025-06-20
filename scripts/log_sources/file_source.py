import time
from .base import LogSource

class FileLogSource(LogSource):
    def __init__(self, filepath):
        self.filepath = filepath

    def stream(self):
        with open(self.filepath, "r") as f:
            f.seek(0, 2)  # Move to end of file
            while True:
                line = f.readline()
                if line:
                    yield line.strip()
                else:
                    time.sleep(0.1)