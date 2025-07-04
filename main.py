from tqdm import tqdm
from queue import Queue
from sentence_transformers import SentenceTransformer

from scripts.config import get_config
from scripts.log_reader import tail_log_source, start_processing_thread
from processing.log_processor import LogProcessor
from utils.paths import PROJECT_ROOT
from utils.logger import setup_logger
from monitoring.health_registry import registry as health_registry
from monitoring.health_registry import start_heartbeat 

from monitoring.metrics_server import start_metrics_server

start_metrics_server(8000)

if __name__ == "__main__":
    config = get_config()
    logger = setup_logger("main", str(PROJECT_ROOT / config["log_file_path"]))

    try:
        logger.info("Initializing BERT model...")
        model = SentenceTransformer(config["bert_model"])

        processor = LogProcessor(model, config)

        logger.info("Starting log processing thread...")
        line_queue = Queue()
        start_processing_thread(line_queue, processor)

        start_heartbeat("main")

        logger.info("Starting log tailing...")
        tail_log_source(config, line_queue)

    except Exception as e:
        logger.exception("Fatal error occurred in main execution")
        health_registry.update("main", "unhealthy")