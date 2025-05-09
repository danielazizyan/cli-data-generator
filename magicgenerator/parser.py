import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Literal
from magicgenerator.logger import get_logger

logger = get_logger(__name__)


def load_schema(schema_arg: str) -> Dict[str, str]:
    """
    Accepts either:
        - a path to a .json schema file, or
        - an inline JSON string.

    Returns:
        Dict[str, str]: Dictionary mapping
                        field names to their generation spec strings.

    Raises:
        SystemExit: If the file is unreadable, the input is not valid JSON,
        or the result is not a str-to-str dictionary.
    """
    schema_path = Path(schema_arg)

    if schema_path.is_file():
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            logger.info("Loaded schema from file %s", schema_path)
        except Exception as e:
            logger.error(
                "Failed to load JSON schema file %s: %s",
                schema_path, e
            )
            sys.exit(1)
    else:
        try:
            schema = json.loads(schema_arg)
            logger.info("Parsed inline JSON schema")
        except json.JSONDecodeError as e:
            logger.error("Invalid inline JSON schema: %s", e)
            sys.exit(1)

    if not isinstance(schema, dict):
        logger.error(
            "Schema must be a JSON object, got %s",
            type(schema).__name__
        )
        sys.exit(1)

    for key, val in schema.items():
        if not isinstance(val, str):
            logger.error(
                "Schema entries must be str -> str;"
                "got key=%r (%s), val=%r (%s)",
                key, type(key).__name__, val, type(val).__name__
            )
            sys.exit(1)

    logger.info("Schema has %d fields", len(schema))
    return schema


@dataclass
class SchemaField:
    """
    Represents a single parsed field in the schema.

    Attributes:
        type:   logical data type for validators / serializers
        mode:   how to generate the value (one of the “modes” below)
        args:   extra parameters,
                for rand_range → [min, max], for choice → list[Any], else []
        const:  only used if mode == "constant" -> the literal value
    """
    type:   Literal["timestamp", "str", "int"]
    mode:   Literal[
        "timestamp", "empty", "rand_uuid",
        "rand_int", "rand_range", "choice", "constant"
    ]
    args: list[Any]
    const: Any = None


def _parse_timestamp(field_name: str, right: str) -> SchemaField:
    """
    Parses a timestamp field. The `right` part is ignored (but warned about).

    Returns:
         a SchemaField with mode "timestamp".
    """
    if right:
        logger.warning("Field %s: timestamp ignores %#r", field_name, right)
    return SchemaField(type="timestamp", mode="timestamp", args=[])


def _parse_str(field_name: str, right: str) -> SchemaField:
    """
    Parses a string field specification.

    Supports:
        - "" → empty string
        - "rand" → UUID
        - '["a", "b"]' → choice list
        - any other → treated as a constant

    Returns:
        SchemaField: Parsed schema field.

    Raises:
        SystemExit: If choice list is not valid JSON or contains non-strings.
    """
    if right.startswith("rand("):
        logger.error(
            "Field %s: rand(range) not supported for str type", field_name
        )
        sys.exit(1)

    if right == "":
        return SchemaField("str", "empty", [], const="")

    if right == "rand":
        return SchemaField("str", "rand_uuid", [])

    if right.startswith("["):
        try:
            items = json.loads(right)
        except json.JSONDecodeError as e:
            logger.error(
                "Field %s: invalid choice list %r —"
                "please supply a JSON array of strings, e.g. [\"a\",\"b\"]."
                "Error: %s",
                field_name, right, e.msg
            )
            sys.exit(1)
        if not all(isinstance(x, str) for x in items):
            logger.error(
                "Field %s: choice list must be all strings", field_name
            )
            sys.exit(1)
        return SchemaField("str", "choice", items)

    # anything else -> constant
    return SchemaField("str", "constant", [], const=right)


def _parse_int(field_name: str, right: str) -> SchemaField:
    """
    Parses an integer field specification.

    Supports:
        - "" → empty (None)
        - "rand" → random int
        - "rand(min,max)" → random int in range
        - '[1, 2, 3]' → choice list
        - numeric string → constant int

    Returns:
        SchemaField: Parsed schema field.

    Raises:
        SystemExit: On invalid syntax, malformed JSON, or non-integer values.
    """
    if right == "":
        return SchemaField("int", "empty", [], const=None)

    if right == "rand":
        return SchemaField("int", "rand_int", [], None)

    pattern = re.compile(r"""
        rand\(              # literal 'rand('
        \s*                 # optional whitespace
        (\d+)               # first group: one or more digits (min value)
        \s*,\s*             # comma, optionally surrounded by whitespace
        (\d+)               # second group: one or more digits (max value)
        \s*                 # optional whitespace
        \)                  # literal closing parenthesis ')'
    """, re.VERBOSE)
    # Attempt to match against the input string `right`
    if match := pattern.fullmatch(right):
        min_val, max_val = map(int, match.groups())
        return SchemaField("int", "rand_range", [min_val, max_val])

    if right.startswith("["):
        try:
            items = json.loads(right)
        except json.JSONDecodeError as e:
            logger.error("Field %s: bad JSON list %s", field_name, e)
            sys.exit(1)
        if not all(isinstance(x, int) for x in items):
            logger.error("Field %s: list must contain ints", field_name)
            sys.exit(1)
        return SchemaField("int", "choice", items)

    # literal int
    try:
        val = int(right)
    except ValueError:
        logger.error("Field %s: cannot convert %r to int", field_name, right)
        sys.exit(1)
    return SchemaField("int", "constant", [], const=val)


def parse_field_spec(field_name: str, raw: str) -> SchemaField:
    """
    Parses a raw field specification.

    Parameters:
        field_name (str): Name of the field for error reporting.
        raw (str): Spec in the format "type:what_to_generate".

    Returns:
        SchemaField: Parsed and validated schema field.

    Raises:
        SystemExit: If format is invalid or type is unsupported.
    """
    if ':' not in raw:
        logger.error("Field %s spec missing ':' -> %r", field_name, raw)
        sys.exit(1)
    left, right = raw.split(":", 1)
    left = left.strip()
    right = right.strip()

    if left not in {"timestamp", "str", "int"}:
        logger.error(
            "Field %s: unknown type %r (allowed: timestamp, str, int)",
            field_name, left)
        sys.exit(1)

    if left == "timestamp":
        return _parse_timestamp(field_name, right)
    if left == "str":
        return _parse_str(field_name, right)
    # left == "int":
    return _parse_int(field_name, right)


def build_schema_model(raw_schema: Dict[str, str]) -> Dict[str, SchemaField]:
    """
    Transforms a raw schema dictionary into a validated schema model.

    Parameters:
        raw_schema (Dict[str, str]): Field-to-spec mapping from input schema.

    Returns:
        Dict[str, SchemaField]: Field-to-SchemaField mapping for generation.
    """
    model = {}
    for field, spec in raw_schema.items():
        model[field] = parse_field_spec(field, spec)
    return model
