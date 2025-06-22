from tqdm import tqdm
from queue import Queue
from sentence_transformers import SentenceTransformer

from config_loader import load_config
from log_reader import tail_log_source, start_processing_thread
from log_processor import LogProcessor
from paths import CONFIG_PATH
from paths import PROJECT_ROOT
from logger import setup_logger
from monitoring.health_registry import registry as health_registry


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)
    logger = setup_logger("DriftMonitor", str(PROJECT_ROOT / config["log_file_path"]))

    try:
        logger.info("Initializing BERT model...")
        model = SentenceTransformer(config["bert_model"])

        pbar = tqdm(desc="Processed log lines", unit="lines")
        processor = LogProcessor(model, config, pbar)

        logger.info("Starting log processing thread...")
        line_queue = Queue()
        start_processing_thread(line_queue, processor)
        health_registry.update("drift_monitor", "healthy")

        logger.info("Starting log tailing...")
        tail_log_source(config, line_queue)

    except Exception as e:
        logger.exception("Fatal error occurred in main execution")
        health_registry.update("drift_monitor", "unhealthy")