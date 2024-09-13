import logging


def setup_logger(name):
    """
    Create and return a logger with the given name.

    :param name: Name of the logger (usually __name__ of the module calling this function)
    :return: A configured logger instance
    """
    # Create a logger
    logger = logging.getLogger(name)

    # Set the logging level
    logger.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create a handler (for console output)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger
