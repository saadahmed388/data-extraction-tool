import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'logs.log'
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(filename)s:%(lineno)d  | %(message)s')
    
    file_handler = RotatingFileHandler(log_file, maxBytes=5242880, backupCount=5)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)