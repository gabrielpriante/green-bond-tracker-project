"""
Shared test utilities and fixtures for the green bond tracker test suite.
"""

import re


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape codes from text.

    This is useful for testing CLI output that may contain
    color codes, formatting, or other terminal escape sequences
    that vary across Python/library versions.

    Parameters
    ----------
    text : str
        Text potentially containing ANSI escape codes

    Returns
    -------
    str
        Text with ANSI codes removed
    """
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)
