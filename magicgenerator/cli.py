import sys
import argparse
from typing import Dict
from magicgenerator.logger import get_logger

logger = get_logger(__name__)


class FatalArgumentParser(argparse.ArgumentParser):
    """
    An ArgumentParser that routes all parsing errors
    through the project's logger and exits with status code 1

    Overrides:
        error(message: str): Log the error via logger.error and exit(1)
        instead of printing a traceback or exiting with code 2.
    """
    def error(self, message: str) -> None:
        # Show correct CLI usage format to stderr before exiting
        self.print_usage(sys.stderr)
        logger.error("Argument error: %s", message)
        sys.exit(1)


def build_parser(defaults: Dict[str, str]) -> argparse.ArgumentParser:
    """
    Constructs and returns an argument parser for the magicgenerator tool,
    using default values provided by the user or config.
    Parameters:
        defaults (Dict[str, str]): Dictionary of default values.

    Returns:
        argparse.ArgumentParser: Fully configured argument parser object.
    """
    p = FatalArgumentParser(
        prog="magicgenerator",
        description="Generate JSON test data files "
                    "based on the given data schema."
    )

    p.add_argument(
        "path_to_save_files",
        nargs="?",
        default=defaults["path_to_save_files"],
        help="Output directory (relative or absolute)."
             "(Default: %(default)s)"
    )

    p.add_argument(
        "--files_count", "-n",
        type=int,
        default=int(defaults["files_count"]),
        help="How many files to generate (0 = stdout)."
             "(Default: %(default)s)"
    )

    p.add_argument(
        "--file_name",
        default=defaults["file_name"],
        help="Base file name (without .json extension)."
             "(Default: %(default)s)"
    )

    p.add_argument(
        "--file_prefix",
        choices=["count", "random", "uuid"],
        default=defaults["file_prefix"],
        help="Which prefix to attach when generating multiple files. "
             "(Default: %(default)s)"
    )

    p.add_argument(
        "--data_schema",
        type=str,
        default=defaults["data_schema"],
        help="JSON schema string or path to a .json file."
             "(Default: %(default)s)"
    )

    p.add_argument(
        "--data_lines",
        type=int,
        default=int(defaults["data_lines"]),
        help="Number of JSON-lines per file."
             "(Default: %(default)s)"
    )

    p.add_argument(
        "--multiprocessing",
        type=int,
        default=int(defaults["multiprocessing"]),
        help="Number of worker processes (capped to CPU cores)."
             "(Default: %(default)s)"
    )

    p.add_argument(
        "--clear_path",
        action="store_true",
        default=defaults["clear_path"].lower() == "true",
        help="Remove existing matching files before generating."
             "(Default: %(default)s)"
    )

    return p
