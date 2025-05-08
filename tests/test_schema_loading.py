import json
import pytest
from magicgenerator.parser import load_schema


def test_load_schema_inline_valid():
    inline = '{"foo":"str:rand", "bar":"int:rand(1,5)"}'
    schema = load_schema(inline)
    assert isinstance(schema, dict)
    assert set(schema.keys()) == {"foo", "bar"}
    assert schema["foo"] == "str:rand"
    assert schema["bar"] == "int:rand(1,5)"


def test_load_schema_from_file(tmp_path):
    data = {"x": "str:hello", "y": "int:42"}
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(data))
    schema = load_schema(str(p))
    assert schema == data


def test_load_schema_invalid_json():
    with pytest.raises(SystemExit):
        load_schema("not a valid { json")


def test_load_schema_not_object(tmp_path):
    p = tmp_path / "list.json"
    p.write_text(json.dumps([1, 2, 3]))
    with pytest.raises(SystemExit):
        load_schema(str(p))


def test_load_schema_nonstring_value(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"a": 2}))
    with pytest.raises(SystemExit):
        load_schema(str(bad))
