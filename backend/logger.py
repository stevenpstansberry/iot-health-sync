import logging
import os

def setup_logger(name="iot_consumer", log_file="iot_consumer.log", level=logging.INFO):
    """
    Sets up a logger with the specified name, log file, and log level.
    
    Args:
        name (str): The name of the logger.
        log_file (str): The file to log messages to.
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create file handler for logging to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Create console handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
