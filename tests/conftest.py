import logging


def get_test_logger(name, caplog, level=logging.WARNING):
    """
    Configures and returns a logger for use in test cases.

    Parameters:
        name (str): The name of the logger.
        caplog: The pytest `caplog` fixture to attach to the logger.
        level (int): Logging level (default: logging.WARNING).

    Returns:
        logging.Logger: A logger configured to use `caplog.handler`.
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.addHandler(caplog.handler)
    logger.setLevel(level)
    return logger
