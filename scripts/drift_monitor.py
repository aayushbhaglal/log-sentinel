from tqdm import tqdm
from queue import Queue
from sentence_transformers import SentenceTransformer

from config_loader import load_config
from log_reader import tail_log_source, start_processing_thread
from log_processor import LogProcessor
from paths import CONFIG_PATH



if __name__ == "__main__":
    config = load_config(CONFIG_PATH)
    pbar = tqdm(desc="Processed log lines", unit="lines")
    model = SentenceTransformer(config["bert_model"])
    processor = LogProcessor(model, config, pbar)

    line_queue = Queue()
    start_processing_thread(line_queue, processor)

    tail_log_source(config, line_queue)