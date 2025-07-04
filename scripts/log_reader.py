import threading
from queue import Queue
from scripts.log_sources.loader import get_log_source
from scripts.log_sources.base import LogSource

def tail_log_source(config: dict, line_queue: Queue):
    log_source: LogSource = get_log_source(config)

    for line in log_source.stream():
        line_queue.put(line)

    return line_queue
    

def start_processing_thread(line_queue, processor):
    def loop():
        while True:
            line = line_queue.get()
            processor.process_line(line)
            line_queue.task_done()
    t = threading.Thread(target=loop, daemon=True)
    t.start()