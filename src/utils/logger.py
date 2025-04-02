import logging
from datetime import datetime


def setup_logger(name="airport_sim", level=logging.INFO):
    """Setup logger for simulation"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(f"logs/simulation_{datetime.now():%Y%m%d_%H%M}.log")

    # Create formatters
    c_format = logging.Formatter("%(levelname)s - %(message)s")
    f_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Add formatters to handlers
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
