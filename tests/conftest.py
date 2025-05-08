import logging


def get_test_logger(name, caplog, level=logging.WARNING):
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.addHandler(caplog.handler)
    logger.setLevel(level)
    return logger
