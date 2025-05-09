import pytest
from magicgenerator.parser import build_schema_model, SchemaField


def test_build_model_single_field():
    """
    One valid field builds correct SchemaField.
    """
    raw = {"a": "str:rand"}
    model = build_schema_model(raw)
    assert set(model.keys()) == {"a"}
    sf = model["a"]
    assert sf == SchemaField(type="str", mode="rand_uuid", args=[], const=None)


def test_build_model_multiple_fields():
    """
    Multiple fields build expected SchemaField objects.
    """
    raw = {
        "id": "int:rand(10, 20)",
        "name": "str:[\"x\",\"y\"]",
        "ts": "timestamp:"
    }
    model = build_schema_model(raw)
    assert set(model.keys()) == {"id", "name", "ts"}
    sf_id = model["id"]
    sf_name = model["name"]
    sf_ts = model["ts"]
    assert sf_id == SchemaField(
        type="int", mode="rand_range", args=[10, 20], const=None
    )
    assert sf_name == SchemaField(
        type="str", mode="choice", args=["x", "y"], const=None
    )
    assert sf_ts == SchemaField(
        type="timestamp", mode="timestamp", args=[], const=None
    )


def test_build_model_invalid_spec():
    """
    Invalid specs raise SystemExit.
    """
    with pytest.raises(SystemExit):
        build_schema_model({"a": "foo:bar"})
    with pytest.raises(SystemExit):
        build_schema_model({"a": "int:rand(a,b)"})
    with pytest.raises(SystemExit):
        build_schema_model({"a": "str:[1,2]"})
