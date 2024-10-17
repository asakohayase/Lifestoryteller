import logging
import sys

def setup_logger(name: str, level=logging.INFO):
    """
    Set up a logger that only logs to the console.
    
    :param name: Name of the logger (usually __name__ of the module calling this function)
    :param level: Logging level (default is INFO)
    :return: Configured logger instance
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create a console handler and set level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger

# Create a main application logger
main_logger = setup_logger('family_book_app')