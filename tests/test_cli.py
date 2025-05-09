import pytest
import logging
from magicgenerator.config import read_defaults
from magicgenerator.cli import build_parser
from tests.conftest import get_test_logger


@pytest.fixture
def cli_parser(caplog):
    """
    Fixture that returns an ArgumentParser configured with defaults.
    Hooks logging from magicgenerator.cli to pytest caplog at ERROR level.
    """
    defaults = read_defaults()
    parser = build_parser(defaults)
    get_test_logger("magicgenerator.cli", caplog, logging.ERROR)
    return parser


def test_invalid_int_arg(cli_parser, caplog):
    """
    Invalid int should exit with code 1 and log error.
    """
    with pytest.raises(SystemExit) as exc:
        cli_parser.parse_args(["--files_count", "not_an_int"])
    assert exc.value.code == 1
    assert "invalid int value" in caplog.text


def test_invalid_choice_arg(cli_parser, caplog):
    """
    Invalid choice should exit with code 1 and log error.
    """
    with pytest.raises(SystemExit) as exc:
        cli_parser.parse_args(["--file_prefix", "wrong"])
    assert exc.value.code == 1
    assert "invalid choice" in caplog.text


def test_help_exits_zero(cli_parser, capsys):
    """
    --help should exit 0 and print usage.
    """
    with pytest.raises(SystemExit) as exc:
        cli_parser.parse_args(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "usage:" in captured.out
    assert "magicgenerator" in captured.out
