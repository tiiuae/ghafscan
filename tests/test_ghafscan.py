#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022-2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=global-statement, redefined-outer-name

""" Tests for ghafscan """

import os
import subprocess
import shutil
from pathlib import Path
import pytest

from ghafscan.main import FlakeScanner

################################################################################

MYDIR = Path(os.path.dirname(os.path.realpath(__file__)))
TEST_WORK_DIR = None
REPOROOT = MYDIR / ".."
GHAFSCAN = REPOROOT / "src" / "ghafscan" / "main.py"

################################################################################


@pytest.fixture(scope="session")
def test_work_dir(tmp_path_factory):
    """Fixture for session-scope tempdir"""
    tempdir = tmp_path_factory.mktemp("test_ghafscan")
    return Path(tempdir)


@pytest.fixture(autouse=True)
def set_up_test_data(test_work_dir):
    """Fixture to set up the test data"""
    print("setup")
    global TEST_WORK_DIR
    TEST_WORK_DIR = test_work_dir
    TEST_WORK_DIR.mkdir(parents=True, exist_ok=True)
    print(f"using TEST_WORK_DIR: {TEST_WORK_DIR}")
    os.chdir(TEST_WORK_DIR)
    yield "resource"
    print("clean up")
    shutil.rmtree(TEST_WORK_DIR)


################################################################################


def test_ghafscan_help():
    """Test ghafscan command line argument: '-h'"""
    cmd = [GHAFSCAN, "-h"]
    assert subprocess.run(cmd, check=True).returncode == 0


def test_ghafscan_basic():
    """Basic tests for GhafScanner"""
    scanner = FlakeScanner("github:tiiuae/ghaf?ref=main")
    scanner.scan_target("formatter.x86_64-linux", buildtime=False)
    test_work_dir = Path(TEST_WORK_DIR)
    scanner.report(test_work_dir)
    readme = test_work_dir / "README.md"
    assert readme.exists()
    assert readme.stat().st_size != 0


################################################################################


if __name__ == "__main__":
    pytest.main([__file__])


################################################################################
