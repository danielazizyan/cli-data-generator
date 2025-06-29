import json
import pytest
from magicgenerator.parser import SchemaParser
from magicgenerator.generator import DataGenerator


@pytest.fixture
def simple_schema_model():
    """
    Small schema with int, str, and timestamp fields.
    """
    raw = {
        "a": "int: rand(0,2)",
        "b": "str: [\"x\", \"y\"]",
        "c": "timestamp:"
    }
    return SchemaParser.build_schema_model(raw)


def test_generate_record_types(simple_schema_model):
    """
    Record has correct field types and values.
    """
    gen = DataGenerator(simple_schema_model)
    rec = gen.generate_record()
    assert set(rec.keys()) == set(simple_schema_model.keys())
    assert isinstance(rec["a"], int)
    assert rec["a"] in {0, 1, 2}
    assert rec["b"] in {"x", "y"}
    assert isinstance(rec["c"], str)
    float(rec["c"])


def test_write_jsonl_file_creates_and_content(tmp_path, simple_schema_model):
    """
    .jsonl file is created with correct records.
    """
    out = tmp_path / "out.jsonl"
    gen = DataGenerator(simple_schema_model)
    gen.write_jsonl_file(out, data_lines=5)
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
