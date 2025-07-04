from tqdm import tqdm
from queue import Queue
from sentence_transformers import SentenceTransformer

from scripts.config import get_config
from scripts.log_reader import tail_log_source, start_processing_thread
from scripts.log_processor import LogProcessor
from scripts.paths import PROJECT_ROOT
from scripts.logger import setup_logger
from scripts.monitoring.health_registry import registry as health_registry
from scripts.monitoring.health_registry import start_heartbeat 

if __name__ == "__main__":
    config = get_config()
    logger = setup_logger("main", str(PROJECT_ROOT / config["log_file_path"]))

    try:
        logger.info("Initializing BERT model...")
        model = SentenceTransformer(config["bert_model"])

        pbar = tqdm(desc="Processed log lines", unit="lines")
        processor = LogProcessor(model, config, pbar)

        logger.info("Starting log processing thread...")
        line_queue = Queue()
        start_processing_thread(line_queue, processor)

        start_heartbeat("main")

        logger.info("Starting log tailing...")
        tail_log_source(config, line_queue)

    except Exception as e:
        logger.exception("Fatal error occurred in main execution")
        health_registry.update("drift_monitor", "unhealthy")