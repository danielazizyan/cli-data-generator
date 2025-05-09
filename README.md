# MagicGenerator

**MagicGenerator** is a console utility that generates structured JSON test data
based on a flexible schema definition.

---

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/gridu/Python-Basic--Daniel-Azizyan.git
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Python 3.9+ is recommended

---

## Project Structure

```
├── main.py          # Entry point
magicgenerator/
├── logger.py        # Unified logger setup
├── config.py        # Reads defaults from `default.ini`
├── cli.py           # CLI parser and arg definitions
├── utils.py         # Path validation, file clearing, etc.
├── parser.py        # Schema parsing and validation
├── generator.py     # Core data generation logic
tests/
├── test_*.py        # Unit and integration tests
configs/
├── default.ini      # Default CLI values
```

---

## Schema Format

A schema is a `Dict[str, str]` that defines the type and generation rule
for each field.

---

## CLI Usage

```bash
python main.py [output_path] [--options]
```

### Examples:

```bash
# Generate 1 file with 10 lines using inline schema
python main.py ./output     --files_count 1     --data_lines 10     --file_name sample     --data_schema '{"name":"str:[\"Alice\",\"Bob\"]","age":"int:rand(18,60)"}'

# Print 5 lines to stdout
python main.py ./output     --files_count 0     --data_lines 5     --data_schema '{"ts":"timestamp:"}'
```

---

## Configuration

Defaults are stored in `configs/default.ini` and loaded on startup.
Command-line arguments override config values.

---

## Testing

Run all tests using:

```bash
pytest
```
