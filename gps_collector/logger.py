import logging
import os
from datetime import datetime
from .config import Config

def configure_logger(config: Config) -> logging.Logger:
    """Configure application-wide logging."""
    logger = logging.getLogger('gps_collector')
    
    # Get log level from config
    log_level = config.get_log_level()
    logger.setLevel(log_level)

    # Prevent duplicate handlers
    if not logger.handlers:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get the current date to create a daily log file
        current_date = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(script_dir, f'../logs/qanalytics_integration_{current_date}.log')

        handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
