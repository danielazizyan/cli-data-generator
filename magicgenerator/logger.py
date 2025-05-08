import logging
import sys
from typing import Optional


def get_logger(
        name: str = "magicgenerator",
        log_file: Optional[str] = "logfile.log"
) -> logging.Logger:
    """
    Return a logger that writes INFO+ messages to stderr
    and also to a file by default.

    Parameters:
        name (str): The logger’s namespace (e.g., module name).
                    Defaults to 'magicgenerator'.
        log_file (Optional[str]): Path to a file for duplicating logs.
                                Pass None to disable file logging.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)

    # This check ensures we only add handlers once.
    # Without it, calling get_logger() multiple times would attach
    # multiple StreamHandlers/FileHandlers
    # and log each message repeatedly.
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        # Console handler -> stderr
        # so stdout stays purely for program output
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Prevent messages bubbling up to the root logger
        logger.propagate = False

    return logger
