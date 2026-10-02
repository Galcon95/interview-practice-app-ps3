# Tests for client/app_config.py (reading developer_mode from config.ini).
# They use temporary INI files, so the real config.ini is never changed.
# Run from the project root: py -3.13 -m pytest

import pytest

from app_config import is_developer_mode


def write_config(tmp_path, text):
    """Write an INI file into pytest's temporary folder.

    Args:
        tmp_path: pytest's temporary folder for this test.
        text: the content of the file.

    Returns:
        The path of the file.
    """
    path = tmp_path / "config.ini"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("value", ["on", "ON", "true", "yes", "1"])
def test_developer_mode_on(tmp_path, value):
    """on, true, yes and 1 (in any case) switch developer mode on.

    Args:
        value: the value written after "developer_mode =".
    """
    assert is_developer_mode(write_config(tmp_path, f"[app]\ndeveloper_mode = {value}\n"))


@pytest.mark.parametrize("value", ["off", "false", "no", "0"])
def test_developer_mode_off(tmp_path, value):
    """off, false, no and 0 switch developer mode off.

    Args:
        value: the value written after "developer_mode =".
    """
    assert not is_developer_mode(write_config(tmp_path, f"[app]\ndeveloper_mode = {value}\n"))


@pytest.mark.parametrize("text", [
    "",                                  # empty file
    "[other]\ndeveloper_mode = on\n",    # wrong section
    "[app]\n",                           # line missing
    "[app]\ndeveloper_mode = maybe\n",   # unclear value
])
def test_anything_unclear_counts_as_off(tmp_path, text):
    """An empty file, a wrong section, a missing line or an unclear value all mean off.

    Args:
        text: the content of the INI file.
    """
    assert not is_developer_mode(write_config(tmp_path, text))


def test_missing_file_counts_as_off(tmp_path):
    """Without a config.ini, developer mode is off."""
    assert not is_developer_mode(tmp_path / "does_not_exist.ini")

