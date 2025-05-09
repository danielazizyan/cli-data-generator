import logging
import os
import pytest
from magicgenerator.utils import (
    validate_output_path,
    validate_min,
    cap_multiprocessing,
    clear_old_files,
)
from tests.conftest import get_test_logger


def test_validate_output_path_creates_dir(tmp_path):
    """
    Creates new output directory if it doesn't exist.
    """
    new_dir = tmp_path / "newdir"
    assert not new_dir.exists()
    result = validate_output_path(str(new_dir))
    assert new_dir.exists() and new_dir.is_dir()
    assert result == new_dir


def test_validate_output_path_bad_file(tmp_path):
    """
    Exits if path exists but is a file.
    """
    bad_file = tmp_path / "afile"
    bad_file.write_text("hello")
    with pytest.raises(SystemExit):
        validate_output_path(str(bad_file))


def test_validate_min_too_small(caplog):
    """
    Exits if value is below the minimum.
    """
    get_test_logger("magicgenerator.utils", caplog, logging.ERROR)
    with pytest.raises(SystemExit):
        validate_min("test", -1, 0)
    assert "must be >= 0" in caplog.text


def test_cap_multiprocessing_no_cap(monkeypatch):
    """
    Returns requested value if <= CPU count.
    """
    monkeypatch.setattr(os, "cpu_count", lambda: 4)
    assert cap_multiprocessing(2) == 2


def test_cap_multiprocessing_caps_and_warns(caplog, monkeypatch):
    """
    Caps value if above CPU count and logs a warning.
    """
    monkeypatch.setattr(os, "cpu_count", lambda: 2)
    get_test_logger("magicgenerator.utils", caplog, logging.WARNING)
    assert cap_multiprocessing(5) == 2
    assert "exceeds CPU count" in caplog.text


def test_clear_old_files(tmp_path, caplog):
    """
    Deletes files matching prefix and logs results.
    """
    (tmp_path / "data_1.jsonl").write_text("x")
    (tmp_path / "data_2.jsonl").write_text("x")
    (tmp_path / "other.txt").write_text("x")

    get_test_logger("magicgenerator.utils", caplog, logging.INFO)
    clear_old_files(tmp_path, "data")

    remaining = [p.name for p in tmp_path.iterdir()]
    assert "other.txt" in remaining
    for name in remaining:
        assert not name.startswith("data")
    assert "Deleted old file" in caplog.text
