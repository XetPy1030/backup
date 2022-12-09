from datetime import datetime
import logging

_log_format = f"%(asctime)s %(message)s"

def get_name():
    return "./logs/"+datetime.now().strftime('%m.%d.%Y.log')

def get_file_handler():
    file_handler = logging.FileHandler(get_name())
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger