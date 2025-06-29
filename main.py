import json
import random
import uuid
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from magicgenerator.config import read_defaults
from magicgenerator.generator import DataGenerator
from magicgenerator.parser import SchemaParser, SchemaField
from magicgenerator.cli import build_parser
from magicgenerator.logger import get_logger
from magicgenerator.utils import (
    validate_output_path,
    validate_min,
    cap_multiprocessing,
    clear_old_files
)


def _generate_one(i: int, output_dir: Path, base_name: str, file_prefix: str,
                  data_lines: int, schema_model: dict[str, SchemaField],
                  add_suffix: bool):
    """
    Generates a single .jsonl file with synthetic data.

    Parameters:
        i (int): Index of the file (used for "count" prefix).
        output_dir (Path): Output directory path.
        base_name (str): Base name for the output file.
        file_prefix (str): File prefix mode ("count", "random", or "uuid").
        data_lines (int): Number of records to generate.
        schema_model (dict[str, SchemaField]): Field generation rules.
        add_suffix (bool): Whether to add a suffix to the file name.

    Returns:
        Path: Path to the generated output file.
    """
    if file_prefix == "count":
        suffix = str(i + 1)
    elif file_prefix == "random":
        suffix = str(random.randint(0, 10000))
    else:
        suffix = str(uuid.uuid4())

    filename = (
        f"{base_name}_{suffix}.jsonl" if add_suffix
        else f"{base_name}.jsonl"
    )
    out_path = output_dir / filename
    gen = DataGenerator(schema_model)
    gen.write_jsonl_file(out_path, data_lines)
    return out_path


def main():
    """
    Main execution flow for the CLI tool.

    Steps:
        1. Load defaults and parse CLI arguments.
        2. Validate input paths and numeric values.
        3. Load and parse the input schema.
        4. Optionally clear previously generated files.
        5. Generate data:
            - If files_count == 0: print to stdout.
            - If files_count == 1: generate one file.
            - If files_count > 1: use multiprocessing to generate files.

    Raises:
        SystemExit: On invalid input or configuration errors.
    """
    # 1) Load default configuration, parse the command-line args
    logger = get_logger()
    defaults = read_defaults()
    parser = build_parser(defaults)
    args = parser.parse_args()

    logger.info("Starting magicgenerator with args: %s", vars(args))

    # 2) Validate path & numerics
    output_dir = validate_output_path(args.path_to_save_files)
    validate_min("files_count", args.files_count, 0)
    validate_min("multiprocessing", args.multiprocessing, 0)
    args.multiprocessing = cap_multiprocessing(args.multiprocessing)

    logger.info("Validated all inputs")

    # 3) Load raw schema (dict[str,str])
    raw_schema = SchemaParser.load_schema(args.data_schema)

    # 3) Parse that raw schema into SchemaField objects
    schema_model = SchemaParser.build_schema_model(raw_schema)
    logger.info("Built schema model with fields: %s",
                ", ".join(schema_model.keys()))


    # 4) Clear old files if clear_path is True
    if args.clear_path:
        clear_old_files(output_dir, args.file_name)

    # 5) Generate and output data
    if args.files_count == 0:
        logger.info("Entering stdout mode (no files will be written)")
        gen = DataGenerator(schema_model)
        for _ in range(args.data_lines):
            rec = gen.generate_record()
            print(json.dumps(rec))

    elif args.files_count == 1:
        path = _generate_one(
            0,
            output_dir,
            args.file_name,
            args.file_prefix,
            args.data_lines,
            schema_model,
            add_suffix=False
        )
        logger.info("Completed %s", path)

    else:
        with ProcessPoolExecutor(max_workers=args.multiprocessing) as executor:
            futures = [
                executor.submit(
                    _generate_one,
                    i,
                    output_dir,
                    args.file_name,
                    args.file_prefix,
                    args.data_lines,
                    schema_model,
                    add_suffix=True
                )
                for i in range(args.files_count)
            ]

            for future in as_completed(futures):
                try:
                    path = future.result()
                    logger.info("Completed %s", path)
                except Exception as e:
                    logger.error("Worker failed to generate a file: %s", e)


if __name__ == "__main__":
    main()
