import time
import uuid
import random
import json
from pathlib import Path
from typing import Any, Dict
from magicgenerator.parser import SchemaField
from magicgenerator.logger import get_logger

logger = get_logger(__name__)


def gen_timestamp(_: SchemaField) -> str:
    return str(time.time())


def gen_empty(field: SchemaField) -> Any:
    """Empty value: '' for str, None for int."""
    return field.const  # we set const="" or const=None in parser


def gen_rand_uuid(_: SchemaField) -> str:
    return str(uuid.uuid4())


def gen_rand_int(_: SchemaField) -> int:
    return random.randint(0, 10000)


def gen_rand_range(field: SchemaField) -> int:
    min_val, max_val = field.args
    return random.randint(min_val, max_val)


def gen_choice(field: SchemaField) -> Any:
    return random.choice(field.args)


def gen_constant(field: SchemaField) -> Any:
    return field.const


# Map of generation modes → handler functions
# Each mode must match a SchemaField.mode from parser
_GEN_MAP = {
    "timestamp":    gen_timestamp,
    "empty":        gen_empty,
    "rand_uuid":    gen_rand_uuid,
    "rand_int":     gen_rand_int,
    "rand_range":   gen_rand_range,
    "choice":       gen_choice,
    "constant":     gen_constant,
}


def generate_record(schema_model: Dict[str, SchemaField]) -> Dict[str, Any]:
    """
    Given a dict of field_name -> SchemaField, produce one dict of
    field_name → generated value.

    Parameters:
        schema_model (Dict[str, SchemaField]): Parsed schema field model.

    Returns:
        Dict[str, Any]: Record with generated values per field.
    """
    record = {}
    for name, field in schema_model.items():
        fn = _GEN_MAP[field.mode]
        record[name] = fn(field)
    return record


def write_jsonl_file(
        output_path: Path,
        schema_model: Dict[str, SchemaField],
        data_lines: int
) -> None:
    """
    Write `data_lines` JSON‐Lines to `output_path`.

    Parameters:
        output_path (Path): Where to write the file.
        schema_model (Dict[str, SchemaField]): Schema for generating data.
        data_lines (int): Number of lines (records) to write.
    """
    logger.info("Generating %d lines → %s", data_lines, output_path)
    with output_path.open("w", encoding="utf-8") as f:
        for i in range(data_lines):
            rec = generate_record(schema_model)
            f.write(json.dumps(rec))
            f.write("\n")
