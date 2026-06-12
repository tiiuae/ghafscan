#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022-2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=global-statement, redefined-outer-name

"""Tests for ghafscan"""

import os
import subprocess
import shutil
from pathlib import Path
import pytest

from ghafscan import main as ghafscan_main
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
    scanner = FlakeScanner(REPOROOT)
    scanner.scan_target("packages.x86_64-linux.default", buildtime=False)
    test_work_dir = Path(TEST_WORK_DIR)
    scanner.report(test_work_dir)
    readme = test_work_dir / "README.md"
    assert readme.exists()
    assert readme.stat().st_size != 0


def test_evaluate_target_drv_reports_stderr(monkeypatch):
    """Evaluation failures should preserve stderr in the report error"""
    scanner = FlakeScanner.__new__(FlakeScanner)
    scanner.tmpdir = None
    scanner.repodir = Path("/tmp/fake-repo")
    scanner.errors = {}

    def _fake_exec_cmd(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=_args[0],
            returncode=1,
            stdout="",
            stderr="line 1\nline 2\nerror: bzip2_1_1 has been removed\n",
        )

    monkeypatch.setattr(ghafscan_main, "exec_cmd", _fake_exec_cmd)

    # pylint: disable=protected-access
    # Exercise the report formatting on evaluation failure.
    drv = scanner._evaluate_target_drv(
        "packages.aarch64-linux.nvidia-jetson-orin-nx-debug",
        "lock_updated",
    )

    assert drv is None
    error_key = "packages.aarch64-linux.nvidia-jetson-orin-nx-debug_lock_updated"
    err = scanner.errors[error_key]
    assert (
        "Error evaluating 'packages.aarch64-linux.nvidia-jetson-orin-nx-debug' "
        "on lock_updated" in err
    )
    assert "error: bzip2_1_1 has been removed" in err
    assert "https://github.com/tiiuae/ghafscan/actions" in err


################################################################################


if __name__ == "__main__":
    pytest.main([__file__])


################################################################################
