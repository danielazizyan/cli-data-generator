import json
import pytest
from magicgenerator.parser import build_schema_model
from magicgenerator.generator import generate_record, write_jsonl_file


@pytest.fixture
def simple_schema_model():
    raw = {
        "a": "int: rand(0,2)",
        "b": "str: [\"x\", \"y\"]",
        "c": "timestamp:"
    }
    return build_schema_model(raw)


def test_generate_record_types(simple_schema_model):
    rec = generate_record(simple_schema_model)
    assert set(rec.keys()) == set(simple_schema_model.keys())
    assert isinstance(rec["a"], int)
    assert rec["a"] in {0, 1, 2}
    assert rec["b"] in {"x", "y"}
    assert isinstance(rec["c"], str)
    float(rec["c"])


def test_write_jsonl_file_creates_and_content(tmp_path, simple_schema_model):
    out = tmp_path / "out.jsonl"
    write_jsonl_file(out, simple_schema_model, data_lines=5)
    assert out.exists()
    text = out.read_text().strip().splitlines()
    assert len(text) == 5

    for line in text:
        dt = json.loads(line)
        assert set(dt.keys()) == set(simple_schema_model.keys())
        assert isinstance(dt["a"], int)
        assert dt["a"] in {0, 1, 2}
        assert dt["b"] in {"x", "y"}
        assert isinstance(dt["c"], str)
        float(dt["c"])
