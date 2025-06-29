import time
import uuid
import random
import json
from pathlib import Path
from typing import Any, Dict
from magicgenerator.parser import SchemaField
from magicgenerator.logger import get_logger

logger = get_logger(__name__)


class DataGenerator:
    """Given a parsed schema model, produce records & files."""

    # Map of generation modes → handler functions
    # Each mode must match a SchemaField.mode from parser
    _GEN_MAP = {
        "timestamp": lambda field: str(time.time()),
        "empty": lambda field: field.const, # we set const="" or const=None in parser
        "rand_uuid": lambda field: str(uuid.uuid4()),
        "rand_int": lambda field: random.randint(0, 10000),
        "rand_range": lambda field: random.randint(*field.args),
        "choice": lambda field: random.choice(field.args),
        "constant": lambda field: field.const
    }

    def __init__(self, schema_model: Dict[str,SchemaField]):
        self.schema = schema_model


    def generate_record(self) -> Dict[str, Any]:
        """
        Given a dict of field_name -> SchemaField, produce one dict of
        field_name → generated value.

        Returns:
            Dict[str, Any]: Record with generated values per field.
        """
        record = {}
        for name, field in self.schema.items():
            fn = self._GEN_MAP[field.mode]
            record[name] = fn(field)
        return record


    def write_jsonl_file(
            self,
            output_path: Path,
            data_lines: int
    ) -> None:
        """
        Write `data_lines` JSON‐Lines to `output_path`.

        Parameters:
            output_path (Path): Where to write the file.
            data_lines (int): Number of lines (records) to write.
        """
        logger.info("Generating %d lines → %s", data_lines, output_path)
        with output_path.open("w", encoding="utf-8") as f:
            for i in range(data_lines):
                rec = self.generate_record()
                f.write(json.dumps(rec))
                f.write("\n")
