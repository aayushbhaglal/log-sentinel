import os
import time
import threading
from queue import Queue

def tail_log_file(filepath, line_queue):
    with open(filepath, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                line_queue.put(line.strip())
            else:
                time.sleep(0.1)

def start_processing_thread(line_queue, processor):
    def loop():
        while True:
            line = line_queue.get()
            processor.process_line(line)
            line_queue.task_done()
    t = threading.Thread(target=loop, daemon=True)
    t.start()