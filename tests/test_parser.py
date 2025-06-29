import pytest
from tests.conftest import get_test_logger
from magicgenerator.parser import SchemaParser, SchemaField


@pytest.mark.parametrize("raw,expected", [
    ("str:",
     SchemaField(type="str", mode="empty", args=[], const="")
     ),
    ("str:rand",
     SchemaField(type="str", mode="rand_uuid", args=[], const=None)
     ),
    ("str:[\"a\",\"b\"]",
     SchemaField(type="str", mode="choice", args=["a", "b"], const=None)
     ),
    ("str:hello",
     SchemaField(type="str", mode="constant", args=[], const="hello"))
])
def test_parser_str_modes(raw, expected):
    """
    str field specs are parsed into correct SchemaField objects.
    """
    sf = SchemaParser.parse_field_spec("field_name", raw)
    assert sf == expected


@pytest.mark.parametrize("raw, expected", [
    ("int:",
     SchemaField(type="int", mode="empty", args=[], const=None)
     ),
    ("int:rand",
     SchemaField(type="int", mode="rand_int", args=[], const=None)
     ),
    ("int:rand(1,5)",
     SchemaField(type="int", mode="rand_range", args=[1, 5], const=None)
     ),
    ("int:[1, 2, 3]",
     SchemaField(type="int", mode="choice", args=[1, 2, 3], const=None)
     ),
    ("int:42",
     SchemaField(type="int", mode="constant", args=[], const=42)
     )
])
def test_parse_int_modes(raw, expected):
    """
    int field specs are parsed into correct SchemaField objects.
    """
    sf = SchemaParser.parse_field_spec("field_name", raw)
    assert sf == expected


def test_parse_timestamp_ignores_extra(caplog):
    """
    Extra data after 'timestamp:' is ignored with a warning.
    """
    get_test_logger("magicgenerator.parser", caplog)
    sf = SchemaParser.parse_field_spec("field_name", "timestamp:foo")
    assert sf == SchemaField(
        type="timestamp", mode="timestamp", args=[], const=None
    )
    assert "timestamp ignores" in caplog.text


@pytest.mark.parametrize("raw", [
    "foo:bar",
    "str:rand(1,2)",
    "int:hello",
    "int:rand(a,b)"
])
def test_parse_errors(raw):
    """
    Invalid field specs raise SystemExit.
    """
    with pytest.raises(SystemExit):
        SchemaParser.parse_field_spec("field_name", raw)
