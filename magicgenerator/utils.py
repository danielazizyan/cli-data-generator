import sys
import os
from pathlib import Path
from magicgenerator.logger import get_logger

logger = get_logger(__name__)


def validate_output_path(path_str: str) -> Path:
    """
    Ensures that the provided path exists and is a directory.
    Creates it if necessary.

    Parameters:
        path_str (str): The path to validate or create.

    Returns:
        Path: A Path object pointing to a valid output directory.

    Raises:
        SystemExit: If the path exists and is not a directory, or
        if the directory cannot be created.
    """
    p = Path(path_str)
    if p.exists():
        if not p.is_dir():
            logger.error("Output path %s exists but is not a directory", p)
            sys.exit(1)
    else:
        try:
            # all parent directories are created if they don't already exist
            # if the directory already exists, it moves on and does nothing
            p.mkdir(parents=True, exist_ok=True)
            logger.info("Created output directory %s", p)
        except Exception as e:
            logger.error("Cannot create directory %s: %s", p, e)
            sys.exit(1)
    return p


def validate_min(name: str, value: int, minimum: int = 0) -> None:
    """
    Ensure an integer flag is >= minimum; exit on error.
    (Assumes `value` is already an int, via argparse(type=int))

    Parameters:
        name (str): Name of the argument (for logging).
        value (int): Value to validate.
        minimum (int): Minimum allowed value (default is 0).

    Raises:
        SystemExit: If value is less than the specified minimum.
    """
    if value < minimum:
        logger.error("%s must be >= %d (got %d)", name, minimum, value)
        sys.exit(1)


def cap_multiprocessing(requested: int):
    """
    Ensures that the requested number of processes does not exceed
    the system's CPU count.
    If os.cpu_count() returns None, defaults to 1.

    Parameters:
        requested (int): Number of worker processes requested.

    Returns:
        int: The capped number of processes (<= CPU count).
    """
    # Get number of CPUs;
    # fallback to 1 if os.cpu_count() returns None
    # (can happen on rare systems)
    cpu = os.cpu_count() or 1
    if requested > cpu:
        logger.warning(
            "Requested multiprocessing=%d exceeds CPU count %d, using %d",
            requested, cpu, cpu
        )
        return cpu
    return requested


def clear_old_files(output_dir: Path, base_name: str) -> None:
    """
    Deletes previously generated files in the output directory that
    start with the given base name.

    Parameters:
        output_dir (Path): Directory to search for old files.
        base_name (str): Filenames to be deleted.
    """
    deleted = 0
    for p in output_dir.iterdir():
        if p.is_file() and p.name.startswith(base_name):
            try:
                p.unlink()
                deleted += 1
                logger.info("Deleted old file %s", p)
            except Exception as e:
                logger.error("Failed to delete %s: %s", p, e)
    if deleted:
        logger.info("Cleared %d old files", deleted)
