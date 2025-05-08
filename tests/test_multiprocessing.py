import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "main.py"
SCHEMA = json.dumps({"x": "int:rand(1,3)", "y": "str:[\"a\",\"b\"]"})


def test_multiprocess_creates_correct_number(tmp_path):
    cmd = [
        sys.executable, str(SCRIPT), str(tmp_path),
        "--files_count", "4",
        "--multiprocessing", "2",
        "--data_schema", SCHEMA,
        "--file_name", "testfile",
        "--data_lines", "2"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Stderr:\n{result.stderr}"

    files = list(tmp_path.iterdir())
    assert len(files) == 4

    for f in files:
        assert f.suffix == ".jsonl"
        lines = f.read_text().strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            d = json.loads(line)
            assert set(d.keys()) == {"x", "y"}


def test_stdout_mode(tmp_path):
    data_lines = 7
    cmd = [
        sys.executable, str(SCRIPT), str(tmp_path),
        "--files_count", "0",
        "--data_schema", SCHEMA,
        "--data_lines", str(data_lines)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Stderr:\n{result.stderr}"

    lines = result.stdout.strip().splitlines()
    assert len(lines) == data_lines, (
        f"Expected {data_lines} lines, got {len(lines)}:\n{lines}"
    )

    for line in lines:
        d = json.loads(line)
        assert set(d.keys()) == {"x", "y"}
