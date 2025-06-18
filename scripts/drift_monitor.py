from tqdm import tqdm
from queue import Queue
from sentence_transformers import SentenceTransformer

from config_loader import load_config
from log_reader import tail_log_file, start_processing_thread
from log_processor import LogProcessor

if __name__ == "__main__":
    config = load_config()
    pbar = tqdm(desc="Processed log lines", unit="lines")
    model = SentenceTransformer(config["bert_model"])
    processor = LogProcessor(model, config, pbar)

    line_queue = Queue()
    start_processing_thread(line_queue, processor)

    print(f"\nMonitoring log file: {config['log_file_path']}")
    tail_log_file(config["log_file_path"], line_queue)