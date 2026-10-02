# Reads the app settings from config.ini in the project root (see that file).
# Only the front end uses these settings: they decide which pages are shown.

import configparser
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config.ini"


def is_developer_mode(config_file=CONFIG_FILE):
    """Check whether developer mode is switched on in config.ini.

    The file is read on every call, so a change takes effect at the next page
    reload. Anything unclear counts as off: a missing file, a missing [app]
    section or developer_mode line, or a value that is not on/off.

    Args:
        config_file: the path of the INI file; only the tests pass another one.

    Returns:
        True if [app] developer_mode is on (also accepted: true, yes, 1),
        otherwise False.
    """
    config = configparser.ConfigParser()
    config.read(config_file, encoding="utf-8")  # a missing file is simply skipped
    try:
        return config.getboolean("app", "developer_mode", fallback=False)
    except ValueError:
        return False  # e.g. "developer_mode = maybe"
