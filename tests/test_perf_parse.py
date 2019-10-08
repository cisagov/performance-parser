#!/usr/bin/env pytest -vs
"""Tests for perf_parse."""

import logging
import os
import sys
from unittest.mock import patch

import pytest

from perf_parse import perf_parse


log_levels = (
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    pytest.param("critical2", marks=pytest.mark.xfail),
)

# define sources of version strings
TRAVIS_TAG = os.getenv("TRAVIS_TAG")
PROJECT_VERSION = perf_parse.__version__


def test_stdout_version(capsys):
    """Verify that version string sent to stdout agrees with the module version."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            perf_parse.main()
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


@pytest.mark.skipif(
    TRAVIS_TAG in [None, ""], reason="this is not a release (TRAVIS_TAG not set)"
)
def test_release_version():
    """Verify that release tag version agrees with the module version."""
    assert (
        TRAVIS_TAG == f"v{PROJECT_VERSION}"
    ), "TRAVIS_TAG does not match the project version"


@pytest.mark.parametrize("level", log_levels)
def test_log_levels(level):
    """Validate commandline log-level arguments."""
    with patch.object(
        sys,
        "argv",
        ["bogus", f"--log-level={level}", "forms/307.txt", "/tmp/test.csv"],  # nosec
    ):
        with patch.object(logging.root, "handlers", []):
            assert (
                logging.root.hasHandlers() is False
            ), "root logger should not have handlers yet"
            return_code = perf_parse.main()
            assert (
                logging.root.hasHandlers() is True
            ), "root logger should now have a handler"
            assert return_code == 0, "main() should return success (0)"
