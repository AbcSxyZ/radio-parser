import logging

LOG_FILE = "wikipedia.log"

def setup_logger():
    logger = logging.getLogger("wiki")
    logger.setLevel(logging.DEBUG)

    #Setup log format
    format_log = logging.Formatter("%(levelname)s:%(process)s: %(message)s")

    #Setup log file
    log_file = logging.FileHandler(LOG_FILE)
    log_file.setFormatter(format_log)


    logger.addHandler(log_file)
    return logger


setup_logger()
