import sys
from configparser import ConfigParser
from pathlib import Path
from typing import Dict
from magicgenerator.logger import get_logger

logger = get_logger(__name__)


def read_defaults() -> Dict[str, str]:
    """
        Reads default configuration values from the 'default.ini' file.

        Returns:
            Dict[str, str]: A dictionary of default settings
            from the [settings] section.

        Raises:
            SystemExit: If the config file is missing or unreadable.
    """

    # Construct the full path to the config file:
    # <project_root>/configs/default.ini
    config_path = Path(__file__).parent.parent / "configs" / "default.ini"

    # Create a ConfigParser object to read .ini-style config files
    config = ConfigParser()

    # Attempt to read the config file
    # returns a list of successfully read files
    read_files = config.read(config_path)   #
    if not read_files:
        logger.error("Could not read config at %s", config_path)
        sys.exit(1)

    # config["settings"] returns a SectionProxy (dict-like view of the section)
    # explicitly convert it to a real dict[str, str] for downstream use
    return dict(config["settings"])
